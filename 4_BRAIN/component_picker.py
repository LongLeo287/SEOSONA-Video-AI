# -*- coding: utf-8 -*-
"""Component picker — choose a native_composer scene component (kind, data) from a scene's
narration text. The single place the scene→component VOCABULARY lives (the sibling of
`block_picker` for hf_blocks). This is how the craft-study components (alert, chiprow,
bignum-strike, …) actually appear in videos: `video_engine.plan_scenes` calls `pick()` per
middle scene before its own bignum/stats/tip/quote fallbacks.

Deterministic + import-light (no LLM). Data shapes match
`2_KNOWLEDGE/hyperframes/craft/template-study-2026-07.md` §7. Grow the vocabulary HERE.
"""
import re

_NUM = re.compile(r"\d[\d.,]*%?")

# Cue words (Vietnamese, lower-cased). Order = priority in pick().
_DANGER = ("rủi ro", "nguy hiểm", "cảnh báo", "mất an toàn", "tấn công", "lỗ hổng",
           "sai lầm nghiêm trọng", "hiểm họa", "đừng bao giờ")
_CAUTION = ("lưu ý", "cẩn thận", "coi chừng", "chưa chắc", "kiểm chứng", "cần nhớ",
            "thận trọng", "chú ý", "đừng vội")
_SKEPTIC = ("chưa kiểm chứng", "ai bịa", "tự bịa", "nghe hợp lý", "chưa xác minh",
            "bịa số", "không có nguồn")
_LIST_TRIG = ("hỗ trợ", "bao gồm", "gồm có", "gồm", "tích hợp với", "tích hợp", "chạy với",
              "tương thích", "như là", ":")
# before→after contrast markers: (marker, before-is-left?) — "thay vì X thì Y", "trước … giờ …".
_BA_SPLIT = [(" thì ", "thay vì "), (" giờ ", "trước đây "), (" nay ", "trước kia ")]


def _nums(seg):
    return _NUM.findall(seg)


def _extract_list(seg):
    """A clear in-sentence list of ≥3 short items (after a trigger / colon, split on , / · và).
    Conservative: only fires when items are short (≤3 words) so prose never becomes chips."""
    low = seg.lower()
    cut = -1
    for t in _LIST_TRIG:
        p = low.rfind(t)
        if p > cut:
            cut = p + len(t)
    tail = seg[cut:] if cut > 0 else ""
    parts = re.split(r"\s*[,/·]\s*|\s+và\s+|\s+hoặc\s+", tail)
    # A part may still carry a CATEGORY prefix before a nested connector ("nhiều nền tảng như Windows"),
    # which exceeds the ≤3-word cap and drops the FIRST real item. Keep only what follows the nested
    # connector so the item survives ("Windows"). Runs only on an already-triggered tail → no new false
    # positives (prose without a trigger never reaches here); only strips prefixes, never adds items.
    _nested = re.compile(r"^.*?(?:\bnhư\b|\bgồm\b|:)\s*", re.IGNORECASE)
    parts = [_nested.sub("", p) for p in parts]
    parts = [p.strip(" .").strip() for p in parts if p.strip(" .")]
    parts = [p for p in parts if 1 <= len(p) <= 22 and len(p.split()) <= 3]
    return parts if len(parts) >= 3 else []


def _before_after(seg):
    """Extract a (before, after) contrast from 'thay vì X thì Y' / 'trước đây X giờ Y'."""
    low = seg.lower()
    for mid, pre in _BA_SPLIT:
        if pre in low and mid in low:
            tail = seg[low.index(pre) + len(pre):]
            if mid in tail.lower():
                j = tail.lower().index(mid)
                before = tail[:j].strip(" ,.")
                after = tail[j + len(mid):].strip(" ,.")
                if 3 <= len(before) <= 42 and 3 <= len(after) <= 42:
                    return before, after
    return None


def pick(seg, h1="", i=0, total=1, label_fn=None, prev_kind=None):
    """Return (kind, data) for a middle scene, or None (let the caller's fallbacks decide).
    label_fn(seg)->short caption (video_engine passes its _label). prev_kind = the previous
    scene's component kind, used to avoid the SAME component two scenes in a row (repetition)."""
    seg = seg or ""                     # a text-less scene must not crash picking (seg.lower / _nums(None))
    low = seg.lower()
    nums = _nums(seg)
    lab = (label_fn(seg) if label_fn else "") or (h1 or "SEOSONA")

    # 1) bignum-strike — MOST specific: a real number the speaker flags as false/unverified
    #    (vids 17,20). Checked before alert because "chưa kiểm chứng" is also a caution cue.
    if nums and any(c in low for c in _SKEPTIC):
        return ("bignum", {"big": nums[0], "label": lab, "strike": True})

    # 2) alert — a caution/danger beat → a role-coloured callout (craft-study §1). Never two
    #    alerts in a row (would read as monotonous).
    if prev_kind != "alert":
        if any(c in low for c in _DANGER):
            return ("alert", {"role": "danger", "title": (h1 or "RỦI RO").upper(), "text": seg.rstrip(".")})
        if any(c in low for c in _CAUTION):
            return ("alert", {"role": "caution", "title": (h1 or "LƯU Ý").upper(), "text": seg.rstrip(".")})

    # 3) before→after compare — a "thay vì X thì Y" contrast (craft-study §1 arrow variant).
    if prev_kind != "compare":
        ba = _before_after(seg)
        if ba:
            return ("compare", {"mode": "beforeafter", "left": ("Trước", [ba[0]]), "right": ("Sau", [ba[1]])})

    # 4) chiprow — an explicit list of ≥3 short items (compat/tool chips).
    if prev_kind != "chiprow":
        chips = _extract_list(seg)
        if chips:
            return ("chiprow", {"items": chips[:6]})

    return None


