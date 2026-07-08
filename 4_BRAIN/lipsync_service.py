"""Unified lip-sync service (HeyGen-shaped) — one API over BOTH avatar types.

Modeled on HeyGen's lipsync API (developers.heygen.com): a job has a status lifecycle
(pending -> running -> completed | failed) and, when done, a video + an SRT caption. Two
quality modes trade latency for fidelity, exactly like HeyGen's speed vs precision.

  avatar_type = "expert"  -> MuseTalk (Engine #3b): real photo/video, mouth-inpaint lip-sync.
  avatar_type = "mascot"  -> Rhubarb (Engine #4): 2D cartoon viseme mouth.
  mode        = "speed"   -> fast draft   |  "precision" -> higher fidelity (expert: fp32 + speech-enhance).

Each engine runs in its OWN interpreter (MuseTalk in .venv-musetalk, mascot in base python) via
subprocess, so this orchestrator stays dependency-light. Jobs persist as JSON so a caller can poll
list()/get() like HeyGen's List Lipsyncs. Expert jobs are auto-QC'd (scripts/lipsync_qc.py) and the
score is attached to the job.

  from lipsync_service import create, get, list_jobs
  job = create(source="expert.png", audio="voice.mp3", avatar_type="expert", mode="precision")

CLI:
  python 4_BRAIN/lipsync_service.py --source face.png --audio voice.mp3 --type expert --mode precision
  python 4_BRAIN/lipsync_service.py --list
"""
import argparse
import json
import os
import subprocess
import time
import uuid

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JOBS_DIR = os.path.join(ROOT, "8_WORKSPACE", "lipsync_jobs")
MUSETALK_PY = os.path.join(ROOT, "2_KNOWLEDGE", "external_toolkits", ".venv-musetalk", "Scripts", "python.exe")
LIPSYNC_MT = os.path.join(ROOT, "scripts", "lipsync_musetalk.py")
LIPSYNC_QC = os.path.join(ROOT, "scripts", "lipsync_qc.py")
MASCOT = os.path.join(ROOT, "scripts", "mascot_talk.py")

STATUS = ("pending", "running", "completed", "failed")


def _ffprobe_duration(path):
    ff = os.path.join(ROOT, "node_modules", "ffmpeg-static", "ffprobe.exe")
    ff = ff if os.path.exists(ff) else "ffprobe"
    try:
        out = subprocess.run([ff, "-v", "error", "-show_entries", "format=duration",
                              "-of", "default=nk=1:nw=1", path], capture_output=True, text=True, timeout=30)
        return round(float(out.stdout.strip()), 2)
    except Exception:
        return None


def _write(job):
    os.makedirs(JOBS_DIR, exist_ok=True)
    with open(os.path.join(JOBS_DIR, f"{job['id']}.json"), "w", encoding="utf-8") as f:
        json.dump(job, f, ensure_ascii=False, indent=2)
    return job


def _srt_from_transcript(transcript, duration, out_srt, max_chars=42):
    """Cheap segment-level SRT: split transcript into caption-sized chunks spread across the clip.
    (Word-accurate timing would need ASR alignment; this is the HeyGen 'caption_url' equivalent for a
    known TTS script.) Returns out_srt or None."""
    if not transcript or not duration:
        return None
    words, lines, cur = transcript.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > max_chars and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    if not lines:
        return None
    per = duration / len(lines)

    def ts(t):
        h, rem = divmod(t, 3600); m, s = divmod(rem, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s - int(s)) * 1000):03d}"
    with open(out_srt, "w", encoding="utf-8") as f:
        for i, ln in enumerate(lines):
            f.write(f"{i+1}\n{ts(i*per)} --> {ts((i+1)*per)}\n{ln}\n\n")
    return out_srt


