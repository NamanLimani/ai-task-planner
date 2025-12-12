from typing import List
from src.llm_client import LLMClient
from src.simulation.models import UserProfile, Task

class PlanCritic:
    def __init__(self):
        self.llm = LLMClient()

    def critique_plan(self, tasks_ordered: List[Task], user: UserProfile) -> str:
        """
        Looks for logical flaws in the plan effectively acting as an adversarial agent.
        """
        plan_summary = "\n".join([
            f"- {t.description} (Est: {t.estimated_duration_mins}m, Priority: {t.priority})"
            for t in tasks_ordered
        ])

        prompt = f"""
        You are a Harsh Critic reviewing a student's daily schedule. 
        
        ### USER CONSTRAINTS
        - Work Hours: {user.start_hour}:00 to {user.end_hour}:00
        - Energy: Starts high, drops fast. Complex tasks after 3 PM are risky.
        
        ### PROPOSED PLAN (In Order)
        {plan_summary}
        
        ### YOUR JOB
        Identify 1 CRITICAL FLAW in this plan.
        - Are hard tasks placed too late?
        - Do the tasks actually fit in the hours available?
        - Is the order illogical?
        
        If the plan is perfect, say "APPROVED".
        If there is a flaw, explain it in 1 sentence starting with "FLAW:".
        
        Output JSON: {{ "feedback": "..." }}
        """
        
        # We reuse the robust LLM client which handles JSON cleaning
        response = self.llm.generate_plan(prompt)
        return response.get("feedback", "APPROVED")