# ── WIDER deterministic vocabulary (no LLM) — reach more of the 48-frame kho from content CUES, so a
# video draws from the whole library even when the LLM cascade is down. STRICT: each rule fires only on a
# clear cue AND builds data HONESTLY from the scene's own words (never fabricates numbers/names). Cues are
# space-padded to dodge the VN ASCII-substring collision ([[vn-ascii-substring-collision]]).
_STEP_CUE = (" bước ", "đầu tiên", "tiếp theo", "sau đó", "cuối cùng", "thứ nhất", "thứ hai", "thứ ba")
_WEB_CUE = ("trang web", "website", " web ", "dashboard", "giao diện web", "landing page", "trình duyệt")
_APP_CUE = ("ứng dụng", " app ", "điện thoại", "di động", " mobile", "trên máy", "giao diện app")
_NOTIF_CUE = ("thông báo", "báo tin", "vừa nhận", "nhận được tin", "bảng tin đẩy")
_SOCIAL_CUE = ("mạng xã hội", "bài đăng", "đăng bài", "viral", "bình luận", "nhận xét", "chia sẻ trên")
_FEATURE_CUE = ("tính năng", "điểm mạnh", "điểm nổi bật", "khả năng", "lợi ích")
_CMD_CUE = ("câu lệnh", "dòng lệnh", "chạy lệnh", "terminal", "gõ lệnh", "cài đặt bằng lệnh", "command")
_SECTION_RE = re.compile(r"(?:phần|chương|bước)\s+(\d{1,2}|một|hai|ba|bốn|năm)", re.IGNORECASE)
_DATE_RE = re.compile(r"\b(19|20)\d{2}\b|\btháng\s+\d{1,2}\b")


def _has(low, cues):
    return any(c in low for c in cues)


def _short_clause(seg):
    """The first COMPLETE clause of a sentence (before a comma/colon/period), 2-8 words — for a callout
    that reads as a whole phrase, NEVER a mid-clause truncation like the 3-word `_label` ('TobyFlow không
    tự'). Returns None if there's no clean short clause (→ caller picks a different component)."""
    first = re.split(r"[,;:.!?]| - |—| mà | nhưng ", str(seg or "").strip())[0].strip(" .")
    w = first.split()
    return first if 2 <= len(w) <= 8 else None


def pick_wide(seg, h1="", i=0, total=1, label_fn=None, prev_kind=None):
    """pick() core cues FIRST; then the wider deterministic set. Returns (kind,data) or None. Only emits
    a kind whose data is HONESTLY derivable from `seg` — the rest stay LLM-only (forcing them = fabrication)."""
    got = pick(seg, h1, i, total, label_fn, prev_kind)
    if got and got[0] != "chiprow":
        return got                       # alert / compare / skeptic-bignum keep top priority
    seg = (seg or "").strip()
    low = seg.lower()
    lab = ((label_fn(seg) if label_fn else "") or h1 or "").strip()
    clauses = [p.strip(" .") for p in re.split(r"\s*[,;·]\s*|\s+rồi\s+|\s+sau đó\s+", seg) if len(p.strip()) > 3]

    # a plain list became chiprow — UPGRADE it to a specific list-family kind when the cue is clear
    # (else keep chiprow). Runs before the generic fall-through so the whole list-family kho is reachable.
    lst = _extract_list(seg)
    if len(lst) >= 2:
        if _has(low, ("danh sách", "cần làm", "checklist", "các bước cần", "gồm những")) and prev_kind != "checklist":
            return ("checklist", {"items": [(x, "done") for x in lst[:5]]})
        if _has(low, ("nhãn", " thẻ", "gắn tag", "từ khóa", "hashtag")) and prev_kind != "badges":
            return ("badges", {"items": lst[:6]})
        if _has(low, ("lựa chọn", "phương án", "tùy chọn", " gói ", "option")) and prev_kind != "pill_stack":
            return ("pill_stack", {"items": lst[:5]})
        if _has(low, ("danh mục", "hạng mục", "lĩnh vực", " loại ", " nhóm ")) and prev_kind != "icongrid":
            return ("icongrid", {"items": [["•", x] for x in lst[:6]]})
    # numeric-viz (HONEST: only real numbers from the text)
    _pcts = re.findall(r"(\d{1,3})\s*%", seg)
    if len(_pcts) == 1 and 0 <= int(_pcts[0]) <= 100 and prev_kind != "gauge":
        return ("gauge", {"value": int(_pcts[0]), "label": lab[:24]})
    _pairs = re.findall(r"([\wÀ-ỹ][\wÀ-ỹ ]{1,22}?)\s+(\d{1,3})\s*(?:điểm|point)", seg)
    _bars = [[p[0].strip()[:18], max(0, min(100, int(p[1])))] for p in _pairs][:5]
    if len(_bars) >= 2 and prev_kind != "bars":
        return ("bars", {"items": _bars})
    if got:
        return got                       # was a plain chiprow with no specific cue → keep it

    if _has(low, _STEP_CUE) and len(clauses) >= 2 and prev_kind != "steps":
        return ("steps", {"items": [(c[:40], "") for c in clauses[:4]]})
    if _has(low, _FEATURE_CUE) and prev_kind != "feature":
        items = _extract_list(seg)
        if len(items) >= 2:
            return ("feature", {"items": [("✦", x, "") for x in items[:4]]})
    if _has(low, _NOTIF_CUE) and prev_kind != "notification":
        return ("notification", {"app": "SEOSONA AI", "title": lab or (h1 or "Thông báo"), "text": seg[:120], "time": "vừa xong"})
    if _has(low, _SOCIAL_CUE) and prev_kind != "social":
        return ("social", {"name": "SEOSONA", "handle": "@seosona", "text": seg[:170]})
    if _has(low, _WEB_CUE) and prev_kind != "mockup":
        return ("mockup", {"url": "seosona.ai", "lines": [seg[:80]]})
    if _has(low, _APP_CUE) and prev_kind != "phone":
        scr = _extract_list(seg) or [seg[:38]]
        return ("phone", {"title": lab or "SEOSONA App", "screen": scr[:4]})
    if _has(low, _CMD_CUE) and prev_kind != "terminal" and lab:
        return ("terminal", {"title": "seosona@ai: ~", "lines": [["$", lab.lower()[:40]], ["ok", seg[:60]]]})
    m = _SECTION_RE.search(low)
    if m and prev_kind != "divider":
        _vn = {"một": "01", "hai": "02", "ba": "03", "bốn": "04", "năm": "05"}
        num = _vn.get(m.group(1), str(m.group(1)).zfill(2))
        return ("divider", {"num": num, "title": lab or h1 or seg[:30]})
    if _DATE_RE.search(seg) and prev_kind != "timeline":
        rows = []
        for c in clauses[:4]:
            dm = _DATE_RE.search(c)
            if dm:
                rows.append((dm.group(0), c.replace(dm.group(0), "").strip(" :-")[:34]))
        if len(rows) >= 2:
            return ("timeline", {"items": rows})
    return None


