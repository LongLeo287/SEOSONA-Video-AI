# -*- coding: utf-8 -*-
"""Engine #6 — Seedance 2.0: text (+ optional image ref) → photoreal cinematic AI-video clips.

The factory's other engine (talking-head) turns real footage
into a talking head. Seedance is different: it GENERATES cinematic b-roll/scene footage from a text
prompt. `seedance_director.py` authors the prompts (the craft); THIS module runs them through a
Seedance provider and stitches the clips into a reel.

ACCESS-GATED, honestly. Seedance 2.0 is a PAID ByteDance model. Know who you are paying:

  · BytePlus ModelArk / Volcengine — the OFFICIAL FIRST-PARTY ByteDance API (BytePlus = international/
    USD, Volcengine = China/RMB). No reseller margin; needs a ByteDance-cloud account. env ARK_API_KEY
    (+ ARK_SEEDANCE_ENDPOINT). Adapter is a stub (implement the ark client to use it).
  · fal.ai / Replicate — REPUTABLE THIRD-PARTY HOSTS that resell Seedance behind their own API. Legit
    and convenient, but you pay their margin and they see your prompts. env FAL_KEY / REPLICATE_API_TOKEN.
    Model ids are env-overridable (SEEDANCE_FAL_MODEL / SEEDANCE_REPLICATE_MODEL) — CONFIRM the exact
    current id on fal.ai/models or replicate.com/bytedance before adding a key; they change per version.

SECURITY — do NOT buy "Seedance API keys" from unofficial marketplace/reseller sites (e.g. random
"cheap Seedance API" aggregators). They may resell stolen/shared quota, harvest your key, overcharge,
or vanish. Only use the official BytePlus/Volcengine, or fal.ai / Replicate, EACH WITH YOUR OWN account.
This module only ever sends your key to `queue.fal.run` or `api.replicate.com` — nowhere else.

With NO key configured, `make_reel()` degrades to PROMPT-ONLY: it writes the prompts + shotlist and
reports how to enable rendering — it never fakes a render. (The keyless local LTX-Video lane was
REMOVED 2026-07-14 — local generation was too heavy for the fast-production goal; add a paid key
to enable auto-render.)

  python 4_BRAIN/seedance_engine.py --status
  python 4_BRAIN/seedance_engine.py --script beats.json --title "Toby Labs" --out out/reel.mp4
  python 4_BRAIN/seedance_engine.py --idea "a founder demos an AI SEO tool" --out out/clip.mp4
"""
import os
import sys
import json
import time
import argparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (ROOT, os.path.join(ROOT, "4_BRAIN")):
    if p not in sys.path:
        sys.path.insert(0, p)

import seedance_director as director  # the prompt-authoring craft (Task 1)

# Provider config: env var(s) that hold the key + a human label. Order = preference.
_PROVIDERS = [
    ("byteplus",  ("ARK_API_KEY",),                            "BytePlus/Volcengine ModelArk — OFFICIAL first-party (stub)"),
    ("fal",       ("FAL_KEY", "SEEDANCE_FAL_KEY"),            "fal.ai — third-party reseller (seedance-2.0)"),
    ("replicate", ("REPLICATE_API_TOKEN", "SEEDANCE_REPLICATE_TOKEN"), "Replicate — third-party reseller (bytedance/seedance-*)"),
]


def _load_env():
    """Best-effort .env load (env-first) so keys in the repo .env are visible — mirrors the factory."""
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(ROOT, ".env"))
    except Exception:
        # minimal fallback parser so a key in .env still resolves without python-dotenv
        envp = os.path.join(ROOT, ".env")
        if os.path.exists(envp):
            for ln in open(envp, encoding="utf-8", errors="ignore"):
                ln = ln.strip()
                if ln and not ln.startswith("#") and "=" in ln:
                    k, v = ln.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _key_for(env_names):
    for n in env_names:
        v = os.environ.get(n)
        if v:
            return v
    # also try the factory's credentials_manager (platform=seedance)
    try:
        sys.path.insert(0, os.path.join(ROOT, "1_CONFIG"))
        from credentials_manager import creds
        v = creds.get("seedance", "api_key")
        if v:
            return v
    except Exception:
        pass
    return None


