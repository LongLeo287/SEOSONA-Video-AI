# -*- coding: utf-8 -*-
"""SEOSONA Video — Production Manifest (the factory's variant-tagging keystone).

Every produced video gets ONE manifest: `<project_dir>/production_manifest.json`.
It ties the finished file to the *variant* that made it — template, brand, aspect,
voice, topic, length — plus its QA score and (later) real-world performance.

Without this, the factory can produce but can NEVER learn: there is nothing to join
"what we made" to "how it did". This is Step A of 6_SOP/AUTONOMOUS_FACTORY_LOOP.md.

Non-invasive by design: the orchestrator (factory_brain) calls `record()` AFTER a
project is produced — the render engines are not modified.
"""
import os, sys, json, glob
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

MANIFEST_NAME = "production_manifest.json"


def _now_iso():
    return datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()


def _find_outputs(project_dir):
    """Locate the final mp4 / srt / thumbnail inside a produced project dir."""
    mp4s = [p for p in glob.glob(os.path.join(project_dir, "**", "*.mp4"), recursive=True)
            if not os.path.basename(p).startswith("_raw")]
    mp4 = max(mp4s, key=os.path.getsize) if mp4s else None
    srts = glob.glob(os.path.join(project_dir, "**", "*.srt"), recursive=True)
    thumbs = glob.glob(os.path.join(project_dir, "Thumbnail", "*.png")) + \
             glob.glob(os.path.join(project_dir, "Thumbnail", "*.jpg"))
    return {
        "mp4": os.path.relpath(mp4, project_dir) if mp4 else None,
        "srt": os.path.relpath(srts[0], project_dir) if srts else None,
        "thumbnail": os.path.relpath(thumbs[0], project_dir) if thumbs else None,
    }


def _write_script_txt(project_dir, srt_rel):
    """Plain narration → <project_dir>/script.txt (CapCut auto-caption aid; idea from
    AI-auto-generate-video's 3-file output). Derived from the sidecar SRT so it needs
    no extra inputs — strips indices/timestamps, dedupes consecutive lines."""
    if not srt_rel:
        return None
    srt = os.path.join(project_dir, srt_rel)
    if not os.path.exists(srt):
        return None
    lines, prev = [], None
    for ln in open(srt, encoding="utf-8", errors="replace"):
        t = ln.strip()
        if not t or t.isdigit() or "-->" in t:
            continue
        if t != prev:
            lines.append(t); prev = t
    out = os.path.join(project_dir, "script.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write(" ".join(lines).strip() + "\n")
    return out


def _length_bucket(seconds):
    if not seconds:
        return "unknown"
    s = float(seconds)
    if s < 30:   return "<30s"
    if s < 60:   return "30-60s"
    if s < 120:  return "60-120s"
    return ">120s"


def _duration(mp4_path):
    if not mp4_path or not os.path.exists(mp4_path):
        return None
    try:
        import native_composer as nc
        import subprocess
        out = subprocess.run([nc._ffprobe_bin(), "-v", "error", "-show_entries",
                              "format=duration", "-of", "csv=p=0", mp4_path],
                             capture_output=True, text=True, timeout=20).stdout.strip()
        return round(float(out), 1) if out else None
    except Exception:
        return None


def record(project_dir, *, template=None, brand="seosona", topic=None, aspect="9:16",
           voice=None, source=None, hook_style=None, thumbnail_style=None,
           quality=None, video_id=None, engine="synthesized", extra=None):
    """Write a production manifest for a produced project. Returns the manifest dict.

    quality: a quality_scorer.score_video() result dict (or None → auto-score the mp4).
    """
    project_dir = os.path.abspath(project_dir)
    outputs = _find_outputs(project_dir)
    mp4_abs = os.path.join(project_dir, outputs["mp4"]) if outputs["mp4"] else None
    dur = _duration(mp4_abs)

    if quality is None and mp4_abs:
        try:
            import quality_scorer
            quality = quality_scorer.score_video(mp4_abs, brand=brand)
        except Exception as e:
            quality = {"score": None, "pass": None, "error": str(e)}

    manifest = {
        "video_id": video_id or os.path.basename(project_dir.rstrip("/\\")),
        "project_dir": project_dir,
        "created": _now_iso(),
        "engine": engine,
        "variant": {
            "template": template,
            "brand": brand,
            "aspect": aspect,
            "voice": voice,
            "topic": topic,
            "source": source,
            "length_bucket": _length_bucket(dur),
            "hook_style": hook_style,
            "thumbnail_style": thumbnail_style,
        },
        "duration_s": dur,
        "outputs": outputs,
        "quality": {"score": (quality or {}).get("score"), "pass": (quality or {}).get("pass")}
                   if quality else {"score": None, "pass": None},
        "performance": {},   # filled later by analytics_feedback_agent.performance_ingest
    }
    if extra:
        manifest["extra"] = extra

    os.makedirs(project_dir, exist_ok=True)
    with open(os.path.join(project_dir, MANIFEST_NAME), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    # 3-file output aid: a plain narration script.txt for CapCut auto-caption.
    try:
        _write_script_txt(project_dir, outputs.get("srt"))
    except Exception as e:
        print(f"[manifest] script.txt skipped: {e}")
    return manifest


def load(project_dir):
    p = os.path.join(project_dir, MANIFEST_NAME)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def scan(workspace_dir=None):
    """Return all manifests under the workspace (one per produced video)."""
    workspace_dir = workspace_dir or os.path.join(ROOT, "8_WORKSPACE")
    out = []
    for p in glob.glob(os.path.join(workspace_dir, "**", MANIFEST_NAME), recursive=True):
        try:
            with open(p, encoding="utf-8") as f:
                out.append(json.load(f))
        except Exception:
            pass
    return out


def set_performance(project_dir, metrics):
    """Merge real-world metrics into an existing manifest (used by performance_ingest)."""
    m = load(project_dir)
    if not m:
        return None
    m["performance"].update(metrics or {})
    m["performance"]["updated"] = _now_iso()
    with open(os.path.join(project_dir, MANIFEST_NAME), "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=2)
    return m


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Record/inspect a production manifest")
    ap.add_argument("project_dir")
    ap.add_argument("--template"); ap.add_argument("--brand", default="seosona")
    ap.add_argument("--topic"); ap.add_argument("--aspect", default="9:16")
    ap.add_argument("--voice"); ap.add_argument("--source")
    ap.add_argument("--scan", action="store_true", help="scan workspace instead")
    a = ap.parse_args()
    if a.scan:
        print(json.dumps(scan(), ensure_ascii=False, indent=2))
    else:
        m = record(a.project_dir, template=a.template, brand=a.brand, topic=a.topic,
                   aspect=a.aspect, voice=a.voice, source=a.source)
        print(json.dumps(m, ensure_ascii=False, indent=2))
