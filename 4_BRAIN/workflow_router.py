"""
Workflow Router - Smart video entry point.
"""
import os
import sys
from importlib import import_module
from skill_registry import get_skill
from graph_executor import SuperGraph

# --- SEOSONA AUTO-BOOTSTRAP ---
try:
    brain_dir = os.path.dirname(os.path.abspath(__file__))
    if brain_dir not in sys.path:
        sys.path.insert(0, brain_dir)
    bootstrap = import_module("seosona_bootstrap")
    bootstrap.bootstrap()
except Exception as e:
    print(f"[Router] Bootstrap check failed: {e}")
# ------------------------------

# MoviePy 1.0.3 compatibility with Pillow >= 10.
from PIL import Image

if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS


def detect_input_type(input_value):
    """Auto-detect the input type. Single source of truth lives in the unified
    engine (`video_engine.detect_input_type`); this delegates to it."""
    return import_module("video_engine").detect_input_type(input_value)


def route(input_value, brand="seosona", aspect_ratio="9:16", project_name=None):
    """
    Routes only video workflows. Image and carousel workflows use dedicated
    entrypoints under scripts/.
    """
    mode, processed_input = detect_input_type(input_value)

    print(f"[Router] Input detected as: {mode.upper()}")
    print(f"[Router] Brand: {brand.upper()}")
    print(f"[Router] Aspect Ratio: {aspect_ratio}")

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.append(project_root)

    if mode == "download":
        print("[Router] -> Step 1: yt-dlp Download")
        yt_engine = get_skill("yt_downloader")
        download_dir = os.path.join(project_root, "8_WORKSPACE", project_name or "yt_download", ".temp")
        yt_engine.download_video(processed_input, download_dir)

        print("[Router] -> Step 2: Routing downloaded file to Repurpose Pipeline")
        video_files = [
            f for f in os.listdir(download_dir) if f.endswith((".mp4", ".mkv", ".webm"))
        ] if os.path.exists(download_dir) else []
        if not video_files:
            print("[Router] No video file found after download. Aborting.")
            return None
        processed_input = os.path.join(download_dir, video_files[0])
        mode = "repurpose"
    elif mode == "repurpose":
        print("[Router] -> Routing to: SRT Analyzer -> Clipper -> Render Pipeline")
    elif mode == "scrape":
        print("[Router] -> Step 1: Web Scraping")
        print("[Router] -> Step 2: Extracting News Script")
        print("[Router] -> Step 3: Screen Recording / Screenshots")
        print("[Router] -> Step 4: Routing to Render Pipeline")
    else:
        print("[Router] -> Routing to: TTS -> Subtitles -> HyperFrames Render")

    engine = import_module("video_engine")

    # ---------------------------------------------------------
    # SUPERGRAPH INTEGRATION
    # Wrap the unified video_engine inside the DAG Graph so the quality gate +
    # post-mortem feedback run around every render, regardless of input mode.
    # ---------------------------------------------------------
    import datetime
    
    # Pre-calculate project name to ensure we know the exact output directory
    final_project_name = project_name
    if not final_project_name:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        final_project_name = f"{brand.upper()}_{timestamp}"
        
    final_project_dir = os.path.join(project_root, "8_WORKSPACE", final_project_name)

    def legacy_pipeline_node(state):
        print("[Graph] Executing video_engine render...")
        try:
            result = engine.run_pipeline(
                state["input_val"],
                brand=state["brand"],
                mode=state["mode"],
                aspect_ratio=state["ratio"],
                project_name=state["name"],
            )
            state["output"] = result
        except Exception as e:
            state["error"] = str(e)
        return state

    def check_result(state):
        # Real conditional routing (was "EVALUATE" on both branches — a no-op):
        # a failed pipeline goes to ABORT (post-mortem, no quality gate); a
        # successful one goes to EVALUATE (run the real quality gate).
        if "error" in state:
            print(f"[Graph] Pipeline error: {state.get('error')} -> ABORT")
            return "ABORT"
        return "EVALUATE"

    def abort_node(state):
        print("[Graph] ABORT: pipeline failed; recording post-mortem, skipping quality gate.")
        try:
            feedback_gen = import_module("1_AGENTS.analytics_feedback_agent.feedback_generator")
            feedback_gen.generate_post_mortem(state)
        except Exception as e:
            print(f"[Graph] Warning: post-mortem failed: {e}")
        state["quality_score"] = 0
        return state

    def evaluate_node(state):
        print("[Graph] Executing Evaluate Node (Quality Review & Feedback)...")
        # Run the REAL quality gate on the rendered video (was a hardcoded 85).
        video = None
        if os.path.isdir(final_project_dir):
            for root_d, _, files in os.walk(final_project_dir):
                for fn in files:
                    if fn.lower().endswith(".mp4"):
                        video = os.path.join(root_d, fn)
                        break
                if video:
                    break
        if video:
            try:
                qs = import_module("4_BRAIN.quality_scorer")
                report = qs.score_video(video, brand=state.get("brand", "seosona"))
                state["quality_score"] = report.get("score", 0)
                state["quality_report"] = report
                print(f"[Graph] Quality gate: {state['quality_score']}/100 "
                      f"({'PASS' if report.get('pass') else 'FAIL'})")
            except Exception as e:
                print(f"[Graph] quality_scorer failed: {e}")
                state["quality_score"] = 0
        else:
            print("[Graph] No output video found — quality not scored.")
            state["quality_score"] = 0
            
        # Hook into analytics feedback agent
        try:
            feedback_gen = import_module("1_AGENTS.analytics_feedback_agent.feedback_generator")
            feedback_gen.generate_post_mortem(state)
        except Exception as e:
            print(f"[Graph] Warning: Feedback generation failed: {e}")
        return state

    workflow = SuperGraph()
    workflow.add_node("MAIN_PIPELINE", legacy_pipeline_node)
    workflow.add_node("EVALUATE", evaluate_node)
    workflow.add_node("ABORT", abort_node)
    
    workflow.set_entry_point("MAIN_PIPELINE")
    workflow.add_conditional_edge("MAIN_PIPELINE", check_result)
    workflow.add_edge("EVALUATE", "END")
    workflow.add_edge("ABORT", "END")
    
    graph = workflow.compile()
    
    initial_state = {
        "input_val": processed_input,
        "brand": brand,
        "mode": mode,
        "ratio": aspect_ratio,
        "name": final_project_name,
        "project_dir": final_project_dir
    }
    
    final_state = graph.invoke(initial_state)
    return final_state.get("output")


if __name__ == "__main__":
    input_val = sys.argv[1] if len(sys.argv) > 1 else "Welcome to SEOSONA Video Factory."
    brand = sys.argv[2] if len(sys.argv) > 2 else "seosona"
    ratio = sys.argv[3] if len(sys.argv) > 3 else "9:16"
    name = sys.argv[4] if len(sys.argv) > 4 else None
    mode_override = sys.argv[5] if len(sys.argv) > 5 else None

    if mode_override:
        if mode_override == "carousel":
            raise RuntimeError(
                "Carousel is an image workflow. Use scripts/workflow_social_post.py or npm run post:image."
            )
        _, processed = detect_input_type(input_val)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        sys.path.append(project_root)
        engine = import_module("video_engine")
        engine.run_pipeline(processed, brand=brand, mode=mode_override, aspect_ratio=ratio, project_name=name)
    else:
        route(input_val, brand, ratio, name)