def available():
    """List of {provider,label} runnable now (empty = prompt-only mode). Paid providers only —
    the keyless local LTX-Video lane was REMOVED 2026-07-14 (user decision: local gen too heavy
    for the fast-production goal; paid API to be enabled later by adding a key)."""
    _load_env()
    out = []
    for name, envs, label in _PROVIDERS:
        if name == "byteplus":
            continue                       # official but adapter is a stub → not runnable, don't auto-pick
        if _key_for(envs):
            out.append({"provider": name, "label": label, "env": envs[0]})
    return out


def status():
    """Human status string for --status / logging."""
    av = available()
    lines = ["[seedance_engine] Engine #6 — Seedance 2.0 provider status:"]
    for name, envs, label in _PROVIDERS:
        on = any(os.environ.get(e) for e in envs) or _key_for(envs) is not None
        mark = "READY" if on else "no key"
        lines.append(f"  · {name:9} [{mark:6}] {label}  (set env {envs[0]})")
    lines.append(f"  => {'render ENABLED via ' + av[0]['provider'] if av else 'PROMPT-ONLY — author prompts, run them manually in Seedance (paid API keys enable auto-render)'}")
    return "\n".join(lines)


# ───────────────────────────── provider adapters ─────────────────────────────

def _requests():
    try:
        import requests
        return requests
    except Exception as e:
        raise RuntimeError(f"the 'requests' package is required for Seedance generation ({e})")


def _fal_generate(prompt, out_mp4, *, aspect, duration, resolution, image_url, key, timeout):
    rq = _requests()
    # Model path is env-configurable — the DEFAULT targets Seedance 2.0 (the older 1.0 id was
    # `fal-ai/bytedance/seedance/v1/pro`). ALWAYS confirm the exact current id at fal.ai/models before
    # adding a key — fal renames paths across versions. fal.ai is a reputable THIRD-PARTY host (reseller),
    # not ByteDance first-party.
    model = os.environ.get("SEEDANCE_FAL_MODEL", "fal-ai/bytedance/seedance-2.0")
    base = f"https://queue.fal.run/{model}"
    url = f"{base}/text-to-video"
    body = {"prompt": prompt, "aspect_ratio": aspect, "resolution": resolution, "duration": str(duration)}
    if image_url:
        url = f"{base}/image-to-video"
        body["image_url"] = image_url
    hdr = {"Authorization": f"Key {key}", "Content-Type": "application/json"}
    r = rq.post(url, json=body, headers=hdr, timeout=60); r.raise_for_status()
    j = r.json()
    status_url = j.get("status_url") or j.get("response_url")
    resp_url = j.get("response_url")
    deadline = time.monotonic() + timeout
    while status_url and time.monotonic() < deadline:
        time.sleep(4)
        s = rq.get(status_url, headers=hdr, timeout=30).json()
        if s.get("status") in ("COMPLETED", "OK"):
            break
        if s.get("status") in ("FAILED", "ERROR"):
            raise RuntimeError(f"fal generation failed: {s}")
    final = rq.get(resp_url, headers=hdr, timeout=30).json() if resp_url else s
    vid = (((final.get("video") or {}).get("url")) if isinstance(final.get("video"), dict) else final.get("video"))
    if not vid:
        raise RuntimeError(f"fal returned no video url: {final}")
    return _download(vid, out_mp4, timeout)


