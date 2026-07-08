"""Lip-sync QC — validate a MuseTalk (Engine #3b) clip against an INDEPENDENT viseme timeline.

MuseTalk inpaints lips but never checks itself; a bad crop / silent audio / frozen mouth can pass
silently. Rhubarb (Engine #4's tool, MIT, CPU-only, language-independent phonetic recognizer) gives
a second opinion: the mouth OPENNESS the audio implies, per time. We then measure the ACTUAL mouth
aperture in the rendered video with MediaPipe (a dependency MuseTalk already ships) and check the two
track each other. Catches desync + frozen-mouth failures automatically -> feeds the eval flywheel.

Run in the MuseTalk venv (has cv2 + mediapipe):
  2_KNOWLEDGE/external_toolkits/.venv-musetalk/Scripts/python.exe scripts/lipsync_qc.py --audio v.wav --video clip.mp4
Prints a JSON verdict; exit 0 = PASS, 1 = FAIL.
"""
import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RHUBARB = os.path.join(ROOT, "2_KNOWLEDGE", "external_toolkits", "rhubarb", "rhubarb.exe")

# Rhubarb Preston-Blair shapes -> approximate mouth OPENNESS [0..1] (A/X closed, D widest).
_OPENNESS = {"A": 0.0, "X": 0.0, "B": 0.30, "G": 0.30, "F": 0.35,
             "E": 0.50, "H": 0.50, "C": 0.65, "D": 1.0}
_LIP_TOP, _LIP_BOT = 13, 14          # MediaPipe inner-lip landmarks
_FACE_TOP, _FACE_BOT = 10, 152       # forehead top / chin — for scale-invariant normalisation


def _ffmpeg():
    p = os.path.join(ROOT, "node_modules", "ffmpeg-static", "ffmpeg.exe")
    return p if os.path.exists(p) else "ffmpeg"


def _rhubarb_openness(audio, work):
    """(times[], openness[]) sampled from Rhubarb's viseme cues."""
    wav = os.path.join(work, "qc_in.wav")
    subprocess.run([_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
                    "-i", audio, "-ar", "16000", "-ac", "1", wav], check=True)
    out = os.path.join(work, "qc_visemes.json")
    subprocess.run([RHUBARB, "-r", "phonetic", "-f", "json", "-o", out, wav], check=True)
    cues = json.load(open(out, encoding="utf-8"))["mouthCues"]

    def at(t):
        for c in cues:
            if c["start"] <= t < c["end"]:
                return _OPENNESS.get(c["value"], 0.0)
        return 0.0
    return at


def _measure_apertures(video, sample_hz=10.0):
    """Measure normalised mouth aperture per sampled frame -> (times[], apertures[], face_hit_rate)."""
    import cv2
    import mediapipe as mp
    fm = mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1,
                                         refine_landmarks=False, min_detection_confidence=0.5)
    cap = cv2.VideoCapture(video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    step = max(1, int(round(fps / sample_hz)))
    times, aps, faces, total = [], [], 0, 0
    i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if i % step == 0:
            total += 1
            res = fm.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if res.multi_face_landmarks:
                faces += 1
                lm = res.multi_face_landmarks[0].landmark
                h = frame.shape[0]
                face_h = abs(lm[_FACE_BOT].y - lm[_FACE_TOP].y) * h or 1.0
                mouth = abs(lm[_LIP_BOT].y - lm[_LIP_TOP].y) * h
                times.append(i / fps)
                aps.append(mouth / face_h)
        i += 1
    cap.release()
    hit = faces / total if total else 0.0
    return times, aps, hit


def _pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return 0.0
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs) ** 0.5
    vy = sum((y - my) ** 2 for y in ys) ** 0.5
    return cov / (vx * vy) if vx and vy else 0.0


def qc(audio, video, work=None):
    work = work or os.path.join(os.path.dirname(os.path.abspath(video)) or ".", "_qc")
    os.makedirs(work, exist_ok=True)
    open_at = _rhubarb_openness(os.path.abspath(audio), work)
    times, aps, face_hit = _measure_apertures(os.path.abspath(video))
    expected = [open_at(t) for t in times]
    corr = _pearson(expected, aps)
    # aperture spread — near-zero variance => frozen/near-still mouth (a classic MuseTalk failure)
    spread = (max(aps) - min(aps)) if aps else 0.0
    verdict = {
        "frames_sampled": len(times),
        "face_detect_rate": round(face_hit, 3),
        "openness_corr": round(corr, 3),     # want > 0; calibrated band: matched ~0.25-0.33 vs
                                              # mismatched ~0.14 (Rhubarb-VN phonetics are approximate)
        "aperture_spread": round(spread, 4),  # want > ~0.01 (mouth actually moves)
        "pass": bool(corr >= 0.20 and spread >= 0.008 and face_hit >= 0.6),
    }
    reasons = []
    if face_hit < 0.6:
        reasons.append("face rarely detected in output (crop/render issue)")
    if spread < 0.008:
        reasons.append("mouth barely moves (frozen-mouth / silent-audio)")
    if corr < 0.20:
        reasons.append("mouth motion does not track the audio (possible desync)")
    verdict["reasons"] = reasons
    return verdict


def main():
    ap = argparse.ArgumentParser(description="QC a MuseTalk lip-sync clip vs a Rhubarb viseme timeline")
    ap.add_argument("--audio", required=True)
    ap.add_argument("--video", required=True)
    a = ap.parse_args()
    v = qc(a.audio, a.video)
    print(json.dumps(v, ensure_ascii=False, indent=2))
    return 0 if v["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
