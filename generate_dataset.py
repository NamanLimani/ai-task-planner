import pandas as pd
import random
import uuid
from tqdm import tqdm
from src.simulation.models import Task, UserProfile, TaskStatus
from src.simulation.env import SimulationEnvironment

def generate_synthetic_tasks(num_tasks=5) -> list[Task]:
    """Generates a random list of tasks with loose dependencies."""
    tasks = []
    # Mix of academic and personal tasks
    verbs = ["Read", "Write", "Code", "Review", "Email", "Debug"]
    nouns = ["Paper", "Report", "Module", "Notes", "Professor", "Script"]
    
    for i in range(num_tasks):
        t_id = str(uuid.uuid4())[:8]
        desc = f"{random.choice(verbs)} {random.choice(nouns)} {i+1}"
        est = random.choice([30, 45, 60, 90, 120])
        
        tasks.append(Task(
            id=t_id,
            description=desc,
            estimated_duration_mins=est,
            deadline_day=1
        ))
    return tasks

def run_batch(num_episodes=100000):
    """Runs the baseline (Greedy Scheduler) simulation."""
    data_records = []

    print(f"Generating {num_episodes} episodes...")
    for _ in tqdm(range(num_episodes)):
        # 1. Setup Episode
        user = UserProfile(work_speed_multiplier=random.uniform(0.8, 1.2)) # Randomize user type
        env = SimulationEnvironment(user)
        tasks = generate_synthetic_tasks(num_tasks=random.randint(4, 8))
        
        # 2. Simple Heuristic Planning (Baseline): Sort by Shortest Job First
        # NOTE: Later, your LLM will replace this sorting logic.
        tasks.sort(key=lambda x: x.estimated_duration_mins)
        
        # 3. Run Execution Loop
        episode_log = []
        failures = 0
        
        for task in tasks:
            status, msg = env.simulate_task_execution(task)
            episode_log.append(msg)
            if status == TaskStatus.FAILED:
                failures += 1
                
        # 4. Save Data
        data_records.append({
            "user_speed": user.work_speed_multiplier,
            "total_tasks": len(tasks),
            "failed_tasks": failures,
            "success_rate": 1.0 - (failures/len(tasks)),
            "log_trace": " | ".join(episode_log)
        })

    # Save to CSV
    df = pd.DataFrame(data_records)
    df.to_csv("data/simulation_v1.csv", index=False)
    print("Dataset saved to data/simulation_v1.csv")
    print("\n--- Sample Trace ---")
    print(df.iloc[0]["log_trace"])

if __name__ == "__main__":
    run_batch()