# Safe, NON-FABRICATED components any scene can honestly show (data = the scene's own text or a
# concept keyword — never invented numbers). Rotated so a video shows DISTINCT visuals even with no
# strong cues and no LLM. photocard also turns ON the image kho (native_composer auto-sources a photo).
_FILL_ROTATION = ("photocard", "quote", "callout", "tip")


def fill(seg, h1="", i=0, prev_kind=None, label_fn=None, concept=""):
    """GUARANTEE a real visual for a bare middle scene — the factory's OWN richness, no external
    LLM needed (this is what keeps videos rich when the LLM cascade is down). Cue-based pick() first;
    else a rotating safe component (varied by scene index, never repeating the previous kind). Only
    honest data (the scene text / a concept keyword) — never fabricates numbers or facts."""
    got = pick(seg, h1, i, max(i + 1, 2), label_fn, prev_kind)
    if got:
        return got
    seg_clean = (seg or "").rstrip(" .").strip()
    lab = ((label_fn(seg) if label_fn else "") or h1 or "").strip()
    concept = (concept or h1 or lab).strip()
    order = list(_FILL_ROTATION)
    order = order[i % len(order):] + order[:i % len(order)]     # rotate by index → distinct kinds
    for kind in order:
        if kind == prev_kind:
            continue
        if kind == "photocard" and concept:
            return ("photocard", {"title": (h1 or lab), "concept": concept})
        if kind == "quote" and 4 <= len(seg_clean) <= 150:
            return ("quote", {"text": seg_clean, "by": ""})
        if kind == "callout":
            _cl = _short_clause(seg_clean)          # a COMPLETE phrase, not the truncated 3-word label
            if _cl and _cl.lower() != (h1 or "").lower():   # and not a duplicate of the heading
                return ("callout", {"text": _cl})
            continue                                # no clean callout phrase → next rotation kind (never a fragment)
        if kind == "tip":
            return ("tip", {"title": "GHI NHỚ", "text": seg_clean or lab})
    return ("quote", {"text": seg_clean or (h1 or "SEOSONA"), "by": ""})   # last resort — always something


def auto_grow(seg, h1="", i=0, existing=None):
    """The kho SELF-GROWS: when NO built-in/generated frame fits a scene, HyperFrames (frame_synth)
    synthesises a NEW frame from the scene's content, BANKS it into the kho, and returns (kind, data) to
    use now + reuse forever (no LLM needed to reuse). None if it can't (no LLM reachable / invalid frame).
    Honest: the frame is filled with the scene's OWN text — never fabricates numbers."""
    try:
        import frame_synth as _fsyn
    except Exception:
        return None
    seg = (seg or "").strip()
    if len(seg) < 12:
        return None
    # sample data = the scene's own content (a short list if the sentence enumerates, else title+text)
    items = [p.strip() for p in re.split(r"[·;,:]| - |—", seg) if 3 <= len(p.strip()) <= 40][:5]
    sample = {"title": (h1 or "").strip(), "text": seg}
    if len(items) >= 2:
        sample["items"] = [{"text": x} for x in items]
    exist = set(existing or []) | _ALLOWED | set(_fsyn.kinds())
    kind = _fsyn.grow(f"{h1}: {seg}" if h1 else seg, sample, sorted(exist))
    if not kind:
        return None
    return (kind, _validate(kind, sample) or sample)


# roles this module can emit → kicker label (video_engine merges into its _KICKER_BY_ROLE).
KICKERS = {"alert": "LƯU Ý", "chiprow": "TƯƠNG THÍCH", "hub": "SƠ ĐỒ", "bars": "SO SÁNH",
           "compare": "SO SÁNH", "checklist": "DANH SÁCH", "icongrid": "TÍNH NĂNG",
           "filetree": "CẤU TRÚC", "linechart": "XU HƯỚNG", "donut": "CƠ CẤU"}


# ============================================================================ #
# LLM component enrichment — the STRUCTURED path (auto-on when a real LLM is up).
# Turns text scenes into rich components (hub/bars/compare/checklist/icongrid/filetree)
# that a single sentence can't derive. Every result is validated → never breaks the render.
# ============================================================================ #
_ALLOWED = {"compare", "bignum", "checklist", "hub", "icongrid", "alert", "filetree",
            "bars", "chiprow", "stats", "quote", "tip", "steps", "feature", "photocard",
            "linechart", "donut", "pie", "chat", "codecard", "tabs",
            "gauge", "metric_rows", "pill_stack", "people", "strike_list",
            "notification", "social", "phone",
            # rich frames the LLM MENU advertises + _validate shapes + native_composer renders, but which
            # were missing here → enrich_llm dropped them at the gate (wasted LLM effort, lost the visual).
            "comparison_grid", "split_reveal", "annotated_screenshot", "stat_grid", "ratio_dots",
            "layer_stack", "ticker_feed", "org_diagram", "concept_build"}


def _allowed():
    """_ALLOWED + any frame_synth-generated kinds (the self-grown kho), so LLM picks of a newly
    generated frame aren't dropped as unknown."""
    a = set(_ALLOWED)
    try:
        import frame_synth
        a |= set(frame_synth.kinds())
    except Exception:
        pass
    return a

