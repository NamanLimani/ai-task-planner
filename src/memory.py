import json
import os

MEMORY_FILE = "data/agent_memory.json"

def save_reflection(day_summary_log: str):
    """
    Saves a lesson to the memory file.
    """
    # Create data dir if it doesn't exist
    os.makedirs("data", exist_ok=True)

    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
    else:
        data = []
        
    data.append(day_summary_log)
    
    # Keep only the last 5 lessons to avoid context overflow
    with open(MEMORY_FILE, 'w') as f:
        json.dump(data[-5:], f, indent=2)

def get_past_mistakes() -> str:
    """Returns a string of past failures to warn the agent."""
    if not os.path.exists(MEMORY_FILE):
        return "No past history."
        
    try:
        with open(MEMORY_FILE, 'r') as f:
            data = json.load(f)
        if not data:
            return "No past history."
        return "\n".join([f"- {item}" for item in data])
    except:
        return "No past history."