def _replicate_generate(prompt, out_mp4, *, aspect, duration, resolution, image_url, key, timeout):
    rq = _requests()
    # env-configurable model — default is Seedance 1.0 Pro (confirm/point to a 2.0 model at
    # replicate.com/bytedance when available). Replicate is a reputable THIRD-PARTY host (reseller).
    model = os.environ.get("SEEDANCE_REPLICATE_MODEL", "bytedance/seedance-1-pro")
    url = f"https://api.replicate.com/v1/models/{model}/predictions"
    inp = {"prompt": prompt, "aspect_ratio": aspect, "duration": int(duration), "resolution": resolution}
    if image_url:
        inp["image"] = image_url
    hdr = {"Authorization": f"Bearer {key}", "Content-Type": "application/json", "Prefer": "wait"}
    r = rq.post(url, json={"input": inp}, headers=hdr, timeout=60); r.raise_for_status()
    j = r.json()
    get_url = (j.get("urls") or {}).get("get")
    deadline = time.monotonic() + timeout
    while j.get("status") not in ("succeeded", "failed", "canceled") and get_url and time.monotonic() < deadline:
        time.sleep(4)
        j = rq.get(get_url, headers=hdr, timeout=30).json()
    if j.get("status") != "succeeded":
        raise RuntimeError(f"replicate status={j.get('status')}: {j.get('error')}")
    out = j.get("output")
    vid = out[0] if isinstance(out, list) else out
    if not vid:
        raise RuntimeError(f"replicate returned no output: {j}")
    return _download(vid, out_mp4, timeout)


def _byteplus_generate(*a, **k):
    raise RuntimeError(
        "BytePlus ModelArk (Doubao-Seedance) adapter is a stub — it needs ARK_API_KEY + "
        "ARK_SEEDANCE_ENDPOINT and the official ark SDK. Use fal.ai or Replicate for now, "
        "or implement the ark client here.")


# (the keyless local LTX-Video adapter was REMOVED 2026-07-14 — local gen too heavy for the
#  fast-production goal; paid providers below are the render path once a key is added)
_ADAPTERS = {"fal": _fal_generate, "replicate": _replicate_generate,
             "byteplus": _byteplus_generate}


