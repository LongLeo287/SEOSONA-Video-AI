"""
OODA Loop Cognitive Framework - loop-engineering implementation.
Provides a base class for agents to self-correct during generation.
"""
import time

class OODALoop:
    def __init__(self, agent_name, max_retries=3):
        self.agent_name = agent_name
        self.max_retries = max_retries

    def observe(self, state):
        """Analyze the current state or output."""
        # print(f"[{self.agent_name} OODA] Observing current state...")
        pass

    def orient(self, state, error_info):
        """Understand the error context."""
        print(f"[{self.agent_name} OODA] Orienting around issue: {error_info}")
        pass

    def decide(self, state, error_info):
        """Formulate a corrective action."""
        print(f"[{self.agent_name} OODA] Deciding on corrective action...")
        return "retry"

    def act(self, action_func, *args, **kwargs):
        """Execute the action with self-correction."""
        retries = 0
        last_error = None
        
        while retries < self.max_retries:
            try:
                # print(f"[{self.agent_name} OODA] Acting (Attempt {retries + 1}/{self.max_retries})...")
                result = action_func(*args, **kwargs)
                
                # Check for logic errors (e.g., subtitle too long)
                is_valid, error_msg = self.validate_result(result)
                if is_valid:
                    return result
                else:
                    raise ValueError(error_msg)
                    
            except Exception as e:
                last_error = str(e)
                self.observe(None)
                self.orient(None, last_error)
                decision = self.decide(None, last_error)
                
                if decision != "retry":
                    print(f"[{self.agent_name} OODA] Decision was not to retry. Aborting loop.")
                    break
                    
                retries += 1
                time.sleep(1) # Backoff
                
        print(f"[{self.agent_name} OODA] Failed after {self.max_retries} retries. Last error: {last_error}")
        return None

    def validate_result(self, result):
        """Override this in specific agents to validate logical correctness."""
        return True, ""
