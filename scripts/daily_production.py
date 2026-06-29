# -*- coding: utf-8 -*-
"""SEOSONA Video — Daily Production runner (Phase 5: SCALE).

The single entry you SCHEDULE for unattended daily output. It runs the reliable
inbox queue (Phase 3 `queue_processor`), optionally batches GitHub news, and
publishes if configured — all free/local by default; paid steps stay off unless
their keys are set.

Free by default:
  - render = VieNeu (local) + HyperFrames (local) — no paid API
  - publish = whatever SEOSONA_PUBLISH lists; with no credentials every destination
    is skipped (never crashes). Telegram is the free instant target.

Usage:
  python scripts/daily_production.py                      # process the inbox queue
  python scripts/daily_production.py --news sources.txt   # + GitHub news batch
  SEOSONA_PUBLISH=telegram python scripts/daily_production.py   # + publish (free)

Schedule it: see deploy/SCHEDULING.md (Windows schtasks / Linux cron).
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent.parent


def _log_line(logf, msg):
    print(msg)
    logf.write(msg + "\n")
    logf.flush()


def main():
    ap = argparse.ArgumentParser(description="SEOSONA daily production")
    ap.add_argument("--news", help="file of GitHub URLs (one per line) for the news batch")
    ap.add_argument("--retries", type=int, default=2)
    ap.add_argument("--timeout", type=int, default=1800)
    a = ap.parse_args()

    tag = datetime.now().strftime("%Y%m%d-%H%M%S")
    logdir = ROOT / "logs" / "daily"
    logdir.mkdir(parents=True, exist_ok=True)
    rc_total = 0
    with open(logdir / f"{tag}.log", "w", encoding="utf-8") as logf:
        publish = os.environ.get("SEOSONA_PUBLISH", "").strip() or "(off)"
        _log_line(logf, f"[daily] SEOSONA production {tag} | publish={publish}")

        # Using SEOSONA Video auto-starts the health dashboard (background, idempotent).
        try:
            sys.path.insert(0, str(ROOT / "9_DASHBOARD"))
            import autostart
            autostart.ensure_running()
        except Exception:
            pass

        # 1) Inbox queue (the reliable batch — retry/isolation/idempotency built in).
        _log_line(logf, "[daily] ── inbox queue ──")
        rc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "queue_processor.py"),
             "--retries", str(a.retries), "--timeout", str(a.timeout)],
            cwd=ROOT,
        ).returncode
        rc_total |= (1 if rc not in (0, 2) else 0)   # 2 = some items failed (logged), still a clean run
        _log_line(logf, f"[daily] queue exit={rc} (0=all ok, 2=some failed+logged)")

        # 2) Optional GitHub news batch (rotates templates so the feed isn't repetitive).
        if a.news:
            src = Path(a.news)
            if src.exists():
                urls = [u.strip() for u in src.read_text(encoding="utf-8").splitlines()
                        if u.strip() and not u.strip().startswith("#")]
                _log_line(logf, f"[daily] ── news batch ({len(urls)} urls) ──")
                rc2 = subprocess.run(
                    [sys.executable, str(ROOT / "4_BRAIN" / "make_video.py"), "--news", str(src)],
                    cwd=ROOT,
                ).returncode
                rc_total |= (1 if rc2 != 0 else 0)
                _log_line(logf, f"[daily] news exit={rc2}")
            else:
                _log_line(logf, f"[daily] [!] news sources file not found: {src}")

        # 3) Close the feedback loop: recompute the quality gate from this batch's signals
        #    so the NEXT batch is held to the bar we've actually demonstrated (Phase 6).
        _log_line(logf, "[daily] ── feedback loop ──")
        try:
            sys.path.insert(0, str(ROOT / "9_DASHBOARD"))
            import feedback_loop
            st = feedback_loop.write_state()
            _log_line(logf, f"[daily] feedback gate={st['recommended_gate']} "
                            f"avg={st['avg_score']} pass={st['pass_rate']}%")
        except Exception as e:
            _log_line(logf, f"[daily] feedback loop skipped: {e}")

        _log_line(logf, f"[daily] DONE {tag} | overall={'ok' if rc_total == 0 else 'had-errors'}")
    return rc_total


if __name__ == "__main__":
    sys.exit(main())
