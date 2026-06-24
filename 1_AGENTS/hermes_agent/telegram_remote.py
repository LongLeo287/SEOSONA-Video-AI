"""
Telegram Remote — control the SEOSONA Video factory from your phone.

Hermes is the remote brain: it accepts commands over Telegram, triggers production,
reports status, and sends finished products (or a Google Drive link) back to you.

Auth/security:
- Token + allowed chat from 1_CONFIG credentials (telegram.bot_token / telegram.chat_id).
- The bot ONLY answers the configured chat_id. Every other sender is ignored.
- No extra pip deps required — uses the raw Telegram Bot API over HTTP (long polling).

Run:  python 1_AGENTS/hermes_agent/telegram_remote.py
(needs telegram.bot_token + telegram.chat_id configured — see 1_CONFIG/README.md)

Commands:
  /help                 show commands
  /status               last job + recent products
  /list                 list finished products in 8_WORKSPACE
  /news <topic>         produce a Vietnamese tech-news video on <topic>
  /publish <name> <d>   publish product <name> to destinations d (e.g. google_drive,youtube)
  /review <text>        ask Hermes to review a script snippet
"""
import os
import sys
import json
import time
import threading
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "1_CONFIG"))
sys.path.insert(0, str(_ROOT / "1_AGENTS"))

try:
    from credentials_manager import creds
except Exception:
    creds = None

_API = "https://api.telegram.org/bot{token}/{method}"
_JOBS = {"last": None}  # tiny in-memory job state


# ── Telegram Bot API helpers (stdlib only) ──────────────────────────
def _call(token, method, params=None):
    url = _API.format(token=token, method=method)
    data = urllib.parse.urlencode(params or {}).encode() if params else None
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=70) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _send(token, chat_id, text):
    return _call(token, "sendMessage", {"chat_id": chat_id, "text": text[:4000]})


def _send_video(token, chat_id, video_path, caption=""):
    """Send a local mp4 via multipart upload."""
    if not os.path.exists(video_path):
        return _send(token, chat_id, f"(video not found: {video_path})")
    boundary = "----SEOSONABoundary"
    with open(video_path, "rb") as f:
        body = f.read()
    parts = []
    for k, v in {"chat_id": str(chat_id), "caption": caption[:1000]}.items():
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    fname = os.path.basename(video_path)
    parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"video\"; filename=\"{fname}\"\r\n"
        f"Content-Type: video/mp4\r\n\r\n".encode() + body + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    payload = b"".join(parts)
    url = _API.format(token=token, method="sendVideo")
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ── Command handlers ────────────────────────────────────────────────
def _list_products():
    ws = _ROOT / "8_WORKSPACE"
    if not ws.exists():
        return []
    out = []
    for p in ws.iterdir():
        if p.is_dir() and not p.name.startswith("_"):
            mp4 = list(p.glob("*.mp4"))
            if mp4:
                out.append((p.name, str(mp4[0])))
    return out


def _produce_news(token, chat_id, topic):
    """Run the news workflow in a background thread; notify on completion."""
    _JOBS["last"] = {"type": "news", "topic": topic, "status": "running", "started": time.time()}
    _send(token, chat_id, f"🎬 Bắt đầu sản xuất video tin tức: “{topic}”. Sẽ báo khi xong…")

    def _work():
        try:
            proc = subprocess.run(
                [sys.executable, str(_ROOT / "scripts" / "workflow_video_news.py"), topic],
                cwd=str(_ROOT), capture_output=True, text=True, timeout=3600,
            )
            ok = proc.returncode == 0
            _JOBS["last"]["status"] = "done" if ok else "failed"
            if ok:
                prods = _list_products()
                if prods:
                    name, mp4 = prods[-1]
                    _send(token, chat_id, f"✅ Xong: {name}. Đang gửi video…")
                    _send_video(token, chat_id, mp4, caption=f"SEOSONA • {topic}")
                else:
                    _send(token, chat_id, "✅ Pipeline xong nhưng không tìm thấy file mp4.")
            else:
                _send(token, chat_id, f"❌ Sản xuất lỗi.\n{(proc.stderr or '')[-500:]}")
        except Exception as e:
            _JOBS["last"]["status"] = "failed"
            _send(token, chat_id, f"❌ Lỗi: {e}")

    threading.Thread(target=_work, daemon=True).start()


