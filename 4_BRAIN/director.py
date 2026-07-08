# -*- coding: utf-8 -*-
"""SEOSONA Director — the stage BETWEEN scriptwriter and factory (user's 5-role pipeline:
thu-thập → viết-kịch-bản → ĐẠO DIỄN → nhà-máy → kiểm-duyệt).

The scriptwriter decides WHAT each scene says; the DIRECTOR decides HOW it is shown — the
demonstrative MOTION and the action-matched SFX per scene — and writes that into the scene spec
so the factory (native_composer) renders EXACTLY the directed plan instead of a generic default.

`direct(scenes, segments, gh)` annotates each scene in place with:
  sc["direction"] = {"motion": <how it animates>, "sfx": <action SFX>, "why": <content cue>}
  sc["fx"]["sfx"] = <SFX key>   # the hook native_composer._sfx_cues already reads (writer override)
and returns a printable SHOT LIST (bảng phân cảnh) for logging / QC.

Deterministic + dependency-free: it reads the component the archetype chose + the scene's content
and picks the treatment. Motions themselves live in native_composer (count-up, chart-grow, terminal
typing, mockup Ken Burns, list reveal); the director's job is to make the CHOICE explicit + author
the SFX intent so nothing is left to a generic fallback. An LLM director (opt-in) refines icon+chips.
"""
import re, os, json as _json

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _plan_transition(kind, idx, seed):
    """The director's content-aware TRANSITION choice per scene (so it, not a render-time default, holds
    the plan). Mirrors effect_library's fit-pool + per-video rotation. Returns a valid TRANSITIONS name."""
    try:
        import effect_library as _el
        klass = _el._KIND_CLASS.get(kind or "", "")
        pool = _el._TRANSITION_FIT.get(klass, _el.TRANSITION_ORDER)
        return pool[(int(seed) + idx) % len(pool)]
    except Exception:
        return None


def _plan_lottie(text):
    """A CONTENT-MATCHED lottie animation (element_maker concept→anim aliases) when the scene's meaning
    clearly calls for one (thành công/chiến thắng/ý tưởng/biểu đồ/tiền/thông báo…). None otherwise —
    real relevance ('data thật'), not random decoration. Space-padded match → no VN substring collision."""
    try:
        import sys as _sys
        _emd = os.path.join(_ROOT, "2_SKILLS", "element_maker")
        if _emd not in _sys.path:
            _sys.path.insert(0, _emd)
        import element_maker as _em
        low = " " + re.sub(r"\s+", " ", (text or "").lower()) + " "
        for cue, anim in _em.LOTTIE_ALIASES.items():
            if f" {cue} " in low:
                return anim
    except Exception:
        pass
    return None


def _plan_accent(kind, i, n, seed):
    """A seek-safe decorative EFFECT accent (effect_library.EFFECTS) on high-impact scenes — hook, CTA,
    and every 3rd beat — so motion never goes flat. Sparse by design. Returns an EFFECTS name or None."""
    try:
        import effect_library as _el
        names = list(_el.EFFECTS)
        if not names:
            return None
        if i == 0 or i == n - 1 or i % 3 == 0:
            return names[(int(seed) + i) % len(names)]
    except Exception:
        pass
    return None


def _lucide_names():
    try:
        return list(_json.load(open(os.path.join(_ROOT, "7_ASSETS", "brand", "icons", "_lucide_names.json"),
                                    encoding="utf-8")))
    except Exception:
        return []


def _llm_direct(scenes, segments):
    """LLM DIRECTOR (opt-in `SEOSONA_LLM_DIRECTOR=1`): author per-scene ICON (semantic, from the full
    Lucide set) + CHIPS (meaningful key terms) — smarter than the regex rules. Returns {idx: {icon,chips}}
    or {} on ANY failure (→ the deterministic rules stand). Never blocks a render."""
    if os.environ.get("SEOSONA_LLM_DIRECTOR", "0") != "1":
        return {}
    if not (os.getenv("GEMINI_API_KEY") or os.getenv("SEOSONA_OLLAMA_MODEL")):
        return {}
    try:
        import llm_engine
    except Exception:
        return {}
    names = _lucide_names()
    if not names:
        return {}
    nameset = set(names)
    lines = "\n".join(f"{i}: [{sc.get('kicker','')}] {(segments[i] if i < len(segments) else '')[:72]}"
                      for i, sc in enumerate(scenes))
    sysp = ("Bạn là ĐẠO DIỄN hình ảnh cho video ngắn. Với MỖI cảnh, chọn 1 ICON (đúng TÊN trong danh sách "
            "Lucide được cấp) minh hoạ SÁT nội dung cảnh, và 2-3 CHIP là từ khoá ngắn (≤14 ký tự, thuật ngữ "
            "tech Việt/Anh) làm nổi bật ý chính. CHỈ dùng tên icon có trong danh sách.")
    userp = (f"ICON hợp lệ (chọn đúng tên, không bịa): {', '.join(names)}\n\nCÁC CẢNH:\n{lines}\n\n"
             f"Trả JSON: {{\"scenes\":[{{\"i\":0,\"icon\":\"ten-icon\",\"chips\":[\"...\"]}}]}} đúng "
             f"{len(scenes)} phần tử (i = chỉ số cảnh).")
    try:
        out = llm_engine.generate_json_strict(sysp, userp, require_key="scenes")
        rows = out.get("scenes") if isinstance(out, dict) else (out if isinstance(out, list) else None)
        res = {}
        for r in (rows or []):
            if not isinstance(r, dict):
                continue
            i = r.get("i")
            if not isinstance(i, int):
                continue
            ic = str(r.get("icon", "")).strip()
            chips = [str(c).strip()[:14] for c in (r.get("chips") or []) if str(c).strip()][:3]
            res[i] = {"icon": ic if ic in nameset else None, "chips": chips}
        if res:
            print(f"[director] LLM director refined {len(res)} scene(s)")
        return res
    except Exception as _e:
        return {}