def _download(url, out_mp4, timeout):
    rq = _requests()
    os.makedirs(os.path.dirname(os.path.abspath(out_mp4)) or ".", exist_ok=True)
    with rq.get(url, stream=True, timeout=min(timeout, 120)) as r:
        r.raise_for_status()
        with open(out_mp4, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
    return out_mp4


# ───────────────────────────── public generation API ─────────────────────────────

def generate(prompt, out_mp4, *, aspect="16:9", duration=5, resolution="720p",
             image_url=None, provider=None, timeout=600):
    """Generate ONE Seedance clip from a prompt. Raises a clear RuntimeError if no key is configured."""
    av = available()
    if not av:
        raise RuntimeError(
            "No Seedance provider key configured. Set one of: FAL_KEY (fal.ai) / REPLICATE_API_TOKEN "
            "(Replicate) / ARK_API_KEY (BytePlus) in the environment or repo .env, then retry. "
            "Until then use PROMPT-ONLY mode (make_reel writes prompts + shotlist).")
    chosen = provider or av[0]["provider"]
    envs = next((e for n, e, _ in _PROVIDERS if n == chosen), None)
    key = _key_for(envs) if envs else None
    if not key:
        raise RuntimeError(f"provider '{chosen}' has no key (set env {envs[0] if envs else '?'})")
    print(f"[seedance_engine] generating via {chosen} · {aspect} · {duration}s · {resolution}")
    return _ADAPTERS[chosen](prompt, out_mp4, aspect=aspect, duration=duration,
                             resolution=resolution, image_url=image_url, key=key, timeout=timeout)


def _ffmpeg():
    try:
        import native_composer as nc
        return nc._ffmpeg_bin()
    except Exception:
        p = os.path.join(ROOT, "node_modules", "ffmpeg-static", "ffmpeg.exe")
        return p if os.path.exists(p) else "ffmpeg"


def _concat(clips, out_mp4):
    """Concat rendered clips into one reel (ffmpeg concat demuxer)."""
    import subprocess, tempfile
    lst = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    for c in clips:
        lst.write(f"file '{os.path.abspath(c)}'\n")
    lst.close()
    cmd = [_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
           "-i", lst.name, "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", out_mp4]
    subprocess.run(cmd, check=True, timeout=600)
    os.unlink(lst.name)
    return out_mp4


def make_reel(title, beats, out_mp4, *, aspect="16:9", resolution="720p", provider=None):
    """Author prompts (director) → render each clip (if a key) → concat into a reel.

    NO KEY → PROMPT-ONLY: writes <out>.shotlist.html + <out>.prompts.txt next to out_mp4 and returns
    a report dict with ``rendered=False`` and the exact env var to set. Honest, never a fake mp4.
    """
    _load_env()
    doc = director.author_from_script(title, beats, aspect=aspect)
    scenes = doc["scenes"]
    base = os.path.splitext(os.path.abspath(out_mp4))[0]
    os.makedirs(os.path.dirname(base) or ".", exist_ok=True)
    html_path, txt_path = director.author_and_write(title, beats, base + ".shotlist.html", aspect=aspect)

    av = available()
    if not av:
        print(status())
        return {"rendered": False, "reason": "no_provider_key", "scenes": len(scenes),
                "shotlist_html": html_path, "prompts_txt": txt_path,
                "hint": "Set FAL_KEY or REPLICATE_API_TOKEN then re-run to render."}

    clips, work = [], base + "_clips"
    os.makedirs(work, exist_ok=True)
    for sc in scenes:
        total = float(sc.get("duration", len(sc.get("shots", [])) * 5 or 15))
        for k, sub in enumerate(director.split_long(sc, total) if total > 15 else [sc]):
            lbl = f"{sc.get('label','')}{chr(97+k)}" if total > 15 else sc.get("label", "")
            # paid Seedance wants the full structured prompt (build_prose stays in the director
            # for any future provider that prefers natural prose).
            prompt = director.build_prompt(sub)
            clip = os.path.join(work, f"scene_{lbl}.mp4")
            dur = int(sub.get("clip_seconds", 5))
            generate(prompt, clip, aspect=aspect, duration=dur,
                     resolution=resolution, provider=provider)
            clips.append(clip)
    reel = _concat(clips, out_mp4) if len(clips) > 1 else (clips and __import__("shutil").copy(clips[0], out_mp4))
    print(f"[seedance_engine] reel: {len(clips)} clip(s) -> {out_mp4}")
    return {"rendered": True, "provider": av[0]["provider"], "clips": len(clips),
            "out": out_mp4, "shotlist_html": html_path, "prompts_txt": txt_path}


def main():
    ap = argparse.ArgumentParser(description="Engine #6 — Seedance 2.0 (text -> cinematic AI video)")
    ap.add_argument("--status", action="store_true", help="show provider key status and exit")
    ap.add_argument("--idea", help="one-line idea -> a single clip (or prompt-only if no key)")
    ap.add_argument("--script", help="beats.json -> a full reel")
    ap.add_argument("--title", default="Untitled")
    ap.add_argument("--out", help="output reel/clip .mp4")
    ap.add_argument("--aspect", default="16:9", choices=["16:9", "9:16", "1:1"])
    ap.add_argument("--resolution", default="1080p")
    ap.add_argument("--provider", choices=["fal", "replicate", "byteplus"])
    a = ap.parse_args()

    if a.status or (not a.idea and not a.script):
        print(status()); return
    beats = json.load(open(a.script, encoding="utf-8")) if a.script else [a.idea]
    out = a.out or os.path.join(os.getcwd(), "seedance_out.mp4")
    rep = make_reel(a.title, beats, out, aspect=a.aspect, resolution=a.resolution, provider=a.provider)
    print(json.dumps(rep, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
