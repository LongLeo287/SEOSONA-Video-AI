import json
import os

class IntentRouter:
    """
    SEOSONA Video - Intent Router
    Analyze user request and route to corresponding workflow.
    """
    def __init__(self):
        self.workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.workflows_dir = os.path.join(self.workspace_dir, "1_CORE", "workflows")
        
    def analyze_intent(self, user_prompt):
        prompt = user_prompt.lower()
        
        # Simple heuristic rules mapping to workflows
        if "news" in prompt:
            return "news_workflow.json"
        elif "product" in prompt or "promo" in prompt or "launch" in prompt:
            return "product_launch_workflow.json"
        elif "github" in prompt or "repo" in prompt or "code" in prompt:
            return "repo_video_workflow.json"
        else:
            return "general_video_workflow.json"
            
    def route(self, user_prompt):
        target_workflow = self.analyze_intent(user_prompt)
        workflow_path = os.path.join(self.workflows_dir, target_workflow)
        print(f"🧠 [Intent Router] Request: '{user_prompt}'")
        print(f"👉 [Intent Router] Routing to workflow: {target_workflow}")
        return workflow_path

if __name__ == "__main__":
    import sys
    router = IntentRouter()
    prompt = sys.argv[1] if len(sys.argv) > 1 else "make an ai news video"
    router.route(prompt)
