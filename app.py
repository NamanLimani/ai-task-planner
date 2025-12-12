import streamlit as st
import time
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from ics import Calendar, Event
from src.simulation.models import UserProfile, TaskStatus
from src.simulation.env import SimulationEnvironment
from src.agent import AgenticPlanner
from src.memory import save_reflection
from generate_dataset import generate_synthetic_tasks

# --- HELPER: EXPORT TO CALENDAR ---
def create_ics_file(tasks, start_hour):
    c = Calendar()
    current_time = datetime.now().replace(hour=start_hour, minute=0, second=0, microsecond=0)
    for task in tasks:
        e = Event()
        e.name = f"🤖 {task.description}"
        e.begin = current_time
        e.duration = timedelta(minutes=task.estimated_duration_mins)
        e.description = f"Priority: {task.priority} | ID: {task.id}"
        c.events.add(e)
        current_time += timedelta(minutes=task.estimated_duration_mins)
    return c.serialize()

# --- PAGE CONFIG ---
st.set_page_config(page_title="Agentic Task Planner", page_icon="🧠", layout="wide")

st.title("🧠 Reflexion Agent: Autonomous Task Scheduler")

# --- TABS CONFIGURATION ---
tab1, tab2 = st.tabs(["🚀 Live Simulation", "📊 Research Analytics"])

