from typing import List
from src.simulation.models import Task, UserProfile
from src.llm_client import LLMClient
from src.critic import PlanCritic
from src.memory import get_past_mistakes

class AgenticPlanner:
    def __init__(self):
        self.llm = LLMClient()
        self.critic = PlanCritic()

    def construct_prompt(self, tasks: List[Task], user: UserProfile, past_failures: str, feedback_context: str = "") -> str:
        """
        Builds the prompt. Now accepts 'past_failures' as an argument so we can turn it off.
        """
        task_list_str = "\n".join(
            [f"- ID: {t.id} | Desc: {t.description} | Est: {t.estimated_duration_mins}m | Priority: {t.priority}" 
             for t in tasks]
        )
        
        base_prompt = f"""
        You are an expert AI Scheduler. Your goal is to order these tasks to maximize completion rate.
        
        ### LEARNING FROM THE PAST (Do not repeat these mistakes)
        {past_failures if past_failures else "No history available (Memory Disabled or Empty)."}
        
        ### USER PROFILE
        - Work Window: {user.start_hour}:00 to {user.end_hour}:00
        - Energy Dynamics: The user starts with 100 energy. Complex tasks drain more energy. 
        - Fatigue Rule: If energy drops below 30, tasks take 50% longer.
        
        ### TASKS TO SCHEDULE
        {task_list_str}
        
        ### INSTRUCTIONS
        1. Sort the tasks in the optimal execution order.
        2. Put high-energy/hard tasks EARLY in the day when energy is high.
        3. Put low-priority/easy tasks LATER.
        
        Output valid JSON following this schema:
        {{
            "rationale": "One sentence explaining your strategy.",
            "ordered_task_ids": ["id_1", "id_2", ...]
        }}
        """
        
        if feedback_context:
            base_prompt += f"\n\n### CRITICAL FEEDBACK (FIX THIS FLAW): {feedback_context}"
            
        return base_prompt

    def plan(self, tasks: List[Task], user: UserProfile, use_reflexion: bool = True, use_memory: bool = True) -> List[Task]:
        """
        Main planning loop with Ablation Toggles.
        """
        # 1. Handle Memory Toggle
        if use_memory:
            past_failures = get_past_mistakes()
        else:
            past_failures = "" # Lobotomized: Agent has no memory

        # 2. Draft
        print("\n[Agent]: Drafting initial plan...")
        prompt = self.construct_prompt(tasks, user, past_failures)
        draft_tasks = self.plan_from_prompt(prompt, tasks)
        
        # 3. Handle Reflexion Toggle
        if not use_reflexion:
            print("[System]: Reflexion (Critic) is DISABLED. Skipping validation.")
            return draft_tasks

        # 4. Critique Loop (Only runs if Reflexion is ON)
        print("[Critic]: Reviewing plan...")
        feedback = self.critic.critique_plan(draft_tasks, user)
        
        if feedback == "APPROVED":
            print(f"[Critic]: Plan looks solid. Approving.")
            return draft_tasks
        else:
            print(f"\n[Critic Detected Flaw]: {feedback}")
            print("[Agent]: Refining plan based on feedback...")
            
            # Refine
            refined_prompt = self.construct_prompt(tasks, user, past_failures, feedback_context=feedback)
            return self.plan_from_prompt(refined_prompt, tasks)

    def replan(self, remaining_tasks: List[Task], user: UserProfile, current_time: int, history_log: List[str]) -> List[Task]:
        """
        Called when the schedule breaks during execution.
        """
        task_list_str = "\n".join(
            [f"- ID: {t.id} | Desc: {t.description} | Est: {t.estimated_duration_mins}m" 
             for t in remaining_tasks]
        )
        hour = int(current_time // 60)
        minute = int(current_time % 60)
        time_str = f"{hour:02d}:{minute:02d}"

        prompt = f"""
        WARNING: The original schedule failed. You must re-plan the REMAINING tasks.
        
        ### CURRENT STATUS
        - Current Time: {time_str} (Day ends at {user.end_hour}:00)
        - Current Energy: {user.daily_energy_cap}
        
        ### EXECUTION HISTORY
        {chr(10).join(history_log[-3:])} 
        
        ### REMAINING TASKS
        {task_list_str}
        
        Output valid JSON:
        {{
            "rationale": "Explanation of how you recovered the schedule.",
            "ordered_task_ids": ["id_remaining_1", ...]
        }}
        """
        return self.plan_from_prompt(prompt, remaining_tasks)

    def plan_from_prompt(self, prompt: str, tasks: List[Task]) -> List[Task]:
        """Helper to handle the LLM call and parsing"""
        response_json = self.llm.generate_plan(prompt)
        try:
            ordered_ids = response_json.get("ordered_task_ids", [])
            rationale = response_json.get("rationale", "No rationale.")
            print(f"[Agent Thought]: {rationale}")
            
            task_map = {t.id: t for t in tasks}
            ordered_tasks = []
            for tid in ordered_ids:
                if tid in task_map:
                    ordered_tasks.append(task_map[tid])
            
            # Append forgotten tasks
            for t in tasks:
                if t not in ordered_tasks:
                    ordered_tasks.append(t)
            return ordered_tasks
        except Exception as e:
            print(f"Parsing Error: {e}")
            return tasks