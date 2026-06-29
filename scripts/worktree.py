# -*- coding: utf-8 -*-
"""SEOSONA Video — git worktree isolation (Loop Engineering "one worktree per task").

Two kinds of parallelism need different isolation:

  - Parallel RENDERS (videos) → already isolated by the queue: each render is its own
    subprocess writing its own project_dir. Use `queue_processor.py --concurrency N`.
  - Parallel CODE edits (an agent changing repo files) → must NOT share the working tree,
    or concurrent edits collide ("tangled loop"). THIS module gives each such task its own
    git worktree so they can run truly in parallel without conflicts.

  python scripts/worktree.py add  fix-captions     # → .worktrees/fix-captions on branch loop/fix-captions
  python scripts/worktree.py list
  python scripts/worktree.py remove fix-captions    # cleans the worktree + leaves the branch
"""
import re
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WT_DIR = ROOT / ".worktrees"


def _git(*args, check=True):
    return subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True, text=True, check=check)


def _slug(name):
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", name.strip()).strip("-") or "task"


def add(name):
    """Create an isolated worktree + branch for a parallel code task. Returns its path."""
    slug = _slug(name)
    path = WT_DIR / slug
    branch = f"loop/{slug}"
    if path.exists():
        print(f"[worktree] exists: {path}")
        return str(path)
    WT_DIR.mkdir(exist_ok=True)
    # Reuse the branch if it already exists, else create it.
    exists = _git("rev-parse", "--verify", branch, check=False).returncode == 0
    args = ["worktree", "add", str(path)] + ([branch] if exists else ["-b", branch])
    r = _git(*args, check=False)
    if r.returncode != 0:
        print(f"[worktree] add failed: {r.stderr.strip()}")
        return None
    print(f"[worktree] + {path}  (branch {branch})")
    return str(path)


def remove(name):
    slug = _slug(name)
    path = WT_DIR / slug
    r = _git("worktree", "remove", str(path), "--force", check=False)
    print(f"[worktree] - {path}" if r.returncode == 0 else f"[worktree] remove failed: {r.stderr.strip()}")
    return r.returncode == 0


def lst():
    print(_git("worktree", "list", check=False).stdout.rstrip() or "(none)")


def main():
    if len(sys.argv) < 2:
        print("usage: python scripts/worktree.py {add|remove|list} [name]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "list":
        lst()
    elif cmd in ("add", "remove") and len(sys.argv) >= 3:
        (add if cmd == "add" else remove)(sys.argv[2])
    else:
        print("usage: python scripts/worktree.py {add|remove|list} [name]")
        sys.exit(1)


if __name__ == "__main__":
    main()