_COMPONENT_MENU_FALLBACK = (
    "MENU component (chọn cái HỢP NHẤT với nội dung cảnh; bỏ qua nếu không rõ):\n"
    "- compare: 2 cột đối lập/trước-sau. data{left:[\"tiêu đề\",[\"ý\",..]],right:[\"tiêu đề\",[\"ý\",..]],mode?:\"beforeafter\"}\n"
    "- bars: thanh điểm/so sánh. data{items:[[\"nhãn\",số0-100],..]}\n"
    "- linechart: ĐƯỜNG xu hướng theo THỜI GIAN (traffic/thứ hạng/doanh thu qua các mốc). CHỈ dùng khi cảnh "
    "có chuỗi số THẬT ≥3 mốc. data{points:[[\"T1\",120],[\"T2\",180],..≤8], label?:\"chú thích trục\"}\n"
    "- donut: PHẦN trong TỔNG (tỷ trọng/cơ cấu: thiết bị, thị phần, phân bổ). CHỈ dùng khi cảnh có ≥2 phần có số. "
    "data{segments:[[\"Mobile\",60],[\"Desktop\",40],..≤6], center?:\"chữ giữa\", label?:\"chú thích\"}\n"
    "- pie: giống donut nhưng là BÁNH ĐẶC (miếng quạt tô kín, không lỗ giữa). data{segments:[[\"A\",60],[\"B\",40],..≤6], label?:\"chú thích\"}\n"
    "- chat: hội thoại tin nhắn (bong bóng trái=AI, phải=người dùng) — dùng khi mô tả 'hỏi AI → AI trả lời'. data{messages:[{from:\"user\",text:\"..\"},{from:\"ai\",text:\"..\"},..≤6]}\n"
    "- codecard: thẻ CODE/JSON có tên file + cú pháp tô màu (KHÁC terminal là dòng lệnh $). data{file:\"config.json\",lines:[\"dòng 1\",\"dòng 2\",..≤12]}\n"
    "- tabs: DANH SÁCH theo TAB (cấp độ/nhóm: Cơ bản/Nâng cao). 1 tab active. data{tabs:[\"Cơ bản\",\"Nâng cao\",..≤4],active:0,items:[[\"nội dung\",\"done|doing|locked\"],..≤6]}\n"
    "- hub: 1 trung tâm + vệ tinh. data{center:\"...\",nodes:[\"..\",..≤8],line:true}\n"
    "- concept_build: SƠ ĐỒ GIẢI THÍCH cách một thứ HOẠT ĐỘNG (quy trình/thành phần/quan hệ) — dùng khi cảnh "
    "GIẢI THÍCH 'cách … hoạt động', 'gồm những gì', 'A dẫn tới B'. Sơ đồ tự BUILD theo lời nói (KHÔNG phải chữ). "
    "data{nodes:[{label:\"..\",x:0-1,y:0-1,shape?:\"box|chip|tile|note\",role?:\"emphasis|success|danger|info\"},..≤9], "
    "edges?:[[0,1],[1,2],..], frames?:[{label:\"..\",x,y,w,h}]}\n"
    "- checklist: danh sách trạng thái. data{items:[[\"việc\",\"done|doing|locked\"],..]}\n"
    "- icongrid: lưới tính năng. data{items:[[\"emoji\",\"nhãn\"],..]}\n"
    "- filetree: cấu trúc thư mục. data{title:\"repo/\",items:[[\"📁\",\"tên\"],[\"📄\",\"tên\",\"chú thích\"]]}\n"
    "- alert: cảnh báo. data{role:\"danger|caution\",title:\"...\",items:[\"..\"]}\n"
    "- chiprow: hàng chip công cụ. data{items:[\"..\",..]}\n"
    "- stats: 3 số. data{items:[[\"số\",\"nhãn\"],..]}  · quote: trích dẫn. data{text:\"..\",by:\"..\"}\n"
    "- steps: các bước. data{items:[[\"tiêu đề\",\"phụ\"],..]}  · feature: emoji+tiêu đề. data{items:[[\"emoji\",\"tiêu đề\",\"phụ\"],..]}\n"
    "- photocard: mẹo/tip minh hoạ bằng ẢNH THẬT (ảnh tự tìm theo concept). data{title:\"...\",desc:\"1-2 câu\",num?:\"4\",total?:\"5\",concept?:\"từ khoá tìm ảnh\"}\n"
    "- comparison_grid: BẢNG so sánh N cột × M tiêu chí, cột THẮNG tô nổi. data{cols:[{name:\"..\",winner?:true},..≤4], "
    "rows:[[\"tiêu chí\",\"ô1\",\"ô2\"],..] (ô = ✓/✕/chữ ngắn)}\n"
    "- split_reveal: TRƯỚC/SAU bằng 2 ẢNH (ảnh tự tìm theo concept). data{left:{concept:\"từ khoá\",label:\"Trước\"},right:{concept:\"từ khoá\",label:\"Sau\"}}\n"
    "- annotated_screenshot: ẢNH có KHUNG chú ý vùng quan trọng (ảnh tự tìm). data{concept:\"từ khoá\",marks:[{x:0-1,y:0-1,w:0-1,h:0-1,label:\"..\"},..≤4]}\n"
    "- stat_grid: LƯỚI nhiều số liệu (2-6 ô), mỗi ô value+label(+delta). data{stats:[{value:\"300%\",label:\"Traffic\",delta:\"+120%\"},..≤6]}\n"
    "- ratio_dots: TỈ LỆ X/Y bằng lưới chấm (X chấm tô màu trên tổng Y). data{total:12,marked:9,caption:\"Đã tối ưu\"}\n"
    "- layer_stack: CÁC TẦNG xếp chồng (nền→đỉnh), 1 tầng có thể accent. data{title:\"Kiến trúc\",layers:[{label:\"Hạ tầng\",glyph:\"🖥️\",sub:\"..\"},{label:\"..\",accent:true},..≤6]}\n"
    "- ticker_feed: DÒNG hoạt động cuộn (mỗi dòng label+text+time). data{items:[{label:\"SEO\",text:\"Tối ưu tiêu đề\",time:\"now\",glyph:\"⚡\"},..≤6]}\n"
    "- org_diagram: NODE cha + lưới node con (con có thể kept=giữ / dim=loại+✕). data{parent:\"SEOSONA\",nodes:[{label:\"Content\"},{label:\"Backlink\",kept:true},{label:\"Spam\",dim:true},..≤12]}\n"
    "QUY TẮC: KHÔNG bịa số/tên; chỉ dùng dữ liệu có trong cảnh. Tiếng Việt. Số trong bars là 0-100."
)

