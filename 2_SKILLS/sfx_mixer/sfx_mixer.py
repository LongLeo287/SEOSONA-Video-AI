import os
import shutil
import random

def generate_sfx_tags(assets_dir, transition_timings, scene_timings, start_track_idx=7):
    sfx_tags = []
    track_idx = start_track_idx
    workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    assets_sfx_dir = os.path.join(workspace_dir, "7_ASSETS", "sfx")
    
    # Check if real assets exist
    whoosh_files = []
    pop_files = []
    if os.path.exists(os.path.join(assets_sfx_dir, "transitions")):
        whoosh_files = [os.path.join(assets_sfx_dir, "transitions", f) for f in os.listdir(os.path.join(assets_sfx_dir, "transitions")) if f.endswith(".wav")]
    if os.path.exists(os.path.join(assets_sfx_dir, "pops")):
        pop_files = [os.path.join(assets_sfx_dir, "pops", f) for f in os.listdir(os.path.join(assets_sfx_dir, "pops")) if f.endswith(".wav")]
        
    # Process Transitions (Whooshes)
    if transition_timings:
        for idx, transition_time in enumerate(transition_timings):
            # Pick a random whoosh if available
            chosen_whoosh = None
            if whoosh_files:
                chosen_whoosh = random.choice(whoosh_files)
                dest_whoosh = os.path.join(assets_dir, f"whoosh_{idx}.wav")
                shutil.copy2(chosen_whoosh, dest_whoosh)
                src_path = f"assets/whoosh_{idx}.wav"
            else:
                # Fallback to a single generated whoosh or just skip if not doing ffmpeg here
                src_path = "assets/sfx_whoosh.wav"
                
            sfx_tags.append(f'''      <audio
        id="sfx-whoosh-{idx}"
        src="{src_path}"
        data-start="{max(0.0, float(transition_time)):.3f}"
        data-duration="0.240"
        data-track-index="{track_idx}"
        data-volume="0.8"
      ></audio>''')
            track_idx += 1

    # Process Pops (for Scenes)
    if scene_timings:
        for idx, scene in enumerate(scene_timings):
            start_time = float(scene.get('start', 0))
            # Pick a random pop if available
            chosen_pop = None
            if pop_files:
                chosen_pop = random.choice(pop_files)
                dest_pop = os.path.join(assets_dir, f"pop_{idx}.wav")
                shutil.copy2(chosen_pop, dest_pop)
                src_path = f"assets/pop_{idx}.wav"
            else:
                src_path = "assets/sfx_pop.wav"
                
            sfx_tags.append(f'''      <audio
        id="sfx-pop-{idx}"
        src="{src_path}"
        data-start="{max(0.0, start_time + 0.35):.3f}"
        data-duration="0.08"
        data-track-index="{track_idx}"
        data-volume="0.6"
      ></audio>''')
            track_idx += 1
            
    return sfx_tags, track_idx
