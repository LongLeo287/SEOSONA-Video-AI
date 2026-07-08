# -*- coding: utf-8 -*-
"""SEOSONA Video — Inbox Queue Processor (Phase 3: RELIABILITY).

Drop N items in 0_INPUT_INBOX/production_queue.yaml → get N outputs, where ONE bad
item never sinks the batch. Hardened for unattended batch production:

  - per-item crash ISOLATION (a thrown exception is caught; the batch continues)
  - RETRY with backoff (default 2 attempts; transient failures recover)
  - per-item TIMEOUT (a hung render can't block the queue forever)
  - honest LOGGING — each item's stdout/stderr captured to logs/queue/<run>/; the
    tail is printed on failure (no silent failures)
  - crash-safe PROGRESS — the queue file is rewritten after EVERY item, so killing
    the run mid-batch never loses state or reprocesses a finished item
  - IDEMPOTENCY — a processed ledger skips items already completed in a prior run
  - a RUN REPORT (summary + machine-readable run.jsonl)

CLI:
    python scripts/queue_processor.py                 # process the queue
    python scripts/queue_processor.py --dry-run       # show the plan, run nothing
    python scripts/queue_processor.py --only news_videos
    python scripts/queue_processor.py --retries 3 --timeout 1800
Env (used by tests): SEOSONA_QUEUE_CMD_OVERRIDE='python -c "..."' replaces the real
command so the reliability machinery can be exercised without slow renders.
"""
import os
import sys
import json
import time
import signal
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# A queue runner must never die on a log line: force UTF-8 on a cp1252 Windows console.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import yaml
except ImportError:
    print("[-] PyYAML required: pip install pyyaml")
    sys.exit(1)

ROOT_DIR = Path(__file__).resolve().parent.parent
INBOX_DIR = ROOT_DIR / "0_INPUT_INBOX"
QUEUE_FILE = INBOX_DIR / "production_queue.yaml"
PENDING_DIR = INBOX_DIR / "pending_files"
DONE_DIR = INBOX_DIR / "done"
LOG_ROOT = ROOT_DIR / "logs" / "queue"
LEDGER = INBOX_DIR / ".processed_ledger.txt"

COMMAND_MAP = {
    "news_videos":   ["npm", "run", "video:news", "--"],
    "course_videos": ["npm", "run", "video:course", "--"],
    "carousels":     ["npm", "run", "post:image", "--"],
    "thumbnails":    ["npm", "run", "thumbnail:create", "--"],
}


def _now_tag():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def load_queue():
    if not QUEUE_FILE.exists():
        print(f"[-] Cannot find queue file: {QUEUE_FILE}")
        return None
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_queue(queue_data):
    # Atomic-ish: write to a temp then replace, so a crash never leaves a half-written
    # queue file (which would lose the whole batch's remaining items).
    tmp = QUEUE_FILE.with_suffix(".yaml.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.dump(queue_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    os.replace(tmp, QUEUE_FILE)


def _ledger():
    if not LEDGER.exists():
        return set()
    try:
        # errors="replace" so a few corrupt bytes garble a key or two (those items just re-render) instead
        # of raising UnicodeDecodeError; try/except so an unreadable ledger degrades to "re-render" (wasteful
        # but recoverable) rather than CRASHING the whole unattended daily run.
        return set(x.strip() for x in LEDGER.read_text(encoding="utf-8", errors="replace").splitlines()
                   if x.strip())
    except Exception:
        return set()


def _ledger_add(key):
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(key + "\n")


def _resolve_local(input_str):
    """If the item points at pending_files/, return (abs_path_str, Path) else (input_str, None)."""
    if input_str.startswith("pending_files/") or input_str.startswith("pending_files\\"):
        name = input_str.replace("\\", "/").split("/")[-1]
        p = PENDING_DIR / name
        return (str(p.absolute()), p) if p.exists() else (None, p)
    return input_str, None


def _kill_tree(p):
    """Kill a subprocess AND every descendant it spawned.

    The real command is `npm run ...`, which (through the Windows shell) fans out into
    cmd.exe → node → python (seosona-python.cjs) → Playwright/Chromium + ffmpeg. Killing
    only the direct child leaves that grandchild chain ORPHANED — detached processes that
    keep burning CPU/GPU/RAM and can hold file locks. Over a long autonomous run, repeated
    timeouts would pile up orphans until the machine is exhausted, so on timeout we tear
    down the whole tree/group rooted at the child we launched.
    """
    try:
        if os.name == "nt":
            # /T walks the child-PID tree from p.pid; /F forces. Reaps cmd.exe and all
            # of node/python/chromium/ffmpeg beneath it.
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
        else:
            # start_new_session=True made p the leader of its own process group; SIGKILL
            # the whole group so every descendant dies with it.
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
    except Exception:
        # Best effort: if the tree kill fails, at least kill the direct child.
        try:
            p.kill()
        except Exception:
            pass
    try:
        p.wait(timeout=10)   # reap so we don't leave a zombie / half-dead handle
    except Exception:
        pass


def run_command(cmd_prefix, input_val, log_path, timeout):
    """Run one production command, capturing output to log_path. Returns (ok, reason).

    On timeout the entire process TREE is killed (see _kill_tree) — subprocess.run's own
    timeout would only kill the direct child and orphan its grandchildren.
    """
    override = os.environ.get("SEOSONA_QUEUE_CMD_OVERRIDE")
    if override:
        import shlex
        cmd = shlex.split(override) + [input_val]
        use_shell = False
    else:
        cmd = cmd_prefix + [input_val]
        use_shell = (os.name == "nt")   # npm on Windows needs the shell

    # Launch the child as the root of its own group/session so _kill_tree has a handle on
    # every descendant. Windows: a new process group; POSIX: a new session (group leader).
    if os.name == "nt":
        launch_kw = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
    else:
        launch_kw = {"start_new_session": True}

    with open(log_path, "w", encoding="utf-8") as logf:
        logf.write(f"$ {' '.join(cmd)}\n\n")
        logf.flush()
        try:
            p = subprocess.Popen(cmd, cwd=ROOT_DIR, shell=use_shell,
                                 stdout=logf, stderr=subprocess.STDOUT, **launch_kw)
        except Exception as e:                       # spawn failure: never propagate
            logf.write(f"\n[EXCEPTION] {e}\n")
            return False, f"exception:{type(e).__name__}"
        try:
            p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            _kill_tree(p)
            logf.write(f"\n[TIMEOUT after {timeout}s — process tree killed]\n")
            return False, f"timeout>{timeout}s"
        except Exception as e:                       # crash isolation: never propagate
            _kill_tree(p)
            logf.write(f"\n[EXCEPTION] {e}\n")
            return False, f"exception:{type(e).__name__}"
    return (p.returncode == 0), (None if p.returncode == 0 else f"exit={p.returncode}")


def _tail(path, n=12):
    try:
        lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lines[-n:])
    except Exception:
        return "(no log)"


