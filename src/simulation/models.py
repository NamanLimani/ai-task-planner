from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    DELAYED = "delayed"

class Task(BaseModel):
    id: str
    description: str
    estimated_duration_mins: int
    deadline_day: int  # e.g., Day 1, Day 2
    priority: int = 1  # 1 (High) to 5 (Low)
    dependencies: List[str] = Field(default_factory=list)
    
    # State tracking
    status: TaskStatus = TaskStatus.PENDING
    actual_duration_mins: Optional[int] = None

class UserProfile(BaseModel):
    """Defines the 'personality' of the simulated user."""
    daily_energy_cap: int = 100  # Abstract energy units (0-100)
    focus_decay_rate: float = 0.1 # How fast they get tired
    procrastination_prob: float = 0.2 # Probability of starting late
    work_speed_multiplier: float = 1.0 # <1.0 means faster, >1.0 means slower
    
    # Working hours (24h format)
    start_hour: int = 9
    end_hour: int = 17

class DailyLog(BaseModel):
    day: int
    energy_start: int
    energy_end: int
    tasks_attempted: List[str]
    tasks_completed: List[str]
    unexpected_events: List[str]