def _publish_product(token, chat_id, name, dests):
    prods = dict(_list_products())
    if name not in prods:
        return _send(token, chat_id, f"Không thấy sản phẩm “{name}”. Dùng /list để xem.")
    try:
        from publisher_agent import publish
        report = publish({"video": prods[name], "title": name}, destinations=dests)
        lines = [f"{d}: {r.get('status')}" + (f" → {r.get('link')}" if r.get("link") else "")
                 for d, r in report.items()]
        _send(token, chat_id, "📤 Kết quả publish:\n" + "\n".join(lines))
    except Exception as e:
        _send(token, chat_id, f"Publish lỗi: {e}")


def _handle(token, chat_id, text):
    text = (text or "").strip()
    if text in ("/start", "/help"):
        return _send(token, chat_id,
                     "SEOSONA Video — remote\n"
                     "/news <chủ đề> — sản xuất video tin tức\n"
                     "/trend [make] — lấy trend mới nhất (RSS); 'make' để sản xuất luôn\n"
                     "/list — sản phẩm đã có\n"
                     "/status — trạng thái job\n"
                     "/publish <tên> <đích> — vd: /publish MyProj google_drive,youtube\n"
                     "/review <text> — Hermes review kịch bản")
    if text.startswith("/status"):
        return _send(token, chat_id, f"Job gần nhất: {json.dumps(_JOBS['last'], ensure_ascii=False)}")
    if text.startswith("/list"):
        prods = _list_products()
        return _send(token, chat_id, "Sản phẩm:\n" + ("\n".join(n for n, _ in prods) or "(trống)"))
    if text.startswith("/news"):
        topic = text[len("/news"):].strip()
        return _produce_news(token, chat_id, topic) if topic else _send(token, chat_id, "Cú pháp: /news <chủ đề>")
    if text.startswith("/publish"):
        parts = text.split()
        if len(parts) >= 3:
            return _publish_product(token, chat_id, parts[1], parts[2].split(","))
        return _send(token, chat_id, "Cú pháp: /publish <tên> <đích1,đích2>")
    if text.startswith("/trend"):
        try:
            from trend_jacking_agent.trend_tracker import fetch_latest_trend
            topic = fetch_latest_trend()
            if "make" in text:
                _produce_news(token, chat_id, topic)
                return
            return _send(token, chat_id, f"🔥 Trend mới nhất:\n{topic}\n\n→ /news {topic}\nhoặc /trend make để sản xuất ngay.")
        except Exception as e:
            return _send(token, chat_id, f"Trend lỗi: {e}")
    if text.startswith("/review"):
        snippet = text[len("/review"):].strip()
        try:
            from hermes_agent.hermes_local import ask_local_hermes
            return _send(token, chat_id, ask_local_hermes(snippet))
        except Exception as e:
            return _send(token, chat_id, f"Hermes lỗi: {e}")
    return _send(token, chat_id, "Lệnh không rõ. /help để xem danh sách.")


# ── Long-polling loop ───────────────────────────────────────────────
def run():
    if not creds or not creds.has("telegram", "bot_token", "chat_id"):
        print("[telegram] not configured — set telegram.bot_token + telegram.chat_id "
              "(see 1_CONFIG/README.md).")
        return
    token = creds.get("telegram", "bot_token")
    allowed = str(creds.get("telegram", "chat_id"))
    print(f"[telegram] Hermes remote online. Listening for chat_id={allowed}.")
    _send(token, allowed, "🤖 SEOSONA Video remote đã online. /help để bắt đầu.")
    offset = None
    while True:
        resp = _call(token, "getUpdates", {"timeout": 60, "offset": offset} if offset else {"timeout": 60})
        if not resp.get("ok"):
            time.sleep(3)
            continue
        for upd in resp.get("result", []):
            offset = upd["update_id"] + 1
            msg = upd.get("message") or upd.get("edited_message")
            if not msg:
                continue
            sender = str(msg.get("chat", {}).get("id"))
            if sender != allowed:          # security: only the configured chat
                continue
            _handle(token, allowed, msg.get("text", ""))


if __name__ == "__main__":
    run()