def _run_item(cmd_prefix, input_str, run_dir, n, category, raw, retries, timeout):
    """Render ONE item with retries. Pure (no shared-state mutation) → safe to run in a
    worker thread; each render is its own subprocess + project_dir, so parallel runs are
    isolated. Returns (ok, reason)."""
    ok, reason = False, "not-run"
    for attempt in range(1, retries + 1):
        log_path = run_dir / f"{category}_{n}_try{attempt}.log"
        print(f"[+] [{category}] {raw}  (attempt {attempt}/{retries})")
        ok, reason = run_command(cmd_prefix, input_str, log_path, timeout)
        if ok:
            break
        print(f"    [x] failed ({reason}); log: {log_path.name}")
        if attempt < retries:
            time.sleep(3 * attempt)
    return ok, reason


def process_queue(retries=2, timeout=1800, only=None, dry_run=False, concurrency=1):
    print("=" * 56)
    print("🚀 SEOSONA VIDEO — QUEUE PROCESSOR (reliability) 🚀")
    print("=" * 56)
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    DONE_DIR.mkdir(parents=True, exist_ok=True)

    if not dry_run:                     # using the queue auto-starts the dashboard
        try:
            sys.path.insert(0, str(ROOT_DIR / "9_DASHBOARD"))
            import autostart
            autostart.ensure_running()
        except Exception:
            pass

    queue_data = load_queue()
    if queue_data is None:
        return 1
    run_tag = _now_tag()
    run_dir = LOG_ROOT / run_tag
    if not dry_run:
        run_dir.mkdir(parents=True, exist_ok=True)
    ledger = _ledger()
    report = {"run": run_tag, "ok": [], "failed": [], "skipped": [], "stopped": None}

    # Circuit breaker (Loop Engineering "set ceilings"): bound run/day/wall + kill-switch.
    from loop_guard import LoopGuard
    guard = LoopGuard()
    if not dry_run:
        print(f"[guard] {guard.summary()}  | concurrency={concurrency}")

    # ── Phase A (main thread): build the render work-list. Skips/dedup/dry are handled
    # here with no rendering, so this stays thread-safe. ──
    orig = {cat: list(queue_data.get(cat) or []) for cat in COMMAND_MAP}
    work, n_seen = [], 0
    for category, cmd_prefix in COMMAND_MAP.items():
        if only and category != only:
            continue
        for item in orig[category]:
            if not item or str(item).strip() == "":
                continue
            n_seen += 1
            raw = str(item).strip()
            key = f"{category}::{raw}"
            if key in ledger:
                print(f"[=] skip (already done): {raw}"); report["skipped"].append(raw); continue
            input_str, local = _resolve_local(raw)
            if input_str is None:
                print(f"[!] missing pending file: {raw} — keeping in queue.")
                report["failed"].append({"item": raw, "reason": "file-not-found"}); continue
            if dry_run:
                cmd = os.environ.get("SEOSONA_QUEUE_CMD_OVERRIDE") or " ".join(cmd_prefix)
                print(f"[dry] {category}: {cmd} {input_str}"); continue
            work.append({"category": category, "cmd": cmd_prefix, "raw": raw, "key": key,
                         "input": input_str, "local": local, "n": n_seen})

    done_keys = set()

    def _rebuild_save():
        """Queue = everything NOT successfully done (failed + unprocessed + placeholders)."""
        for cat in COMMAND_MAP:
            queue_data[cat] = [i for i in orig[cat]
                               if (not str(i).strip()) or f"{cat}::{str(i).strip()}" not in done_keys]
        save_queue(queue_data)

    def _commit(unit, ok, reason):
        """Record one finished item. Runs ONLY in the main thread → no locks needed."""
        if ok:
            print(f"    [✓] done: {unit['raw']}")
            report["ok"].append(unit["raw"]); _ledger_add(unit["key"]); done_keys.add(unit["key"])
            local = unit["local"]
            if local and local.exists():
                try:
                    dest = DONE_DIR / local.name
                    if dest.exists():
                        dest.unlink()
                    shutil.move(str(local), str(dest)); print(f"    → moved to done/: {local.name}")
                except Exception as e:
                    print(f"    [!] could not move file: {e}")
        else:
            print(f"    [x] giving up after {retries} attempts: {unit['raw']}")
            print("    " + _tail(run_dir / f"{unit['category']}_{unit['n']}_try{retries}.log").replace("\n", "\n    "))
            report["failed"].append({"item": unit["raw"], "reason": reason})
        guard.record_item()
        _rebuild_save()                               # crash-safe: persist after EVERY item

    # ── Ceiling: only run up to the run/day budget; the rest stay queued. ──
    if not dry_run and work:
        kill_now, why = guard.should_stop()
        budget = max(0, min(guard.max_run, guard.max_day - guard.day_count))
        if kill_now:
            report["stopped"] = why; budget = 0
        to_run, deferred = work[:budget], work[budget:]
        if deferred and not report["stopped"]:
            report["stopped"] = f"ceiling reached (budget {budget})"
        if deferred:
            print(f"[GUARD] ⛔ deferring {len(deferred)} item(s) — {report['stopped']}")

        # ── Phase B: render. Sequential (concurrency=1) or isolated-parallel (>1). ──
        if concurrency <= 1:
            for u in to_run:
                stop, why = guard.should_stop()       # live check catches wall/kill mid-run
                if stop:
                    report["stopped"] = why
                    print(f"[GUARD] ⛔ stopping — {why}"); break
                ok, reason = _run_item(u["cmd"], u["input"], run_dir, u["n"], u["category"], u["raw"], retries, timeout)
                _commit(u, ok, reason)
        else:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            with ThreadPoolExecutor(max_workers=concurrency) as ex:
                futs = {ex.submit(_run_item, u["cmd"], u["input"], run_dir, u["n"],
                                  u["category"], u["raw"], retries, timeout): u for u in to_run}
                for fut in as_completed(futs):         # commit in main thread → thread-safe
                    u = futs[fut]
                    try:
                        ok, reason = fut.result()
                    except Exception as e:
                        ok, reason = False, f"worker-exception:{e}"
                    _commit(u, ok, reason)
    if not dry_run:
        _rebuild_save()

    # Run report
    print("\n" + "=" * 56)
    print(f"✅ ok={len(report['ok'])}  ✗ failed={len(report['failed'])}  = skipped={len(report['skipped'])}  (seen={n_seen})")
    for f in report["failed"]:
        print(f"   ✗ {f['item']}  — {f['reason']}")
    if report.get("stopped"):
        print(f"   ⛔ batch stopped early — {report['stopped']} (remaining items kept in queue)")
    if not dry_run:
        print(f"[guard] {guard.summary()}")
    print("=" * 56)
    if not dry_run:
        (run_dir / "run.jsonl").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"report: {run_dir / 'run.jsonl'}")
    return 0 if not report["failed"] else 2


def main():
    ap = argparse.ArgumentParser(description="SEOSONA queue processor")
    ap.add_argument("--retries", type=int, default=2)
    ap.add_argument("--timeout", type=int, default=1800, help="per-item seconds")
    ap.add_argument("--only", help="process only this category")
    ap.add_argument("--queue", help="override queue file path (default: production_queue.yaml)")
    ap.add_argument("--ledger", help="override processed-ledger path")
    ap.add_argument("--concurrency", type=int, default=1,
                    help="parallel renders (each isolated in its own subprocess+project_dir). Default 1.")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    global QUEUE_FILE, LEDGER
    if a.queue:
        QUEUE_FILE = Path(a.queue).resolve()
    if a.ledger:
        LEDGER = Path(a.ledger).resolve()
    sys.exit(process_queue(retries=a.retries, timeout=a.timeout, only=a.only,
                           dry_run=a.dry_run, concurrency=max(1, a.concurrency)))


if __name__ == "__main__":
    main()
