"""2_SKILLS — Technical skill modules for SEOSONA Video Factory."""
from importlib import import_module as _im

def get_skill(name):
    """Load a skill by directory name. Example: get_skill('voice_cloner')"""
    return _im(f"2_SKILLS.{name}")
