# -*- coding: utf-8 -*-
"""SEOSONA Video — Loop Guard (circuit breaker).

From Loop Engineering's "set ceilings before shipping": an unattended loop that can't be
bounded delegates spending/run authority to its own bugs. This converts UNLIMITED risk to
BOUNDED risk. Free/local so the cost isn't dollars — it's render-time runaway and
infinite-retry storms. Ceilings:

  - max items per run          (SEOSONA_MAX_ITEMS_RUN, default 20)
  - max items per day          (SEOSONA_MAX_ITEMS_DAY, default 100)
  - max wall-clock per run     (SEOSONA_MAX_WALL_SECONDS, default 7200 = 2h)
  - KILL SWITCH: a file 0_INPUT_INBOX/STOP halts the loop immediately (manual abort)

Daily counters persist in logs/loop_guard_state.json and reset at date change.
Usage:
  g = LoopGuard()
  for item in items:
      stop, why = g.should_stop()
      if stop: break              # bounded — log `why`, leave the rest in queue
      ... process ...
      g.record_item()
"""
import os
import json
import time
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "logs" / "loop_guard_state.json"
KILL_SWITCH = ROOT / "0_INPUT_INBOX" / "STOP"


def _int_env(name, default):
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


class LoopGuard:
    def __init__(self):
        self.max_run = _int_env("SEOSONA_MAX_ITEMS_RUN", 20)
        self.max_day = _int_env("SEOSONA_MAX_ITEMS_DAY", 100)
        self.max_wall = _int_env("SEOSONA_MAX_WALL_SECONDS", 7200)
        self.t0 = time.time()
        self.run_count = 0
        self.today = datetime.now().strftime("%Y%m%d")
        self.day_count = self._load_day_count()

    def _load_day_count(self):
        try:
            d = json.loads(STATE.read_text(encoding="utf-8"))
            return int(d.get("count", 0)) if d.get("date") == self.today else 0
        except Exception:
            return 0

    def _persist(self):
        try:
            STATE.parent.mkdir(parents=True, exist_ok=True)
            STATE.write_text(json.dumps({"date": self.today, "count": self.day_count},
                                        ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    def should_stop(self):
        """Return (stop: bool, reason: str|None) — check BEFORE processing each item."""
        if KILL_SWITCH.exists():
            return True, "KILL SWITCH (0_INPUT_INBOX/STOP present)"
        if self.run_count >= self.max_run:
            return True, f"max items/run reached ({self.max_run})"
        if self.day_count >= self.max_day:
            return True, f"max items/day reached ({self.max_day})"
        elapsed = time.time() - self.t0
        if elapsed >= self.max_wall:
            return True, f"max wall-clock reached ({self.max_wall}s)"
        return False, None

    def record_item(self):
        """Count one processed item (success OR fail) toward the ceilings."""
        self.run_count += 1
        self.day_count += 1
        self._persist()

    def summary(self):
        return (f"items run={self.run_count}/{self.max_run} · day={self.day_count}/{self.max_day} · "
                f"elapsed={int(time.time()-self.t0)}s/{self.max_wall}s")


if __name__ == "__main__":
    g = LoopGuard()
    print("LoopGuard limits:", g.summary())
    print("kill switch:", "ON" if KILL_SWITCH.exists() else "off", f"({KILL_SWITCH})")
    print("should_stop:", g.should_stop())
