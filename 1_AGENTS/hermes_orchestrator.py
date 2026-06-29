"""
Hermes Orchestrator Bridge.
Connects SEOSONA Video to the configured SEOSONA OS Hermes controller.
"""
import subprocess


def ask_hermes(task_description):
    bridge_script = 'D:\\SEOSONA AI\\SEOSONA OS\\1_CORE\\scripts\\hermes_brain.py'
    result = subprocess.run(
        ["python", bridge_script, "--task", task_description],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    return result.stdout
