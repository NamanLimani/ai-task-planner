import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re
from typing import Dict, Any

# Load environment variables
load_dotenv()

class LLMClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash") # Fallback if env is missing
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        
        print(f"Connecting to LLM Model: {model_name}")
        genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={"response_mime_type": "application/json"}
        )

    def _clean_json_string(self, text: str) -> str:
        """
        Robust cleaning: Removes markdown code blocks (```json ... ```) 
        if the model decides to add them despite our JSON instruction.
        """
        # Remove starting ```json or ```
        text = re.sub(r"^```json\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"^```\s*", "", text, flags=re.MULTILINE)
        # Remove ending ```
        text = re.sub(r"```\s*$", "", text, flags=re.MULTILINE)
        return text.strip()

    def generate_plan(self, prompt: str) -> Dict[str, Any]:
        """
        Sends context to LLM, cleans response, and parses JSON.
        """
        try:
            response = self.model.generate_content(prompt)
            
            # Check if response was blocked (safety filters)
            if not response.parts:
                print("Error: LLM returned empty response (possibly safety blocked).")
                return {}

            raw_text = response.text
            clean_text = self._clean_json_string(raw_text)
            
            return json.loads(clean_text)
            
        except json.JSONDecodeError as e:
            print(f"JSON Parsing Failed. Raw output:\n{raw_text}")
            return {"error": "Invalid JSON format", "schedule": []}
        except Exception as e:
            print(f"LLM API Error: {e}")
            return {"error": str(e), "schedule": []}