# plan_refiner.py
import json

class PlanRefiner:
    def __init__(self, client):
        self.client = client

    def validate_plan(self, plan: dict) -> list:
        # print("plan",plan,plan.get("plan"))
        steps=plan.get("actions")
        issues = []
        
        for step in steps:
            if(step.get("action")=="write_files"):
                files =step.get("files")
                print(files)
                for file in files:
                    if(not file.get("content","")):
                        issues.append(f"Empty content in {f.get('path', 'unknown')}")
                        
                    
        # if not plan.get("files"):
        #     issues.append("Missing 'files' key.")
        # for f in plan.get("files", []):
        #     if not f.get("content"):
        #         issues.append(f"Empty content in {f.get('path', 'unknown')}")
        # if not plan.get("install"):
        #     issues.append("Missing 'install' commands.")
        # if not plan.get("run"):
        #     issues.append("Missing 'run' commands.")
        return issues

    def refine_plan(self, user_query: str, original_plan_json) -> str:
        """
        Accepts either a JSON string or a Python dict.
        Uses user query + incomplete plan as context to re-prompt the model
        and generate a more complete plan.
        Returns the final corrected JSON string.
        """
        # ✅ Ensure original_plan is always a dict
        
        # print(original_plan.get("plan"))
        # Now plan is a dictionary — safe to proceed
        issues = self.validate_plan(original_plan_json)
        # print(issues)
        # return
        if not issues:
            print("✅ Plan looks complete. No refinement needed.")
            return original_plan_json

        print("🧩 Refining plan. Found issues:", issues)

        refine_prompt = f"""
    The following project setup plan is incomplete.

    User originally asked:
    "{user_query}"

    The plan generated so far:
    {json.dumps(original_plan_json, indent=2)}

    Issues detected:
    {issues}

    Your task:
    - Fix missing or empty 'content' fields with realistic runnable code relevant to the user's request.
    - Add any missing 'install' or 'run' commands (like npm start, pip install, etc.).
    - Keep the same JSON structure.
    - Return only valid JSON, no extra text.
    """

        refined_json = self.client.generate(refine_prompt)
        print("🧠 Refinement requested from model...")

        return refined_json

