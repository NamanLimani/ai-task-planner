import numpy as np
from typing import List, Tuple
from .models import Task, UserProfile, TaskStatus, DailyLog

class SimulationEnvironment:
    def __init__(self, user: UserProfile):
        self.user = user
        self.current_energy = user.daily_energy_cap
        self.current_time = user.start_hour * 60 # Convert to minutes
        
    def reset_day(self):
        self.current_energy = self.user.daily_energy_cap
        self.current_time = self.user.start_hour * 60

    def simulate_task_execution(self, task: Task) -> Tuple[TaskStatus, str]:
        """
        Simulates executing a task. Returns status and a log message.
        Uses probabilistic distributions for realism.
        """
        # 1. Check Fatigue: If energy is low, tasks take longer
        fatigue_factor = 1.0
        if self.current_energy < 30:
            fatigue_factor = 1.5  # 50% slower when tired
            
        # 2. Calculate Actual Duration (Log-Normal Distribution)
        # We assume estimation is imperfect.
        mu = np.log(task.estimated_duration_mins)
        sigma = 0.2 # Variance in how long tasks take
        actual_duration = int(np.random.lognormal(mu, sigma) * self.user.work_speed_multiplier * fatigue_factor)
        
        # 3. Check for Random Interruptions (Poisson process approximation)
        interruption_prob = 0.15
        interruption_duration = 0
        if np.random.random() < interruption_prob:
            interruption_duration = np.random.randint(15, 60)
            
        total_time_cost = actual_duration + interruption_duration
        
        # 4. Validate against Day Constraints
        day_end_mins = self.user.end_hour * 60
        if self.current_time + total_time_cost > day_end_mins:
            return TaskStatus.FAILED, f"Ran out of time. Required {total_time_cost}m, but day ends in {day_end_mins - self.current_time}m."
            
        # 5. Execute
        self.current_time += total_time_cost
        self.current_energy -= (10 * fatigue_factor) # Energy drain
        task.actual_duration_mins = actual_duration
        task.status = TaskStatus.COMPLETED
        
        log_msg = f"Task '{task.description}' done in {actual_duration}m (Est: {task.estimated_duration_mins}m)."
        if interruption_duration > 0:
            log_msg += f" + {interruption_duration}m interruption."
        if fatigue_factor > 1.0:
            log_msg += " (User was tired)."
            
        return TaskStatus.COMPLETED, log_msg