# =========================================
# TAB 1: LIVE SIMULATION
# =========================================
with tab1:
    st.markdown("Demonstration of **Agentic AI** with **Self-Correction** and **Reflexion**.")
    
    # --- SIDEBAR MOVED HERE FOR CONTEXT ---
    with st.sidebar:
        st.header("⚙️ Simulation Settings")
        procrastination = st.slider("Procrastination (Chaos Level)", 0.0, 1.0, 0.3)
        num_tasks = st.slider("Number of Tasks", 3, 10, 6)
        speed_mult = st.slider("Work Speed Multiplier", 0.5, 2.0, 1.0)
        
        st.divider()
        st.header("🔬 Research Controls (Ablation)")
        use_reflexion = st.toggle("Enable Reflexion (Critic)", value=True)
        use_memory = st.toggle("Enable Long-Term Memory", value=True)
        
        st.divider()
        force_crisis = st.checkbox("🔥 Force 'Emergency Meeting' Crisis", value=True)
        run_btn = st.button("▶️ Start Agent Simulation", type="primary")

    if run_btn:
        # 1. Setup Phase
        user = UserProfile(procrastination_prob=procrastination, work_speed_multiplier=speed_mult)
        env = SimulationEnvironment(user)
        agent = AgenticPlanner()
        
        col1, col2 = st.columns([2, 1])
        with col1:
            status_box = st.status("🤖 Agent is thinking...", expanded=True)
            log_container = st.container()
        with col2:
            st.subheader("📊 Live Metrics")
            energy_bar = st.progress(1.0, text="Energy: 100%")
            time_display = st.empty()
            task_table = st.empty()

        # 2. Planning Phase
        status_box.write("Generating Initial Draft...")
        tasks = generate_synthetic_tasks(num_tasks=num_tasks)
        
        # PASS THE TOGGLES HERE
        pending_tasks = agent.plan(tasks, user, use_reflexion=use_reflexion, use_memory=use_memory)
        
        if use_reflexion:
            status_box.write("✅ Plan Approved by Critic Module")
        else:
            status_box.write("⚠️ Critic Disabled (Base Model Only)")
            
        status_box.update(label="🤖 Simulation Running", state="running")

        # Display Initial Table
        df = pd.DataFrame([vars(t) for t in pending_tasks])
        task_table.dataframe(df[["description", "estimated_duration_mins", "priority"]], hide_index=True)

        # Download Button
        try:
            ics_data = create_ics_file(pending_tasks, user.start_hour)
            st.sidebar.success("📅 Schedule Ready!")
            st.sidebar.download_button("📥 Download .ics Calendar", ics_data, "agent_schedule.ics", "text/calendar")
        except Exception as e:
            st.sidebar.error(f"Calendar export failed: {e}")

        # 3. Execution Loop
        history_log = []
        for i, _ in enumerate(range(len(pending_tasks) + 5)):
            if not pending_tasks: break
            if env.current_time >= user.end_hour * 60:
                st.error("⛔ Day Over! Time Limit Reached.")
                break
                
            current_task = pending_tasks[0]
            with log_container:
                with st.chat_message("user", avatar="👤"):
                    st.write(f"**Working on:** {current_task.description}...")
            
            time.sleep(1) 
            status, msg = env.simulate_task_execution(current_task)
            history_log.append(msg)
            
            if force_crisis and i == 1:
                with log_container:
                    st.toast("🔥 CRISIS EVENT TRIGGERED!", icon="🔥")
                    st.warning("⚠️ INTERRUPT: 2 Hour Emergency Meeting Added!")
                env.current_time += 120
                env.current_energy = max(0, env.current_energy - 30)
                msg += " + (MAJOR UNEXPECTED DELAY)"

            # Metrics Update
            energy_pct = max(0, env.current_energy / 100)
            energy_bar.progress(energy_pct, text=f"Energy: {int(env.current_energy)}%")
            cur_hour = int(env.current_time // 60)
            cur_min = int(env.current_time % 60)
            time_display.metric("Current Time", f"{cur_hour:02d}:{cur_min:02d}")
            
            with log_container:
                if "interruption" in msg or "DELAY" in msg: st.warning(f"Result: {msg}")
                else: st.success(f"Result: {msg}")

            # --- THE CRITICAL FIX IS HERE ---
            if status == TaskStatus.COMPLETED:
                pending_tasks.pop(0)
            elif status == TaskStatus.FAILED:
                st.error(f"⛔ Task '{current_task.description}' failed. Stopping execution.")
                break # Stop the loop so we don't retry forever
            # --------------------------------

            # Re-planning
            was_delayed = "interruption" in msg or "tired" in msg or "DELAY" in msg
            # Only re-plan if we still have tasks pending (and didn't just break)
            if was_delayed and pending_tasks:
                with log_container:
                    with st.chat_message("assistant", avatar="🧠"):
                        st.write("Wait! I detect a delay. Re-calculating schedule...")
                try:
                    pending_tasks = agent.replan(pending_tasks, user, env.current_time, history_log)
                    df_new = pd.DataFrame([vars(t) for t in pending_tasks])
                    if not df_new.empty:
                        task_table.dataframe(df_new[["description", "estimated_duration_mins"]], hide_index=True)
                        st.toast("Schedule Updated!", icon="🔄")
                except Exception as e:
                    st.error(f"Re-planning failed: {e}")

        status_box.update(label="🏁 Simulation Complete", state="complete")
        if env.current_energy < 20: lesson = "Burnout Warning: High fatigue."
        elif len(pending_tasks) > 0: lesson = f"Failure: Missed {len(pending_tasks)} tasks."
        else: lesson = "Success: Perfect Execution."
        
        if use_memory:
            save_reflection(lesson)
            st.balloons()
            st.sidebar.success(f"Memory Saved: {lesson}")
        else:
            st.sidebar.warning("Memory Disabled: Lesson not saved.")

# =========================================
# TAB 2: RESEARCH ANALYTICS
# =========================================
with tab2:
    st.header("📈 Benchmark Results: Agent vs. Baseline")
    st.markdown("This dashboard visualizes the performance of the **LLM Agent** compared to a **Greedy Heuristic** (Shortest-Job-First).")
    
    csv_path = "data/evaluation_results.csv"
    
    if os.path.exists(csv_path):
        # Load Data
        df = pd.read_csv(csv_path)
        
        # Display Raw Stats
        st.markdown("### 1. Summary Statistics")
        summary = df.groupby("agent")[["success_rate", "energy_left", "tasks_completed"]].mean()
        st.dataframe(summary.style.highlight_max(axis=0), use_container_width=True)
        
        # Display Charts
        st.markdown("### 2. Performance Comparison")
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("**Success Rate Distribution**")
            fig1, ax1 = plt.subplots()
            sns.barplot(data=df, x="agent", y="success_rate", hue="agent", palette="viridis", ax=ax1)
            ax1.set_ylim(0, 1.1)
            st.pyplot(fig1)
            st.caption("Higher is better. Measures % of tasks completed by deadline.")
            
        with col_b:
            st.markdown("**Energy Conservation**")
            fig2, ax2 = plt.subplots()
            sns.boxplot(data=df, x="agent", y="energy_left", hue="agent", palette="magma", ax=ax2)
            st.pyplot(fig2)
            st.caption("Higher is better. Measures remaining user energy (avoiding burnout).")
            
        st.info("💡 **Analysis:** The Agentic Planner typically preserves more energy by dropping low-priority tasks, whereas the Greedy baseline burns out the user by attempting everything.")
        
    else:
        st.warning("⚠️ No evaluation data found. Please run `python evaluate_models.py` first to generate the benchmarks!")