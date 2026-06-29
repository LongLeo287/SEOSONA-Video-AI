# -*- coding: utf-8 -*-
"""SEOSONA Video — Factory Brain (the autonomous loop orchestrator).

Runs ONE turn of the self-improving factory, unattended and guard-railed:

    PLAN ──▶ PRODUCE ──▶ RECORD ──▶ QA-GATE ──▶ (PUBLISH) ──▶ LEARN ──▶ report

It does NOT reimplement any stage — it conducts the pieces that already exist:
  • PRODUCE  → scripts/queue_processor.py (crash-isolated batch)
  • RECORD   → 4_BRAIN/production_manifest.py (variant tagging)
  • QA-GATE  → 4_BRAIN/quality_scorer.py (via the manifest)
  • PUBLISH  → 1_AGENTS/publisher_agent (behind the approval gate; off until creds)
  • LEARN    → 4_BRAIN/factory_ledger.py + analytics_feedback_agent
Guardrails come from 1_CONFIG/factory_policy.yaml (kill switch, QA min, caps, level).

This is the orchestrator of 6_SOP/AUTONOMOUS_FACTORY_LOOP.md. Cron it for full
autonomy; run it by hand to do one supervised turn.

    python 4_BRAIN/factory_brain.py            # one loop turn (honours policy)
    python 4_BRAIN/factory_brain.py --dry-run  # plan only, produce nothing
    python 4_BRAIN/factory_brain.py --learn-only   # just rebuild the ledger
"""
import os, sys, json, subprocess
from datetime import datetime, timezone

# Never die on a log line: a cron/Windows cp1252 console can't encode the emoji
# banners — force UTF-8 on our streams (same guard as native_composer/queue_processor).
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (ROOT, os.path.dirname(__file__)):
    if p not in sys.path:
        sys.path.insert(0, p)

import production_manifest as pm
import factory_ledger

POLICY_PATH = os.path.join(ROOT, "1_CONFIG", "factory_policy.yaml")
QUEUE_PATH = os.path.join(ROOT, "0_INPUT_INBOX", "production_queue.yaml")
WORKSPACE = os.path.join(ROOT, "8_WORKSPACE")
RUNLOG_DIR = os.path.join(ROOT, "3_MEMORY", "factory_runs")

DEFAULT_POLICY = {
    "autonomy_level": 1, "kill_switch": False,
    "quality": {"min_score": 70, "require_pass": True},
    "publish": {"enabled": False, "require_approval": True, "platforms": [], "daily_cap": 3},
    "production": {"batch_max": 10, "retries": 2, "timeout_s": 1800},
    "learning": {"rebuild_ledger": True, "explore_ratio": 0.2},
    "budget": {"max_videos_per_day": 30},
}


def _now():
    return datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()


def load_policy():
    try:
        import yaml
        with open(POLICY_PATH, encoding="utf-8") as f:
            p = yaml.safe_load(f) or {}
        # shallow-merge onto defaults so a partial file can't crash the loop
        merged = dict(DEFAULT_POLICY)
        for k, v in p.items():
            if isinstance(v, dict) and isinstance(merged.get(k), dict):
                merged[k] = {**merged[k], **v}
            else:
                merged[k] = v
        return merged
    except Exception as e:
        print(f"[factory] policy load failed ({e}); using safe defaults.")
        return dict(DEFAULT_POLICY)


def _queue_size():
    try:
        import yaml
        with open(QUEUE_PATH, encoding="utf-8") as f:
            q = yaml.safe_load(f) or {}
        return sum(len([x for x in (q.get(k) or []) if x and str(x).strip()])
                   for k in q)
    except Exception:
        return 0


def _produced_today():
    today = datetime.now().strftime("%Y-%m-%d")
    return sum(1 for m in pm.scan(WORKSPACE) if (m.get("created") or "").startswith(today))


