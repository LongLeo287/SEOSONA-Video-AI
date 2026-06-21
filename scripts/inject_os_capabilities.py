"""Inject selected SEOSONA OS skills and knowledge into this project."""
import os
import shutil
from pathlib import Path


def resolve_os_root() -> Path:
    configured = os.environ.get("SEOSONA_OS_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    return (Path.home() / ".seosona").resolve()


ROOT = Path(__file__).resolve().parents[1]
OS_ROOT = resolve_os_root()

skills_to_link = [
    "decodo-openclaw-skill",
    "humanizer",
    "gdrive-manager",
    "openclaw-skill-infographic",
]

for skill in skills_to_link:
    src = OS_ROOT / ".agents" / "skills" / skill
    dst = ROOT / "2_SKILLS" / f"os_{skill}"
    if src.exists() and not dst.exists():
        try:
            os.symlink(src, dst, target_is_directory=True)
            print(f"Symlinked skill: {skill}")
        except OSError:
            shutil.copytree(src, dst)
            print(f"Copied skill {skill}; symlink was not available.")

os_ki_dir = OS_ROOT / "3_MEMORY" / "knowledge_items"
video_ki_dir = ROOT / "2_KNOWLEDGE" / "data" / "os_knowledge"
video_ki_dir.mkdir(parents=True, exist_ok=True)

count_ki = 0
if os_ki_dir.exists():
    for item in os_ki_dir.glob("*.md"):
        name_lower = item.name.lower()
        if any(term in name_lower for term in ["ui", "design", "layout", "seosona"]):
            shutil.copy2(item, video_ki_dir / item.name)
            count_ki += 1
print(f"Injected {count_ki} knowledge items from SEOSONA OS.")

orchestrator_path = ROOT / "1_AGENTS" / "hermes_orchestrator.py"
bridge_script = OS_ROOT / "1_CORE" / "scripts" / "hermes_brain.py"
orchestrator_path.write_text(
    f'''"""
Hermes Orchestrator Bridge.
Connects SEOSONA Video to the configured SEOSONA OS Hermes controller.
"""
import subprocess


def ask_hermes(task_description):
    bridge_script = {str(bridge_script)!r}
    result = subprocess.run(
        ["python", bridge_script, "--task", task_description],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    return result.stdout
''',
    encoding="utf-8",
)
print("Injected Hermes Orchestrator Bridge.")