# component → (demonstrative motion the factory renders, default action SFX). One INTENTIONAL
# treatment per visual kind so no scene is "just static text".
_MOTION = {
    "bignum":  ("đếm số tăng dần (count-up) + nảy", "impact_deep"),
    "stats":   ("đếm số tăng dần từng thẻ", "impact_hit"),
    "chart":   ("cột mọc dần trái→phải", "impact_soft"),
    "bars":    ("thanh chạy dần", "impact_soft"),
    "ring":    ("vòng % quét", "impact_soft"),
    "terminal": ("gõ lệnh từng dòng + success ✓", None),   # SFX sequence handled in _sfx_cues
    "compare": ("hai bên hiện đối đầu (VS)", "ui_click"),
    "steps":   ("hiện từng bước", "ui_pop"),
    "feature": ("hiện từng tính năng", "ui_pop"),
    "badges":  ("chip hiện lần lượt", "ui_success"),
    "mockup":  ("ảnh zoom + pan (Ken Burns) như video", "ui_pop"),
    "gittree": ("cây thư mục mở dần", "ui_pop"),
    "hub": ("sơ đồ orbit — node vệ tinh sáng dần quanh tâm", "impact_soft"),
    "quote":   ("trích dẫn hiện mượt", "ui_positive"),
    "tip":     ("mẹo bật lên", "ui_notify"),
    "repo":    ("thẻ dự án trượt vào", "impact_soft"),
    "cta":     ("nút kêu gọi nhấn mạnh", "ui_success"),
}

# CONTENT-semantic SFX: when the scene's meaning matches, override the component default so the
# sound MATCHES the message (a win sounds like success, a warning like an alert).
_SEMANTIC = [
    (("thành công", "hoàn tất", "xong", "miễn phí", "sẵn sàng", "chọn"), "ui_success"),
    (("cảnh báo", "vấn đề", "lỗi", "khó khăn", "rủi ro", "đừng"), "ui_notify"),
    (("nhanh", "tăng tốc", "bùng nổ", "kỷ lục", "vượt trội"), "impact_hit"),
    (("ra mắt", "mới", "đột phá", "lần đầu"), "riser_short"),
]


def _semantic_sfx(text):
    low = (text or "").lower()
    for kws, key in _SEMANTIC:
        if any(k in low for k in kws):
            return key
    return None


# CONTENT → illustrative emoji so a scene ILLUSTRATES what the voice says (user 2026-07-03: câu "ngốn
# tài nguyên máy tính" mà màn hình trống → phải có icon minh hoạ). Single-codepoint emoji ONLY (no
# variation-selector — those render blank per native_composer's note). Ordered: first keyword match wins.
_ICON = [
    (("tài nguyên", "máy tính", "gpu", "cpu", "phần cứng", "server", "bộ nhớ", "ram"), "💻"),
    (("bản quyền", "watermark", "dấu mờ", "logo", "hình ảnh", "ảnh"), "🖼"),
    (("video", "clip", "quay"), "🎬"),
    (("nhanh", "tốc độ", "tức thì", "real-time", "thời gian thực"), "⚡"),
    (("ai", "trí tuệ", "thông minh", "học máy", "mô hình"), "🤖"),
    (("miễn phí", "free"), "🆓"),
    (("bảo mật", "riêng tư", "an toàn", "cục bộ", "local", "trình duyệt"), "🔒"),
    (("cài đặt", "lệnh", "terminal", "code", "lập trình"), "🔧"),
    (("dữ liệu", "số liệu", "thống kê", "chỉ số"), "📊"),
    (("so sánh", "đối đầu", "khác biệt", "trước", "sau"), "🆚"),
    (("tăng", "vượt", "bùng nổ", "kỷ lục", "phổ biến", "tin dùng", "sao", "cộng đồng"), "🚀"),
    (("chính xác", "chuẩn", "đúng"), "🎯"),
    (("vấn đề", "khó khăn", "rắc rối", "phiền"), "⚠"),
]


