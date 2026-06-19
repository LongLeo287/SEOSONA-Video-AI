"""
Editor Agent — Manages scene composition, text placement, and visual quality.
"""
import os
import yaml

def load_brand_profile(brand="seosona"):
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'system_config.yaml'))
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config['profiles'].get(brand, config['profiles']['cqa'])

def validate_scenes(scenes, min_scenes=3, max_scene_duration=10):
    """
    Validates scene array before sending to renderer.
    Ensures minimum scene count and max duration per scene.
    """
    issues = []

    if len(scenes) < min_scenes:
        issues.append(f"Only {len(scenes)} scenes — minimum is {min_scenes}. Add more B-roll.")

    for i, scene in enumerate(scenes):
        duration = scene.get('end', 0) - scene.get('start', 0)
        if duration > max_scene_duration:
            issues.append(f"Scene {i+1} is {duration:.1f}s — max is {max_scene_duration}s. Split it.")

        path = scene.get('path', '')
        if not os.path.exists(path):
            issues.append(f"Scene {i+1} file not found: {path}")

    if issues:
        print("[Editor Agent] Scene validation issues:")
        for issue in issues:
            print(f"  ⚠ {issue}")
    else:
        print(f"[Editor Agent] ✓ All {len(scenes)} scenes validated.")

    return {"valid": len(issues) == 0, "issues": issues}

def suggest_scene_split(total_duration, target_scene_duration=7):
    """
    Suggests how many scenes are needed and their approximate durations.
    """
    num_scenes = max(3, int(total_duration / target_scene_duration))
    scene_duration = total_duration / num_scenes

    print(f"[Editor Agent] Suggest {num_scenes} scenes, ~{scene_duration:.1f}s each for {total_duration:.1f}s video.")
    return {
        "num_scenes": num_scenes,
        "scene_duration": round(scene_duration, 1)
    }

def enforce_light_mode(brand_profile):
    """
    Final check: ensures no dark colors leak into the render.
    """
    dark_colors = ['#000000', '#1A1A1A', '#111111', '#0D0D0D', '#121212', '#1E1E1E', '#2D2D2D']
    for key, color in brand_profile.get('colors', {}).items():
        if color.upper() in dark_colors:
            print(f"[Editor Agent] 🚨 VIOLATION: '{key}' uses dark color {color}. Overriding to #FFFFFF.")
            brand_profile['colors'][key] = '#FFFFFF'
    return brand_profile