# The LLM menu is now GENERATED from the single frame-study catalog (4_BRAIN/frame_study.py) so EVERY
# frame in the library is offered — nothing goes stale/missing → richer, more varied videos. Falls back
# to the hand-written literal above if the catalog can't be imported (never breaks the picker).
try:
    import frame_study as _frame_study
    _COMPONENT_MENU = _frame_study.menu()
except Exception:
    _COMPONENT_MENU = _COMPONENT_MENU_FALLBACK


def _real_llm():
    import os
    if os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"):
        return True
    if not os.getenv("SEOSONA_OLLAMA_MODEL"):
        return False
    try:
        import requests
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        return requests.get(f"{host}/api/tags", timeout=3).status_code == 200
    except Exception:
        return False


def _pair(x):
    """Coerce a 2-seq [title, items] with items as a list of strings."""
    if not isinstance(x, (list, tuple)) or len(x) < 2:
        return None
    title = str(x[0]).strip()
    items = [str(i).strip() for i in x[1] if str(i).strip()] if isinstance(x[1], (list, tuple)) else []
    return [title, items[:5]] if title and items else None


def _validate(kind, d):
    """Return render-safe data for `kind`, or None to drop it. Guards the render from bad LLM JSON."""
    try:
        if kind == "photocard":                      # img is AUTO-sourced at render time by concept
            title = str(d.get("title", "")).strip()
            if not title:
                return None
            out = {"title": title, "concept": str(d.get("concept", "") or title).strip()}
            for k in ("num", "total", "desc"):
                if d.get(k) not in (None, ""):
                    out[k] = d[k]
            return out
        if kind == "compare":
            l = _pair(d.get("left")); r = _pair(d.get("right"))
            if not (l and r):
                return None
            out = {"left": l, "right": r}
            if d.get("mode") == "beforeafter":
                out["mode"] = "beforeafter"
            return out
        if kind == "bars":
            items = []
            for it in d.get("items", []):
                if isinstance(it, (list, tuple)) and len(it) >= 2:
                    try:
                        items.append([str(it[0]).strip(), max(0, min(100, float(it[1])))])
                    except Exception:
                        pass
            return {"items": items[:5]} if len(items) >= 2 else None
        if kind == "hub":
            nodes = [str(x).strip() for x in d.get("nodes", []) if str(x).strip()][:8]
            c = str(d.get("center", "")).strip()
            return {"center": c, "nodes": nodes, "line": bool(d.get("line", True))} if c and len(nodes) >= 3 else None
        if kind == "concept_build":                  # explainer canvas — nodes at x,y (+ edges/frames)
            _sh = ("box", "chip", "tile", "note"); _ro = ("emphasis", "success", "danger", "caution", "info")
            nodes = []
            for nd in d.get("nodes", []):
                if isinstance(nd, dict) and str(nd.get("label", "")).strip():
                    nodes.append({"label": str(nd["label"]).strip()[:40],
                                  "x": min(1.0, max(0.0, float(nd.get("x", 0.5)))),
                                  "y": min(1.0, max(0.0, float(nd.get("y", 0.5)))),
                                  "shape": nd.get("shape") if nd.get("shape") in _sh else "box",
                                  **({"role": nd["role"]} if nd.get("role") in _ro else {})})
            if len(nodes) < 2:
                return None
            edges = [[int(e[0]), int(e[1])] for e in d.get("edges", [])
                     if isinstance(e, (list, tuple)) and len(e) >= 2 and 0 <= int(e[0]) < len(nodes) and 0 <= int(e[1]) < len(nodes)]
            frames = [{"label": str(f.get("label", "")).strip()[:30], "x": float(f.get("x", .1)),
                       "y": float(f.get("y", .1)), "w": float(f.get("w", .4)), "h": float(f.get("h", .3))}
                      for f in d.get("frames", []) if isinstance(f, dict)][:2]
            return {"nodes": nodes, "edges": edges, **({"frames": frames} if frames else {})}
        if kind == "comparison_grid":
            cols = []
            for c in d.get("cols", [])[:4]:
                nm = str((c.get("name") if isinstance(c, dict) else c) or "").strip()
                if nm:
                    cols.append({"name": nm, **({"winner": True} if isinstance(c, dict) and c.get("winner") else {})})
            rows = [[str(x).strip() for x in r] for r in d.get("rows", [])
                    if isinstance(r, (list, tuple)) and len(r) >= 2 and str(r[0]).strip()]
            return {"cols": cols, "rows": rows} if len(cols) >= 2 and len(rows) >= 2 else None
        if kind == "split_reveal":
            def _s(x):
                x = x if isinstance(x, dict) else {}
                return {"concept": str(x.get("concept", "")).strip(), "label": str(x.get("label", "")).strip()}
            l, r = _s(d.get("left")), _s(d.get("right"))
            return {"left": l, "right": r} if (l["concept"] and r["concept"]) else None
        if kind == "annotated_screenshot":
            marks = [{"x": min(1.0, max(0.0, float(m.get("x", .1)))), "y": min(1.0, max(0.0, float(m.get("y", .1)))),
                      "w": min(1.0, float(m.get("w", .3))), "h": min(1.0, float(m.get("h", .15))),
                      "label": str(m.get("label", "")).strip()}
                     for m in d.get("marks", []) if isinstance(m, dict)][:4]
            c = str(d.get("concept", "")).strip()
            return {"concept": c, "marks": marks} if c and marks else None
        if kind == "stat_grid":
            stats = []
            for s in (d.get("stats") or d.get("items") or [])[:6]:
                s = s if isinstance(s, dict) else {"value": str(s)}
                val = str(s.get("value", "")).strip()
                if val:
                    stats.append({"value": val[:12], "label": str(s.get("label", "")).strip()[:24],
                                  **({"delta": str(s.get("delta")).strip()[:10]} if s.get("delta") else {})})
            return {"stats": stats} if len(stats) >= 2 else None
        if kind == "ratio_dots":
            try:
                total, marked = int(d.get("total", 0)), int(d.get("marked", 0))
            except Exception:
                return None
            if not (1 <= total <= 60 and 0 <= marked <= total):
                return None
            return {"total": total, "marked": marked, "caption": str(d.get("caption", "")).strip()[:28]}
        if kind == "layer_stack":
            layers = []
            for ly in d.get("layers", [])[:6]:
                ly = ly if isinstance(ly, dict) else {"label": str(ly)}
                lab = str(ly.get("label", "")).strip()
                if lab:
                    layers.append({"label": lab[:28], **({"glyph": str(ly.get("glyph"))[:3]} if ly.get("glyph") else {}),
                                   **({"sub": str(ly.get("sub")).strip()[:24]} if ly.get("sub") else {}),
                                   **({"accent": True} if ly.get("accent") else {})})
            return {"title": str(d.get("title", "")).strip()[:30], "layers": layers} if len(layers) >= 2 else None
        if kind == "ticker_feed":
            items = []
            for it in d.get("items", [])[:6]:
                it = it if isinstance(it, dict) else {"text": str(it)}
                txt = str(it.get("text", "")).strip()
                if txt:
                    items.append({"text": txt[:40], **({"label": str(it.get("label")).strip()[:14]} if it.get("label") else {}),
                                  **({"time": str(it.get("time")).strip()[:8]} if it.get("time") else {}),
                                  **({"glyph": str(it.get("glyph"))[:3]} if it.get("glyph") else {})})
            return {"items": items} if len(items) >= 2 else None
        if kind == "org_diagram":
            nodes = []
            for nd in d.get("nodes", [])[:12]:
                nd = nd if isinstance(nd, dict) else {"label": str(nd)}
                lab = str(nd.get("label", "")).strip()
                if lab:
                    nodes.append({"label": lab[:22], **({"kept": True} if nd.get("kept") else {}),
                                  **({"dim": True} if nd.get("dim") else {})})
            return {"parent": str(d.get("parent", "")).strip()[:24], "nodes": nodes} if len(nodes) >= 2 else None
        if kind == "chat":
            msgs = []
            for m in (d.get("messages") or d.get("items") or [])[:6]:
                m = m if isinstance(m, dict) else {"text": str(m)}
                txt = str(m.get("text", "")).strip()
                if txt:
                    who = str(m.get("from", m.get("who", "ai"))).lower()
                    msgs.append({"from": "user" if who in ("user", "me", "bạn", "you", "u") else "ai", "text": txt[:120]})
            return {"messages": msgs} if len(msgs) >= 2 else None
        if kind == "codecard":
            lines = [str(x) for x in (d.get("lines") or d.get("items") or []) if str(x).strip()][:12]
            fn = str(d.get("file") or d.get("title") or "").strip()[:32]
            return {"file": fn or "code", "lines": lines} if len(lines) >= 2 else None
        if kind == "tabs":
            tabs = [str(t).strip()[:18] for t in (d.get("tabs") or []) if str(t).strip()][:4]
            items = []
            for it in (d.get("items") or [])[:6]:
                it = it if isinstance(it, (list, tuple)) else [str(it)]
                lab = str(it[0]).strip() if it else ""
                if lab:
                    st = str(it[1]).lower() if len(it) > 1 and str(it[1]).lower() in ("done", "doing", "locked") else ""
                    items.append([lab[:40]] + ([st] if st else []))
            try:
                active = int(d.get("active", 0))
            except Exception:
                active = 0
            return {"tabs": tabs, "active": max(0, min(active, len(tabs) - 1)), "items": items} if len(tabs) >= 2 and len(items) >= 2 else None
        if kind == "gauge":
            try:
                val = float(str(d.get("value")).replace("%", "").replace(",", "").strip())
            except Exception:
                return None
            mx = d.get("max")
            try:
                mx = float(str(mx).replace("%", "").strip()) if mx is not None else 100.0
            except Exception:
                mx = 100.0
            out = {"value": val, "max": mx if mx > 0 else 100.0}
            for k in ("unit", "label", "display"):
                if str(d.get(k, "")).strip():
                    out[k] = str(d[k]).strip()[:16]
            return out
        if kind == "metric_rows":
            rows = []
            for it in (d.get("rows") or d.get("items") or [])[:6]:
                if isinstance(it, dict):
                    lab, valx, icon = str(it.get("label", "")).strip(), str(it.get("value", "")).strip(), str(it.get("icon", ""))[:3]
                elif isinstance(it, (list, tuple)) and it:
                    lab = str(it[0]).strip(); valx = str(it[1]).strip() if len(it) > 1 else ""; icon = str(it[2])[:3] if len(it) > 2 else ""
                else:
                    lab, valx, icon = str(it).strip(), "", ""
                if lab:
                    rows.append({"label": lab[:24], "value": valx[:12], **({"icon": icon} if icon else {})})
            return {"rows": rows} if len(rows) >= 2 else None
        if kind == "pill_stack":
            items = []
            for it in (d.get("items") or [])[:5]:
                it = it if isinstance(it, dict) else {"label": str(it)}
                lab = str(it.get("label", "")).strip()
                if lab:
                    items.append({"label": lab[:30], **({"icon": str(it.get("icon"))[:3]} if it.get("icon") else {}),
                                  **({"active": True} if it.get("active") else {})})
            return {"items": items} if len(items) >= 2 else None
        if kind == "people":
            items = []
            for it in (d.get("items") or [])[:5]:
                it = it if isinstance(it, dict) else {"name": str(it)}
                nm = str(it.get("name", "")).strip()
                if nm:
                    items.append({"name": nm[:28], **({"role": str(it.get("role")).strip()[:32]} if it.get("role") else {}),
                                  **({"img": str(it.get("img")).strip()} if it.get("img") else {})})
            return {"items": items} if len(items) >= 2 else None
        if kind == "strike_list":
            items = [str(x).strip()[:44] for x in (d.get("items") or []) if str(x).strip()][:5]
            out = {"items": items}
            if str(d.get("conclusion", "")).strip():
                out["conclusion"] = str(d["conclusion"]).strip()[:40]
            return out if len(items) >= 2 else None
        if kind == "notification":                       # mockup: real scene message, not demo data
            title = str(d.get("title", "")).strip()
            if not title:
                return None
            out = {"title": title[:60]}
            for k in ("app", "text", "time"):
                if str(d.get(k, "")).strip():
                    out[k] = str(d[k]).strip()[:120 if k == "text" else 40]
            return out
        if kind == "social":
            text = str(d.get("text", "")).strip()
            if not text:
                return None
            out = {"text": text[:180], "name": str(d.get("name", "")).strip()[:28] or "SEOSONA"}
            for k in ("handle", "likes", "comments"):
                if str(d.get(k, "")).strip():
                    out[k] = str(d[k]).strip()[:20]
            return out
        if kind == "phone":
            lines = [str(x).strip()[:40] for x in (d.get("screen") or d.get("items") or []) if str(x).strip()][:5]
            title = str(d.get("title", "")).strip()
            if not (title or lines):
                return None
            return {"title": title[:44], "screen": lines}
        if kind == "checklist":
            items = []
            for it in d.get("items", []):
                if isinstance(it, (list, tuple)) and it:
                    st = str(it[1]).strip() if len(it) > 1 else "done"
                    items.append([str(it[0]).strip(), st if st in ("done", "doing", "locked") else "done"])
                elif isinstance(it, str) and it.strip():
                    items.append([it.strip(), "done"])
            return {"items": items[:6]} if len(items) >= 2 else None
        if kind == "icongrid":
            items = [[str(it[0]).strip(), str(it[1]).strip()] for it in d.get("items", [])
                     if isinstance(it, (list, tuple)) and len(it) >= 2 and str(it[1]).strip()]
            return {"items": items[:6]} if len(items) >= 2 else None
        if kind == "filetree":
            items = []
            for it in d.get("items", []):
                if isinstance(it, (list, tuple)) and len(it) >= 2:
                    row = [str(it[0]).strip(), str(it[1]).strip()]
                    if len(it) >= 3 and str(it[2]).strip():
                        row.append(str(it[2]).strip())
                    items.append(row)
            return {"title": str(d.get("title", "")).strip(), "items": items[:6]} if len(items) >= 2 else None
        if kind == "alert":
            role = d.get("role", "caution"); role = role if role in ("danger", "caution") else "caution"
            body = {"role": role, "title": str(d.get("title", "")).strip()}
            its = [str(x).strip() for x in d.get("items", []) if str(x).strip()][:4]
            if its:
                body["items"] = its
            elif str(d.get("text", "")).strip():
                body["text"] = str(d["text"]).strip()
            else:
                return None
            return body
        if kind == "chiprow":
            its = [str(x).strip() for x in d.get("items", []) if str(x).strip()][:6]
            return {"items": its} if len(its) >= 3 else None
        if kind == "stats":
            its = [[str(it[0]).strip(), str(it[1]).strip() if len(it) > 1 else ""]
                   for it in d.get("items", []) if isinstance(it, (list, tuple)) and it][:3]
            return {"items": its} if its else None
        if kind == "quote":
            t = str(d.get("text", "")).strip()
            return {"text": t, "by": str(d.get("by", "")).strip()} if t else None
        if kind == "tip":
            t = str(d.get("text", "")).strip()
            return {"title": str(d.get("title", "GHI NHỚ")).strip(), "text": t} if t else None
        if kind in ("steps", "feature"):
            items = [list(map(lambda z: str(z).strip(), it)) for it in d.get("items", [])
                     if isinstance(it, (list, tuple)) and it]
            return {"items": items[:5]} if items else None
        if kind == "bignum":
            b = str(d.get("big", "")).strip()
            return {"big": b, "label": str(d.get("label", "")).strip()} if b else None
        if kind == "linechart":
            def _num(x):
                return float(str(x).replace(",", "").replace("%", "").strip())
            pts = []
            raw = d.get("points")
            if isinstance(raw, (list, tuple)):
                for it in raw:
                    if isinstance(it, (list, tuple)) and len(it) >= 2:
                        try:
                            pts.append([str(it[0]).strip(), _num(it[1])])
                        except Exception:
                            pass
            else:                                        # accept the {values:[],labels:[]} shape too
                vals, labs = d.get("values") or [], d.get("labels") or []
                for j, v in enumerate(vals):
                    try:
                        pts.append([str(labs[j]).strip() if j < len(labs) else "", _num(v)])
                    except Exception:
                        pass
            if len(pts) < 3:                             # a trend needs ≥3 points, else it's not a line
                return None
            out = {"points": pts[:8]}
            if str(d.get("label", "")).strip():
                out["label"] = str(d["label"]).strip()
            return out
        if kind in ("donut", "pie"):                     # same data shape; pie renders filled wedges
            def _num(x):
                return float(str(x).replace(",", "").replace("%", "").strip())
            segs = []
            for it in (d.get("segments") or []):
                if isinstance(it, (list, tuple)) and len(it) >= 2:
                    try:
                        v = _num(it[1])
                        if v > 0:
                            segs.append([str(it[0]).strip(), v])
                    except Exception:
                        pass
            if len(segs) < 2:                            # a breakdown needs ≥2 parts
                return None
            out = {"segments": segs[:6]}
            for k in ("center", "label"):
                if str(d.get(k, "")).strip():
                    out[k] = str(d[k]).strip()
            return out
        # generated frame (frame_synth) — the kho self-grew this kind. Its template fills a generic
        # {items:[...] + scalar fields} shape; keep only string/number leaves (the filler HTML-escapes).
        try:
            import frame_synth as _fsyn
            if kind in _fsyn.kinds():
                out = {}
                clean = []
                for it in (d.get("items") or [])[:8]:
                    if isinstance(it, dict):
                        row = {str(k2): str(v2) for k2, v2 in it.items()
                               if isinstance(v2, (str, int, float)) and str(v2).strip()}
                        if row:
                            clean.append(row)
                    elif isinstance(it, (str, int, float)) and str(it).strip():
                        clean.append(str(it))
                if clean:
                    out["items"] = clean
                for k2, v2 in d.items():
                    if k2 != "items" and isinstance(v2, (str, int, float)) and str(v2).strip():
                        out[str(k2)] = str(v2)
                return out or None
        except Exception:
            return None
    except Exception:
        return None
    return None