def _scene_icon(text):
    # WHOLE-WORD match (space-pad like _plan_lottie / _SVG's " ai " cue). A bare substring test put a 🤖 AI
    # emoji on any sentence containing 'hai'/'mai'/'sai'/'trai' (all contain the substring 'ai') and a 🖼 on
    # 'cảnh' (contains 'ảnh') — VN substring collisions. Multi-word cues ("tài nguyên") still match.
    low = " " + re.sub(r"\s+", " ", (text or "").lower()) + " "
    for kws, ic in _ICON:
        if any(f" {k} " in low for k in kws):
            return ic
    return None


# Distinctive tokens make good SUPPORTING CHIPS (density study 2026-07: dense frames pack a chip-row
# under the hero — "big title + 3 sub-cards" is the workhorse). Catch CamelCase (GitHub, JavaScript),
# ALLCAPS (AI, API, MIT, GPU), and number+unit (100%, 4K, 9x) — natural, scannable, on-topic chips.
_CHIP_RX = re.compile(r'\b(?:[A-Z][a-zA-Z]*[A-Z0-9][a-zA-Z0-9]*|[A-Z]{2,5}|[a-z]+[A-Z][a-zA-Z]+|\d+%|\d+[KkMm]|\d+x)\b')


# CONTENT → Lucide SVG icon NAME (professional line-icon; the factory tints + sizes it). Preferred over
# the emoji when a fitting icon exists (reference craft = clean icon-tiles). Verified names in the lib.
_SVG = [
    (("tài nguyên", "máy tính", "gpu", "cpu", "phần cứng", "bộ nhớ", "ram"), "cpu"),
    (("trí tuệ", "thông minh", "học máy", "mô hình", "neural", " ai ", "ai."), "brain"),
    (("nhanh", "tốc độ", "tức thì", "real-time", "thời gian thực", "hiệu năng"), "zap"),
    (("bảo mật", "riêng tư", "an toàn", "cục bộ", "local", "bảo vệ", "trình duyệt"), "lock"),
    (("cài đặt", "lệnh", "terminal", "code", "lập trình", "script"), "code"),
    (("dữ liệu", "số liệu", "thống kê", "chỉ số", "biểu đồ"), "chart-column"),
    (("kết nối", "hệ sinh thái", "tích hợp", "mạng lưới", "liên kết"), "network"),
    (("tăng", "vượt", "bùng nổ", "phổ biến", "tin dùng", "ra mắt", "mới"), "rocket"),
    (("đóng gói", "thư viện", "gói", "module", "template", "kho"), "package"),
    (("web", "online", "toàn cầu", "trực tuyến"), "globe"),
    (("công cụ", "tiện ích", "xử lý"), "wrench"),
    (("mã nguồn", "github", "open source", "nguồn mở"), "git-branch"),
    (("chính xác", "chuẩn", "thuật toán"), "shield"),
]


def _scene_svg(text):
    # WHOLE-WORD match (space-pad like _scene_icon). Bare substring let "kho" (kho=warehouse) hit
    # "khoa"/"khoản"/"khoảng" → wrong 📦 package icon. .strip() lets the pre-padded " ai " / "ai." cues
    # still match cleanly; multi-word cues ("tài nguyên", "open source") keep working.
    low = " " + re.sub(r"\s+", " ", (text or "").lower()) + " "
    for kws, ic in _SVG:
        if any(f" {k.strip()} " in low for k in kws):
            return ic
    return None


def _chips(text, maxn=3):
    seen = []
    for m in _CHIP_RX.findall(text or ""):
        if 2 <= len(m) <= 18 and m.lower() not in (s.lower() for s in seen):
            seen.append(m)
        if len(seen) >= maxn:
            break
    return seen


