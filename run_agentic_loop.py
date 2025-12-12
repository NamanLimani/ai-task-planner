import time
from src.simulation.models import UserProfile, TaskStatus
from src.simulation.env import SimulationEnvironment
from src.agent import AgenticPlanner
from src.memory import save_reflection # <--- NEW
from generate_dataset import generate_synthetic_tasks

def main():
    # 1. Setup
    user = UserProfile(procrastination_prob=0.3)
    env = SimulationEnvironment(user)
    agent = AgenticPlanner()
    
    # 2. Initial State
    tasks = generate_synthetic_tasks(num_tasks=6)
    print(f"Goal: Complete {len(tasks)} tasks by {user.end_hour}:00.")
    
    # 3. Initial Plan (This triggers the Draft -> Critic -> Refine loop)
    pending_tasks = agent.plan(tasks, user)
    history_log = []
    
    # 4. The Execution Loop
    while pending_tasks:
        if env.current_time >= user.end_hour * 60:
            print(f"!!! CRITICAL FAIL: Day over. {len(pending_tasks)} tasks left unfinished.")
            break
            
        current_task = pending_tasks[0]
        
        print(f"\n>>> Attempting: {current_task.description}...")
        status, msg = env.simulate_task_execution(current_task)
        history_log.append(msg)
        print(f"    Result: {msg}")
        
        # --- OPTIONAL: FORCE A CRISIS FOR DEMO ---
        # Uncomment this block to force a replay scenario
        # if len(history_log) == 2: 
        #    print("\n!!! INJECTING SIMULATED DISASTER: 2 Hour Emergency Meeting !!!")
        #    env.current_time += 120 
        #    msg += " + (MAJOR UNEXPECTED DELAY)" 
        # ----------------------------------------
        
        if status == TaskStatus.COMPLETED:
            pending_tasks.pop(0)
            
        # 5. TRIGGER RE-PLANNING?
        was_delayed = "interruption" in msg or "tired" in msg or "DELAY" in msg
        if was_delayed and pending_tasks:
            print("\n*** DETECTED DELAY: Triggering Agent Re-Plan ***")
            pending_tasks = agent.replan(
                pending_tasks, 
                user, 
                env.current_time, 
                history_log
            )

    # 6. SAVE MEMORY (The Learning Step)
    print("\n--- Day Summary ---")
    print(f"Time: {int(env.current_time/60)}:{int(env.current_time%60):02d}")
    
    if env.current_energy < 20:
        lesson = "Burnout Warning: Ended day with very low energy. Schedule fewer hard tasks next time."
    elif len(pending_tasks) > 0:
        lesson = f"Failure: Missed {len(pending_tasks)} tasks. Do not over-commit on deadlines."
    else:
        lesson = "Success: Plan worked well."
        
    save_reflection(lesson)
    print(f"[Memory Saved]: {lesson}")

if __name__ == "__main__":
    main()