def enrich_llm(scenes):
    """Given [{seg,h1,h2}, …], ask a real LLM to assign a STRUCTURED component to the scenes that
    fit. Returns {index: (kind, data)} (validated, render-safe). {} when no real LLM — the caller
    then relies on the deterministic pick() above. Auto-on; disable with SEOSONA_LLM_COMPONENTS=0."""
    import os
    if os.getenv("SEOSONA_LLM_COMPONENTS", "1") == "0" or not scenes or not _real_llm():
        return {}
    lines = "\n".join(f'{i}. [{s.get("h1","")}] {s.get("seg","")}' for i, s in enumerate(scenes))
    sysp = ("Bạn là art-director cho video dọc SEOSONA. Gán component TRỰC QUAN cho các cảnh phù hợp "
            "để video sinh động, dựa ĐÚNG nội dung cảnh.\n" + _COMPONENT_MENU)
    example = (
        'VÍ DỤ (học theo format):\n'
        '- cảnh "OpenClaw 77 điểm, Hermes 85, con người 93" → '
        '{"i":<n>,"kind":"bars","data":{"items":[["OpenClaw",77],["Hermes",85],["Con người",93]]}}\n'
        '- cảnh "một API nối search, file, memory, agent" → '
        '{"i":<n>,"kind":"hub","data":{"center":"API","nodes":["search","file","memory","agent"],"line":true}}\n'
        '- cảnh "thủ công thì chậm, tự động thì nhanh" → '
        '{"i":<n>,"kind":"compare","data":{"left":["Thủ công",["Chậm"]],"right":["Tự động",["Nhanh"]]}}\n'
        '- cảnh "traffic tháng 1 là 120 nghìn, tăng dần tới tháng 6 là 780 nghìn" → '
        '{"i":<n>,"kind":"linechart","data":{"points":[["T1",120],["T3",240],["T6",780]],"label":"Traffic (nghìn)"}}\n')
    userp = (example + "\nCÁC CẢNH:\n" + lines + "\n\nTrả JSON DUY NHẤT: "
             '{"assign":[{"i":<số cảnh>,"kind":"<component>","data":{...}}]}. '
             "Chỉ gán khi thật hợp (không cần gán hết). Cảnh đầu (hook) và cảnh cuối (CTA) BỎ QUA.\n"
             'TỰ SINH KHUNG MỚI: nếu một cảnh RẤT cần khung trực quan mà KHÔNG component nào trong MENU hợp, '
             'đặt {"i":<n>,"kind":"__new__","desc":"<mô tả khung cần, tiếng Việt>","data":{...dữ liệu mẫu...}} '
             '— hệ thống sẽ tự sinh khung mới (light-mode, brand) và thêm vào kho để tái dùng. Dùng dè sẻn.')
    try:
        import sys as _s
        _s.path.insert(0, os.path.dirname(__file__))
        llm = __import__("llm_engine")
        out = llm.generate_json_strict(sysp, userp, require_key="assign")   # robust cascade
    except Exception as e:
        print(f"[component_picker] LLM enrich skipped ({e})")
        return {}
    res = {}
    # A linechart/donut claims a SPECIFIC numeric trend/breakdown — if the scene text has no real numbers,
    # the LLM invented the data (violates "không làm giả"). The structural _validate can't catch this (3
    # fabricated-but-valid points pass), so GROUND it: the scene must actually contain ≥2 numbers. Real
    # data scenes always do; qualitative scenes ("traffic tăng mạnh") don't → the chart is dropped.
    _NUMERIC_VIZ = {"linechart", "donut", "pie"}
    for a in (out.get("assign", []) if isinstance(out, dict) else []):
        try:
            i = a.get("i"); kind = a.get("kind"); data = a.get("data")
            if isinstance(i, int) and kind == "__new__":     # LLM asks the kho to GROW a frame it lacks
                desc = str(a.get("desc", "")).strip()
                sample = data if isinstance(data, dict) else {}
                if not (desc and 0 <= i < len(scenes)):
                    continue
                try:
                    import frame_synth as _fsyn
                    newk = _fsyn.grow(desc, sample, list(_allowed()))
                except Exception:
                    newk = None
                if newk:
                    v = _validate(newk, sample)
                    if v:
                        res[i] = (newk, v)
                        print(f"[component_picker] GREW new frame '{newk}' for scene {i} → added to kho")
                continue
            if isinstance(i, int) and 0 <= i < len(scenes) and kind in _allowed() and isinstance(data, dict):
                # never emit an out-of-range scene index (contract: keys are valid scene indices only) — the
                # bounds check now covers ALL kinds, so scenes[i] below is always safe.
                if kind in _NUMERIC_VIZ and len(_nums(str(scenes[i].get("seg", "")))) < 2:
                    print(f"[component_picker] dropped {kind} on scene {i} — no real numbers in the scene (ungrounded)")
                    continue
                v = _validate(kind, data)
                if v:
                    res[i] = (kind, v)
        except Exception:
            continue
    if res:
        print(f"[component_picker] LLM enriched {len(res)} scene(s): "
              + ", ".join(f"{i}:{k}" for i, (k, _) in sorted(res.items())))
    return res
