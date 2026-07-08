# -*- coding: utf-8 -*-
"""FRAME SYNTH — the frame kho GROWS ITSELF. When a scene's content fits none of the built-in frames
(`frame_study.CATALOG`), an LLM synthesises a NEW frame (light-brand, seek-safe HTML template), it is
VALIDATED (renders, no JS, no dark, balanced), then REGISTERED into the kho so every future video can use it.

A generated frame = {kind, group, title, when, schema, html} where `html` is a tiny-mustache template:
  {{key}}                         → scalar field (HTML-escaped)
  {{acc}}                         → the scene accent colour
  {{#items}}..{{.field}}..{{/items}} → repeat over data.items (dicts or strings via {{.}})
No <script> is allowed (motion comes from the shared `.ritem` reveal the engine applies to any element with
class `ritem`), so generated frames are automatically seek-safe. native_composer._component falls back here
for any kind it doesn't hard-code; frame_study merges these into the catalog + menu + selfcheck.
"""
import os
import re
import json
import html as _html

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GEN_PATH = os.path.join(ROOT, "7_ASSETS", "frames", "generated_frames.json")

# brand tokens the generator MUST use (light only)
BRAND = {"blue": "#2A5BDA", "coral": "#E2724D", "green": "#16A34A", "amber": "#EAB308",
         "ink": "#0F172A", "muted": "#64748B", "card": "#ffffff", "line": "#E6EAF2", "soft": "#EEF2F8"}


def _load():
    try:
        return json.load(open(GEN_PATH, encoding="utf-8"))
    except Exception:
        return {}


