"""
Supergraph Engine - Replaces Linear Pipeline
A lightweight, LangGraph-inspired directed graph state machine for Video Pipeline.
Allows loops, dynamic fallback, and conditional routing.
"""

class SuperGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.conditional_edges = {}
        self.entry_point = None

    def add_node(self, name, action_func):
        """Register a processing node (e.g. Scrape, TTS, Render)."""
        self.nodes[name] = action_func

    def add_edge(self, source, target):
        """Create a direct hardcoded path from source to target."""
        self.edges[source] = target

    def add_conditional_edge(self, source, condition_func):
        """Create a branching path based on the state output."""
        self.conditional_edges[source] = condition_func

    def set_entry_point(self, name):
        """Set the starting node."""
        self.entry_point = name

    def compile(self):
        if not self.entry_point:
            raise ValueError("[SuperGraph] Entry point not set!")
        return self

    def invoke(self, initial_state):
        """Run the graph pipeline."""
        print("\n" + "="*50)
        print("🕸️ SEOSONA SUPERGRAPH - EXECUTING WORKFLOW 🕸️")
        print("="*50)
        
        current_node = self.entry_point
        state = initial_state

        # This engine ALLOWS loops, so a buggy/oscillating condition_func could route forever and hang the
        # (unattended) render. Cap total steps — far above any real graph (a handful of nodes) — and abort
        # loudly instead of spinning. On trip, record an error so downstream routing/gates see the failure.
        steps, MAX_STEPS = 0, 200
        while current_node != "END":
            steps += 1
            if steps > MAX_STEPS:
                print(f"[Graph] ⚠ exceeded {MAX_STEPS} steps at [{current_node}] — aborting (non-terminating loop?)")
                state["error"] = f"graph exceeded {MAX_STEPS} steps (non-terminating loop)"
                break
            print(f"\n[Graph] ---> Entering Node: [{current_node.upper()}]")

            if current_node not in self.nodes:
                raise ValueError(f"Node '{current_node}' not found in graph.")

            action_func = self.nodes[current_node]
            try:
                state = action_func(state)
            except Exception as e:
                print(f"[Graph] ❌ FATAL ERROR in node [{current_node}]: {e}")
                state["error"] = str(e)
                # Fallback to END if uncaught
                break

            # Routing Logic
            if current_node in self.conditional_edges:
                condition = self.conditional_edges[current_node]
                next_node = condition(state)
                print(f"[Graph] Conditional Edge evaluated -> {next_node}")
                current_node = next_node
            elif current_node in self.edges:
                next_node = self.edges[current_node]
                current_node = next_node
            else:
                # If no edges defined, assume it's the end of the line
                current_node = "END"

        print("\n" + "="*50)
        print("✅ SEOSONA SUPERGRAPH - WORKFLOW COMPLETE ✅")
        print("="*50)
        return state

# Example usage (for tests)
if __name__ == "__main__":
    def script_node(state):
        print("Generating script...")
        state["script"] = "Xin chào thế giới"
        return state
        
    def tts_node(state):
        if not state.get("script"):
            state["error"] = "No script"
        print("Generating TTS...")
        return state
        
    def render_node(state):
        print("Rendering video...")
        state["video_path"] = "out.mp4"
        return state
        
    def check_audio(state):
        if "error" in state:
            return "END"
        return "RENDER"

    workflow = SuperGraph()
    workflow.add_node("SCRIPT", script_node)
    workflow.add_node("TTS", tts_node)
    workflow.add_node("RENDER", render_node)
    
    workflow.set_entry_point("SCRIPT")
    workflow.add_edge("SCRIPT", "TTS")
    workflow.add_conditional_edge("TTS", check_audio)
    workflow.add_edge("RENDER", "END")
    
    graph = workflow.compile()
    final_state = graph.invoke({"input": "test"})
    print(final_state)