def produce(policy, dry_run):
    """Run the existing queue processor for one batch."""
    cmd = [sys.executable, os.path.join(ROOT, "scripts", "queue_processor.py"),
           "--retries", str(policy["production"]["retries"]),
           "--timeout", str(policy["production"]["timeout_s"])]
    if dry_run:
        cmd.append("--dry-run")
    print(f"[factory] PRODUCE: {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=ROOT)
    return r.returncode


def record_and_gate(policy):
    """Record manifests for any produced project missing one, then QA-gate them."""
    minq = policy["quality"]["min_score"]
    require_pass = policy["quality"]["require_pass"]
    eligible, blocked = [], []
    for entry in sorted(os.listdir(WORKSPACE)) if os.path.isdir(WORKSPACE) else []:
        pdir = os.path.join(WORKSPACE, entry)
        if not os.path.isdir(pdir) or entry.startswith((".", "_")):
            continue
        man = pm.load(pdir)
        if not man:
            # tag any untagged finished project (best-effort variant inference)
            # DIRECT mp4 only (not recursive) — else a CONTAINER dir (e.g. 8_WORKSPACE/auto
            # holding many project subfolders) gets mis-tagged as one video.
            has_mp4 = any(f.endswith(".mp4") for f in os.listdir(pdir)
                          if os.path.isfile(os.path.join(pdir, f)))
            if not has_mp4:
                continue
            man = pm.record(pdir)
        q = man.get("quality") or {}
        ok = (q.get("score") or 0) >= minq and (q.get("pass") if require_pass else True)
        (eligible if ok else blocked).append(man["video_id"])
    return eligible, blocked


def maybe_publish(policy, eligible, dry_run):
    pub = policy["publish"]
    if not pub.get("enabled"):
        return {"status": "disabled", "reason": "publish.enabled=false (Phase 4: needs credentials)"}
    if policy["autonomy_level"] < 2 or pub.get("require_approval"):
        return {"status": "awaiting_approval", "queued_for_approval": eligible,
                "note": "L1: human approves before publish (telegram/dashboard)."}
    if dry_run:
        return {"status": "dry-run", "would_publish": eligible[:pub.get("daily_cap", 3)]}
    # L2+: auto-publish up to the daily cap — actual dispatch handled by publisher_agent.
    return {"status": "auto", "publish": eligible[:pub.get("daily_cap", 3)]}


def learn(policy):
    if not policy["learning"].get("rebuild_ledger"):
        return None
    led = factory_ledger.rebuild(WORKSPACE)
    # post-mortems for the most recent few (re-grounded feedback agent)
    try:
        sys.path.insert(0, os.path.join(ROOT, "1_AGENTS", "analytics_feedback_agent"))
        import feedback_generator as fg
        recent = sorted([m for m in pm.scan(WORKSPACE)],
                        key=lambda m: m.get("created") or "", reverse=True)[:3]
        for m in recent:
            try:
                fg.generate_post_mortem(m["project_dir"])
            except Exception as e:
                print(f"[factory] post-mortem skipped for {m['video_id']}: {e}")
    except Exception as e:
        print(f"[factory] feedback agent unavailable: {e}")
    return led


def run(dry_run=False, learn_only=False):
    policy = load_policy()
    report = {"started": _now(), "policy_level": policy["autonomy_level"], "dry_run": dry_run}
    print("=" * 60)
    print(f"🏭 FACTORY BRAIN — level {policy['autonomy_level']}  (dry_run={dry_run})")
    print("=" * 60)

    if policy.get("kill_switch"):
        print("[factory] KILL SWITCH ON — refusing to run.")
        return {"status": "halted", "reason": "kill_switch"}

    if learn_only:
        led = learn(policy)
        return {"status": "learn-only", "videos": led["total_videos"] if led else 0,
                "template_weights": led.get("template_weights") if led else {}}

    # budget guard
    today = _produced_today()
    if today >= policy["budget"]["max_videos_per_day"]:
        print(f"[factory] daily budget reached ({today}). Stopping.")
        return {"status": "budget-reached", "produced_today": today}

    # PLAN (lightweight here; the strategist skill enriches the queue out-of-band)
    qsize = _queue_size()
    report["queue_size"] = qsize
    if qsize == 0 and not dry_run:
        print("[factory] queue empty — nothing to PRODUCE. "
              "(Strategist/ideation fills 0_INPUT_INBOX/production_queue.yaml.)")
    else:
        produce(policy, dry_run)

    # RECORD + QA-GATE
    eligible, blocked = record_and_gate(policy)
    report["eligible"] = eligible
    report["blocked_by_qa"] = blocked
    print(f"[factory] QA gate: {len(eligible)} eligible, {len(blocked)} blocked.")

    # PUBLISH (gated)
    report["publish"] = maybe_publish(policy, eligible, dry_run)
    print(f"[factory] PUBLISH: {report['publish']['status']}")

    # LEARN
    led = learn(policy)
    if led:
        report["learning"] = {"total_videos": led["total_videos"],
                              "signal": led["signal"],
                              "template_weights": led.get("template_weights", {})}
        print(f"[factory] LEARN: ledger over {led['total_videos']} videos "
              f"(signal={led['signal']}).")

    report["finished"] = _now()
    if not dry_run:
        os.makedirs(RUNLOG_DIR, exist_ok=True)
        tag = datetime.now().strftime("%Y%m%d-%H%M%S")
        with open(os.path.join(RUNLOG_DIR, f"run-{tag}.json"), "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    print("=" * 60)
    return report


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="SEOSONA autonomous factory — one loop turn")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--learn-only", action="store_true", help="just rebuild the ledger + feedback")
    a = ap.parse_args()
    out = run(dry_run=a.dry_run, learn_only=a.learn_only)
    print(json.dumps(out, ensure_ascii=False, indent=2))
