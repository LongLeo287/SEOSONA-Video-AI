"""1_AGENTS — AI Agent modules for SEOSONA Video Factory."""
from importlib import import_module as _im

def get_agent(name):
    """Load an agent by directory name. Example: get_agent('scraper_agent')"""
    return _im(f"1_AGENTS.{name}")
