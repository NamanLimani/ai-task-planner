import pandas as pd
import time
from src.simulation.models import UserProfile, TaskStatus
from src.simulation.env import SimulationEnvironment
from src.agent import AgenticPlanner
from generate_dataset import generate_synthetic_tasks

def run_episode(agent_type="greedy", agent=None):
    """
    Runs a single day. 
    agent_type: 'greedy' (sorts by time) or 'llm' (uses Gemini)
    """
    # 1. Same initial conditions for fair comparison
    user = UserProfile(procrastination_prob=0.4, work_speed_multiplier=1.1)
    env = SimulationEnvironment(user)
    tasks = generate_synthetic_tasks(num_tasks=6)
    
    # Keep a copy of original tasks for the record
    original_count = len(tasks)
    
    # 2. Planning Phase
    if agent_type == "llm":
        try:
            pending_tasks = agent.plan(tasks, user)
        except:
            pending_tasks = tasks # Fallback
    else:
        # Baseline: Greedy Sort (Shortest Job First)
        pending_tasks = sorted(tasks, key=lambda x: x.estimated_duration_mins)

    # 3. Execution Loop
    completed_count = 0
    history_log = []
    
    while pending_tasks:
        # Safety Check: If time is already up, stop immediately
        if env.current_time >= user.end_hour * 60:
            break 
            
        current_task = pending_tasks[0]
        status, msg = env.simulate_task_execution(current_task)
        history_log.append(msg)
        
        if status == TaskStatus.COMPLETED:
            completed_count += 1
            pending_tasks.pop(0)
        elif status == TaskStatus.FAILED:
            # FIX: If a task fails (doesn't fit), we must stop the day
            # otherwise we get an infinite loop trying to do the same task.
            break
            
        # RE-PLANNING (Only for LLM)
        if agent_type == "llm":
            was_delayed = "interruption" in msg or "tired" in msg
            # Only re-plan if the task actually finished (pending_tasks was popped) 
            # and there are still tasks left.
            if was_delayed and pending_tasks and status == TaskStatus.COMPLETED:
                try:
                    pending_tasks = agent.replan(pending_tasks, user, env.current_time, history_log)
                except Exception as e:
                    print(f"Replan failed: {e}")

    return {
        "agent": agent_type,
        "tasks_completed": completed_count,
        "total_tasks": original_count,
        "success_rate": completed_count / original_count,
        "energy_left": env.current_energy
    }

def main():
    print("Starting Evaluation: LLM Agent vs. Greedy Baseline")
    results = []
    agent = AgenticPlanner() # Initialize once
    
    # Run 5 rounds of Greedy
    print("Running Baseline (Greedy)...")
    for i in range(5):
        res = run_episode("greedy")
        results.append(res)
        print(f"  Greedy Episode {i+1}: {res['success_rate']*100:.0f}% success")
        
    # Run 5 rounds of LLM
    print("\nRunning AI Agent (LLM)...")
    for i in range(5):
        print(f"  LLM Episode {i+1}...")
        res = run_episode("llm", agent)
        results.append(res)
        time.sleep(2) # Safety pause for API limits
        
    # Save Results
    df = pd.DataFrame(results)
    print("\n--- Final Results (Average) ---")
    print(df.groupby("agent")[["success_rate", "energy_left"]].mean())
    df.to_csv("data/evaluation_results.csv", index=False)
    print("\nDetailed results saved to 'data/evaluation_results.csv'")

if __name__ == "__main__":
    main()