def _save(d):
    os.makedirs(os.path.dirname(GEN_PATH), exist_ok=True)
    json.dump(d, open(GEN_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def kinds():
    return list(_load().keys())


def catalog_entries():
    """Generated frames as frame_study-shaped metadata (so menu + selfcheck include them)."""
    return {k: {"group": v.get("group", "list"), "title": v.get("title", k),
                "when": v.get("when", ""), "schema": v.get("schema", ""), "_generated": True}
            for k, v in _load().items()}


def _esc(s):
    return _html.escape(str(s))


def _fill(tmpl, data, acc):
    """Tiny-mustache fill (safe: values HTML-escaped, leftovers stripped). One {{#items}} repeat + scalars."""
    data = data if isinstance(data, dict) else {}
    def _each(m):
        inner = m.group(1)
        out = ""
        for it in (data.get("items") or [])[:8]:
            row = inner
            if isinstance(it, dict):
                for k2, v2 in it.items():
                    row = row.replace("{{." + k2 + "}}", _esc(v2))
            else:
                row = row.replace("{{.}}", _esc(it))
            row = re.sub(r"\{\{\.[a-z0-9_]+\}\}", "", row)     # drop unfilled item fields
            out += row
        return out
    s = re.sub(r"\{\{#items\}\}(.*?)\{\{/items\}\}", _each, tmpl, flags=re.S)
    s = s.replace("{{acc}}", acc)
    for k2, v2 in data.items():
        if not isinstance(v2, (list, dict)):
            s = s.replace("{{" + k2 + "}}", _esc(v2))
    return re.sub(r"\{\{[#/\.a-z0-9_]+\}\}", "", s)            # strip any leftovers


def render_generated(kind, data, acc):
    """Render a registered generated frame (native_composer._component fallback). None if not found/fails."""
    spec = _load().get(kind)
    if not spec:
        return None
    try:
        out = _fill(spec.get("html", ""), data, acc)
        return out or None
    except Exception:
        return None


_DARK = re.compile(r"background[^;]*:\s*#[0-2][0-9a-fA-F]{2}\b")


def validate(spec, sample):
    """Render-safe + light-brand checks before a generated frame enters the kho. → (ok, reason)."""
    t = str(spec.get("html", "") or "")
    if len(t) < 30 or "class" not in t:
        return False, "template too small / no styling"
    _tl = t.lower()
    # No active content: the frame is PERSISTED and re-rendered by a full browser (Playwright/Chromium),
    # so block ALL event handlers (onerror/onclick/…, not just onload), script/js URIs, and tags that
    # pull or run content (iframe/object/embed/base/meta/link/form). Motion is the shared .ritem reveal.
    if ("<script" in _tl or "javascript:" in _tl or re.search(r"\son\w+\s*=", _tl)
            or re.search(r"<(iframe|object|embed|base|meta|link|form)\b", _tl)):
        return False, "no JS / active content allowed (static seek-safe render only)"
    if "http://" in t or "https://" in t or "url(" in t:
        return False, "no external assets/URLs"
    if _DARK.search(t):
        return False, "dark background — SEOSONA is light-only"
    out = _fill(t, sample or {}, BRAND["blue"])
    if not out or len(out) < 20:
        return False, "renders empty with sample data"
    if out.count("<") != out.count(">"):
        return False, "unbalanced tags"
    return True, "ok"


def register(kind, spec, sample):
    """Validate then persist a generated frame. → (ok, reason)."""
    kind = re.sub(r"[^a-z0-9_]", "", str(kind or "").lower())
    if not kind:
        return False, "bad kind name"
    ok, why = validate(spec, sample)
    if not ok:
        return False, why
    d = _load()
    d[kind] = {"group": spec.get("group", "list"), "title": spec.get("title", kind),
               "when": spec.get("when", ""), "schema": spec.get("schema", ""), "html": spec["html"]}
    _save(d)
    return True, "registered"


_SYS = (
    "Bạn tạo một COMPONENT KHUNG (frame) mới cho video dọc 9:16 thương hiệu SEOSONA — LIGHT MODE. "
    "Chỉ được dùng màu sáng: nền trắng #ffffff/#EEF2F8, chữ #0F172A/#64748B, accent = {{acc}} (biến), xanh lá #16A34A. "
    "TUYỆT ĐỐI KHÔNG nền tối, KHÔNG <script>, KHÔNG url/ảnh ngoài. Chuyển động do engine tự thêm qua class 'ritem' "
    "(mỗi phần tử cần build dần thì thêm class=\"ritem\"). HTML tự chứa style inline hoặc <style>. "
    "Template dùng cú pháp: {{key}} cho trường đơn, {{acc}} cho màu accent, và {{#items}}...{{.text}}...{{/items}} lặp qua data.items. "
    "Trả về JSON THUẦN: {kind (snake_case mới), group (number|chart|compare|list|diagram|dev|media|text|feed|cta), "
    "title (tiếng Việt ngắn), when (khi nào dùng), schema (mô tả data), html (template)}."
)


def grow(desc, sample_data, existing_kinds):
    """Synthesise + validate + register a NEW frame for `desc` when the kho has none. → kind or None.
    LOCAL-FIRST: try local Ollama directly (fast, self-sufficient — no 60s cloud backoff when quota is out);
    the prompt is small so a local model handles it. Falls back to the full cascade only if SEOSONA_GROW_CLOUD=1.
    Best-effort: no LLM / invalid proposal → None (never breaks the pipeline). A grown frame is BANKED, so
    every FUTURE video reuses it with NO LLM."""
    try:
        import llm_engine
    except Exception:
        return None
    user = (f"Nội dung cảnh cần một khung chưa có trong kho: {desc}\n"
            f"Data mẫu: {json.dumps(sample_data, ensure_ascii=False)}\n"
            f"Kho ĐÃ CÓ (đừng trùng): {sorted(existing_kinds)}\nTạo 1 frame MỚI hợp nội dung này.")
    spec = None
    try:                                             # local Ollama first (fast, free)
        raw = llm_engine._try_ollama_json(_SYS, user)
        spec = llm_engine._parse_json_or_none(raw) if raw else None
    except Exception:
        spec = None
    if not (isinstance(spec, dict) and spec.get("html")) and os.getenv("SEOSONA_GROW_CLOUD") == "1":
        try:
            spec = llm_engine.generate_json_from_prompt(_SYS, user)
        except Exception:
            spec = None
    if not isinstance(spec, dict) or not spec.get("kind") or not spec.get("html"):
        return None
    kind = re.sub(r"[^a-z0-9_]", "", str(spec["kind"]).lower())
    if not kind or kind in set(existing_kinds):
        return None
    ok, why = register(kind, spec, sample_data)
    return kind if ok else None


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(f"FRAME SYNTH — {len(_load())} generated frame(s) in the kho: {kinds()}")