def direct(scenes, segments, gh=None):
    """Annotate each scene with its directed treatment + return a shot list (list of dict rows)."""
    shot_list = []
    n = len(scenes)
    _llm = _llm_direct(scenes, segments)          # opt-in LLM director (else {} → rules stand)
    for i, sc in enumerate(scenes):
        comp = sc.get("comp") or sc.get("component")
        kind = comp[0] if isinstance(comp, (list, tuple)) and comp else (comp if isinstance(comp, str) else None)
        seg = segments[i] if segments and i < len(segments) else ""
        heading = f"{sc.get('h1','')} {sc.get('h2','')} {sc.get('kicker','')}"
        motion, base_sfx = _MOTION.get(kind, ("hiện mượt (fade)", "ui_pop"))
        # first scene = hook (riser lifts it), last = CTA
        if i == 0:
            motion = "hook mở màn — riser nâng"
        # content-semantic SFX beats the component default when the meaning matches
        sfx = _semantic_sfx(f"{heading} {seg}") or base_sfx
        # author it into the spec so the factory uses the DIRECTED sfx (not a generic default)
        if sfx and kind != "terminal":               # terminal owns its keystroke/success sequence
            fx = dict(sc.get("fx") or {})
            fx.setdefault("sfx", sfx)
            sc["fx"] = fx
        # ILLUSTRATIVE icon matched to the spoken words → fills empty space + shows what's being said.
        # Skip components that ARE the visual (mockup/repo/terminal show their own thing).
        icon = None
        if kind not in ("mockup", "repo", "terminal", "gittree"):
            icon = _scene_icon(f"{seg} {heading}")
            if icon:
                sc["icon"] = icon
            svg = _scene_svg(f"{seg} {heading}")     # professional Lucide line-icon (factory prefers it over emoji)
            if svg:
                sc["svg"] = svg
        # SUPPORTING CHIPS row (density study): scenes whose component ISN'T already a multi-item list get
        # a 2-3 chip cluster under the hero → +density, kills empty space. Skip list-heavy comps.
        if kind not in ("badges", "feature", "steps", "chiprow", "compare", "icongrid", "checklist", "stats"):
            ch = _chips(f"{seg}")
            if len(ch) >= 2:
                sc["chips"] = ch[:3]
        # LLM DIRECTOR override (opt-in): a semantically-chosen icon + chips beat the regex rules.
        if i in _llm:
            if _llm[i].get("icon"):
                sc["svg"] = _llm[i]["icon"]
            _lc = _llm[i].get("chips") or []
            if len(_lc) >= 2 and kind not in ("badges", "feature", "steps", "chiprow", "compare",
                                              "icongrid", "checklist", "stats"):
                sc["chips"] = _lc[:3]
        # DIRECTOR HOLDS THE WHOLE KHO: author the transition + a seek-safe effect accent per scene, so
        # the plan for EVERY resource layer (component · transition · effect · animation · SFX · block)
        # lives in one place and is reported. `force` in effect_library.entrance reads fx["transition"].
        _seed = sum(ord(c) for c in (segments[0] if segments else "s")[:24])
        fx = dict(sc.get("fx") or {})
        _trans = fx.get("transition") or _plan_transition(kind, i, _seed)
        if _trans:
            fx["transition"] = _trans
        _accent = _plan_accent(kind, i, n, _seed)
        if _accent and not fx.get("effect"):
            fx["effect"] = _accent
        sc["fx"] = fx
        # CONTENT-MATCHED lottie accent (sparse: only when the meaning calls for one; capped ≤3/video).
        _lottie = sc.get("lottie") or _plan_lottie(f"{heading} {seg}")
        if _lottie and sum(1 for s in scenes if s.get("lottie")) < 3:
            sc["lottie"] = _lottie
        else:
            _lottie = sc.get("lottie")
        _block = (sc.get("block") if isinstance(sc.get("block"), str) else (sc.get("block") or {}).get("name")) \
            if sc.get("block") else None
        _anim = "ambient+ghost" + (f"+{_accent}" if _accent else "") + (f"+lottie:{_lottie}" if _lottie else "")
        sc["direction"] = {"motion": motion, "sfx": sfx or "auto", "kind": kind or "text", "icon": icon or "-",
                           "chips": sc.get("chips") or "-", "transition": _trans or "auto",
                           "effect": _accent or "-", "block": _block or "-"}
        shot_list.append({"scene": i + 1, "tag": sc.get("kicker", ""), "kind": kind or "text",
                          "motion": motion, "sfx": sfx or "auto", "icon": icon or "-",
                          "transition": _trans or "auto", "effect": _accent or "-",
                          "anim": _anim, "block": _block or "-"})
    return shot_list


def format_shot_list(shot_list):
    """Human-readable bảng phân cảnh for the render log / QC — the director's FULL per-scene plan across
    every resource layer: component · transition · effect accent · animation · SFX · block."""
    out = ["[director] BẢNG PHÂN CẢNH (đạo diễn — nắm toàn bộ kho):"]
    for r in shot_list:
        out.append(f"  Cảnh {r['scene']:>2} [{r['tag']:<10}] {r['kind']:<11} {r.get('icon','-')} → {r['motion']}")
        out.append(f"        ↳ transition={r.get('transition','auto'):<10} effect={r.get('effect','-'):<10}"
                   f" anim={r.get('anim','-'):<18} sfx={r['sfx']:<10} block={r.get('block','-')}")
    return "\n".join(out)
