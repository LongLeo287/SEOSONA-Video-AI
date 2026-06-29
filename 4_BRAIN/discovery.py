# -*- coding: utf-8 -*-
"""SEOSONA Video — Discovery (Loop Engineering move #2).

The fix for the "blind loop": the loop should identify its own work, not have a human
hand-pick each item. Discovery reads a maintained source list, drops anything already
done (the processed-ledger) or already queued, and appends the NEW items to the
production queue — so a scheduled run picks up fresh work by itself.

Source = `0_INPUT_INBOX/sources.txt` (one per line; GitHub URL or a Vietnamese topic;
`#` lines ignored). Free/local; no network needed for the source list itself.

  python 4_BRAIN/discovery.py            # discover + enqueue new items
  python 4_BRAIN/discovery.py --dry-run  # show what would be added, change nothing

Called at the start of scripts/daily_production.py so each batch self-discovers.
"""
import os
import sys
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[discovery] PyYAML required")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "0_INPUT_INBOX"
SOURCES = INBOX / "sources.txt"
QUEUE = INBOX / "production_queue.yaml"
LEDGER = INBOX / ".processed_ledger.txt"
CATEGORY = "news_videos"     # discovered items become news videos


def _ledger():
    if not LEDGER.exists():
        return set()
    return set(x.strip() for x in LEDGER.read_text(encoding="utf-8").splitlines() if x.strip())


def _read_sources():
    if not SOURCES.exists():
        return []
    out = []
    for line in SOURCES.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            out.append(s)
    return out


def discover(dry_run=False):
    sources = _read_sources()
    if not sources:
        print(f"[discovery] no sources ({SOURCES} empty or missing) — nothing to discover.")
        return []
    if not QUEUE.exists():
        print(f"[discovery] queue file missing: {QUEUE}")
        return []
    queue = yaml.safe_load(QUEUE.read_text(encoding="utf-8")) or {}
    current = [str(i).strip() for i in (queue.get(CATEGORY) or []) if str(i).strip()]
    ledger = _ledger()

    added, skipped = [], []
    for s in sources:
        if f"{CATEGORY}::{s}" in ledger:
            skipped.append((s, "already done"))
        elif s in current:
            skipped.append((s, "already queued"))
        else:
            added.append(s)

    print(f"[discovery] {len(sources)} sources · {len(added)} new · {len(skipped)} skipped")
    for s in added:
        print(f"  + {s}")
    if added and not dry_run:
        placeholders = [i for i in (queue.get(CATEGORY) or []) if not str(i).strip()]
        queue[CATEGORY] = current + added + placeholders   # keep template placeholders last
        tmp = QUEUE.with_suffix(".yaml.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.dump(queue, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        os.replace(tmp, QUEUE)
        print(f"[discovery] enqueued {len(added)} item(s) → {QUEUE.name}")
    elif dry_run:
        print("[discovery] dry-run — queue not modified")
    return added


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    discover(dry_run=a.dry_run)
