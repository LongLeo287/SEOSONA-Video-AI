"""
Skill Registry - Dynamic Skill Discovery & Execution
Implements the Claude-code-skill-manager Tier 1 Concept.
"""
import os
import sys
import importlib
from pathlib import Path

# Setup paths
BRAIN_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BRAIN_DIR.parent
SKILLS_DIR = PROJECT_ROOT / "2_SKILLS"

class SkillRegistry:
    def __init__(self):
        self.skills = {}
        self._discover_skills()

    def _discover_skills(self):
        """Dynamically scans 2_SKILLS directory and registers available modules."""
        if not SKILLS_DIR.exists():
            print("[SkillRegistry] Warning: 2_SKILLS directory not found.")
            return

        # Add project root to sys path if not already there
        if str(PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT))

        for item in SKILLS_DIR.iterdir():
            if item.is_dir() and not item.name.startswith(("_", ".")):
                self._register_skill_folder(item)

    def _register_skill_folder(self, folder_path):
        """Attempts to register the main module inside a skill folder."""
        skill_name = folder_path.name
        
        # Look for the main engine file (e.g. yt_dlp_engine.py inside yt_downloader)
        engine_files = list(folder_path.glob("*_engine.py"))
        if not engine_files:
            engine_files = list(folder_path.glob("*.py"))
            
        if engine_files:
            # We just map the skill name to the import path of the first matching file
            # e.g., 2_SKILLS.yt_downloader.yt_dlp_engine
            # Filter out __init__.py
            valid_files = [f for f in engine_files if f.name != "__init__.py"]
            if valid_files:
                target_file = valid_files[0]
                module_path = f"2_SKILLS.{skill_name}.{target_file.stem}"
                self.skills[skill_name] = module_path
                # print(f"[SkillRegistry] Registered skill: {skill_name} -> {module_path}")

    def load_skill(self, skill_name):
        """Dynamically imports and returns a skill module."""
        if skill_name not in self.skills:
            print(f"[SkillRegistry] Skill '{skill_name}' not found.")
            return None
        
        module_path = self.skills[skill_name]
        try:
            return importlib.import_module(module_path)
        except Exception as e:
            print(f"[SkillRegistry] Failed to load skill '{skill_name}': {e}")
            return None

    def execute_skill(self, skill_name, function_name, *args, **kwargs):
        """Dynamically executes a function from a registered skill."""
        module = self.load_skill(skill_name)
        if not module:
            return None
            
        if not hasattr(module, function_name):
            print(f"[SkillRegistry] Function '{function_name}' not found in skill '{skill_name}'.")
            return None
            
        func = getattr(module, function_name)
        return func(*args, **kwargs)

# Singleton instance
registry = SkillRegistry()

def get_skill(skill_name):
    return registry.load_skill(skill_name)
