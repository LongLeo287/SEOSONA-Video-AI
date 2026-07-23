#!/usr/bin/env python
"""reframe_router — auto-vertical crop: 16:9 video -> subject-tracked 9:16 crop keyframes.

author: SEOSONA  ·  place at  <LEGACY_ROOT>/2_SKILLS/srt_maker/reframe_router.py

The V2 seam `@seosona/engines` `reframeAdapter.planReframe(video, targetAspect)` calls
`reframe_router.plan_reframe(video, target_aspect)` and expects on stdout:
    SEOSONA_REFRAME_RESULT:[{"t": <sec>, "x": f, "y": f, "w": f, "h": f}, ...]   (all 0..1 fractions)

Samples the video, detects the subject FACE per sampled frame (OpenCV YuNet DNN — the model
`models/face_detection_yunet_2023mar.onnx` sits next to this script), smooths its centre (EMA), and
emits a moving crop WINDOW of the target aspect that keeps the subject centred — so a horizontal
client clip becomes a vertical reel without decapitating the speaker. Falls back to a centred crop
when no face is found. v1: face-centred + EMA; tune sample_hz / smooth on real footage.

Deps: opencv-python(-headless), numpy (in the legacy venv). Never fabricates — raises on failure so
the V2 seam falls back to a static centre-crop.
"""
import json
import os
import sys

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "face_detection_yunet_2023mar.onnx")


def _target_ratio(target_aspect: str) -> float:
    aw, ah = (float(x) for x in target_aspect.split(":"))
    return aw / ah


def plan_reframe(video_path: str, target_aspect: str = "9:16", sample_hz: float = 2.0, smooth: float = 0.35):
    """Return [{'t','x','y','w','h'}] crop keyframes (0..1 fractions) that follow the subject face."""
    import cv2

    if not os.path.isfile(MODEL_PATH):
        raise RuntimeError(f"YuNet face model not found: {MODEL_PATH}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"could not open video: {video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 1920)
    src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 1080)
    src_ratio = src_w / src_h
    crop_w = min(1.0, _target_ratio(target_aspect) / src_ratio)  # width fraction of the target window
    half = crop_w / 2.0
    step = max(1, int(round(fps / max(0.1, sample_hz))))

    detector = cv2.FaceDetectorYN.create(MODEL_PATH, "", (src_w, src_h), score_threshold=0.6)
    detector.setInputSize((src_w, src_h))

    keyframes = []
    cx = 0.5  # smoothed subject centre-x (fraction); start centred
    idx = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if idx % step == 0:
                _, faces = detector.detect(frame)
                target_cx = cx
                if faces is not None and len(faces) > 0:
                    f = max(faces, key=lambda r: float(r[2]) * float(r[3]))  # biggest face box
                    target_cx = (float(f[0]) + float(f[2]) / 2.0) / src_w
                cx = (1 - smooth) * cx + smooth * target_cx  # EMA toward the subject
                x = min(max(cx - half, 0.0), 1.0 - crop_w)   # clamp so the window stays in-frame
                keyframes.append({"t": round(idx / fps, 3), "x": round(x, 4), "y": 0.0, "w": round(crop_w, 4), "h": 1.0})
            idx += 1
    finally:
        cap.release()

    if not keyframes:  # no frames sampled → one centred keyframe
        keyframes = [{"t": 0.0, "x": round((1 - crop_w) / 2, 4), "y": 0.0, "w": round(crop_w, 4), "h": 1.0}]
    return keyframes


def main() -> None:
    video_path = sys.argv[1]
    target = sys.argv[2] if len(sys.argv) > 2 else "9:16"
    print("SEOSONA_REFRAME_RESULT:" + json.dumps(plan_reframe(video_path, target_aspect=target), ensure_ascii=False))


if __name__ == "__main__":
    main()