def create(source, audio, *, avatar_type="expert", mode="speed", title=None,
           transcript=None, qc=True, callback_id=None):
    """Create + run a lip-sync job. Returns the completed (or failed) job dict."""
    jid = uuid.uuid4().hex[:12]
    out_dir = os.path.join(JOBS_DIR, jid)
    os.makedirs(out_dir, exist_ok=True)
    out_mp4 = os.path.join(out_dir, "output.mp4")
    job = {
        "id": jid, "status": "pending", "title": title or os.path.basename(str(source)),
        "avatar_type": avatar_type, "mode": mode, "duration": None,
        "video_url": None, "caption_url": None, "qc": None,
        "callback_id": callback_id, "created_at": int(time.time()), "failure_message": None,
    }
    _write(job)

    job["status"] = "running"; _write(job)
    try:
        if avatar_type == "expert":
            if not os.path.exists(MUSETALK_PY):
                raise RuntimeError("MuseTalk venv missing — run the Engine #3b setup")
            cmd = [MUSETALK_PY, LIPSYNC_MT, "--face", os.path.abspath(source),
                   "--audio", os.path.abspath(audio), "--out", out_mp4, "--mode", mode]
        elif avatar_type == "mascot":
            # mascot_talk needs Pillow+numpy; the MuseTalk venv has both, so reuse it (no base-env install)
            py = MUSETALK_PY if os.path.exists(MUSETALK_PY) else "python"
            cmd = [py, MASCOT, "--audio", os.path.abspath(audio), "--out", out_mp4]
            if source:
                cmd += ["--image", os.path.abspath(source)]
        else:
            raise ValueError(f"unknown avatar_type: {avatar_type}")

        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        ff = os.path.join(ROOT, "node_modules", "ffmpeg-static")
        env["PATH"] = ff + os.pathsep + env.get("PATH", "")
        proc = subprocess.run(cmd, env=env, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=3600)
        if proc.returncode != 0 or not os.path.exists(out_mp4):
            tail = ((proc.stdout or "") + (proc.stderr or "")).strip().splitlines()[-15:]
            raise RuntimeError("engine failed:\n" + "\n".join(tail))

        job["duration"] = _ffprobe_duration(out_mp4)
        job["video_url"] = out_mp4
        srt = _srt_from_transcript(transcript, job["duration"], os.path.join(out_dir, "output.srt"))
        job["caption_url"] = srt

        if qc and avatar_type == "expert" and os.path.exists(LIPSYNC_QC):
            try:
                q = subprocess.run([MUSETALK_PY, LIPSYNC_QC, "--audio", os.path.abspath(audio),
                                    "--video", out_mp4], env=env, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=600)
                # QC prints a JSON verdict on stdout (last json object)
                txt = q.stdout or ""
                s = txt.rfind("{")
                if s != -1:
                    job["qc"] = json.loads(txt[s:])
            except Exception as e:
                job["qc"] = {"error": str(e)[:200]}

        job["status"] = "completed"
    except Exception as e:
        job["status"] = "failed"
        job["failure_message"] = str(e)[:500]
    return _write(job)


def get(job_id):
    p = os.path.join(JOBS_DIR, f"{job_id}.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def list_jobs(limit=50):
    if not os.path.isdir(JOBS_DIR):
        return []
    js = []
    for fn in os.listdir(JOBS_DIR):
        if fn.endswith(".json"):
            try:
                js.append(json.load(open(os.path.join(JOBS_DIR, fn), encoding="utf-8")))
            except Exception:
                pass
    js.sort(key=lambda j: j.get("created_at", 0), reverse=True)
    return js[:limit]


def main():
    ap = argparse.ArgumentParser(description="Unified lip-sync service (expert=MuseTalk / mascot=Rhubarb)")
    ap.add_argument("--source", help="face image/video (expert) or mascot PNG")
    ap.add_argument("--audio")
    ap.add_argument("--type", choices=["expert", "mascot"], default="expert", dest="avatar_type")
    ap.add_argument("--mode", choices=["speed", "precision"], default="speed")
    ap.add_argument("--title")
    ap.add_argument("--transcript", help="script text (voiced) → generates the SRT caption")
    ap.add_argument("--no-qc", dest="qc", action="store_false")
    ap.add_argument("--list", action="store_true", help="list jobs and exit")
    ap.add_argument("--get", help="print one job by id and exit")
    a = ap.parse_args()
    if a.list:
        print(json.dumps(list_jobs(), ensure_ascii=False, indent=2)); return 0
    if a.get:
        print(json.dumps(get(a.get), ensure_ascii=False, indent=2)); return 0
    if not a.audio:
        ap.error("--audio is required to create a job")
    if a.avatar_type == "expert" and not a.source:
        ap.error("--source (face image/video) is required for an expert job")
    job = create(a.source, a.audio, avatar_type=a.avatar_type, mode=a.mode,
                 title=a.title, transcript=a.transcript, qc=a.qc)
    print(json.dumps(job, ensure_ascii=False, indent=2))
    return 0 if job["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
