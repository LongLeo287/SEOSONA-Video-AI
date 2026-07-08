# -*- coding: utf-8 -*-
"""FRAME STUDY — the single canonical catalog of every SEOSONA scene "frame" (component).

Distilled from the 56-reel Video-Template frame-by-frame study + every component built into
`native_composer._component`. ONE source of truth so the whole pipeline draws from the FULL library
(richer, more varied videos): `component_picker` builds its LLM menu from `menu()`, the planner/director
can browse `by_group()`, and `selfcheck()` catches drift between this catalog and the render engine.

Each entry: (group, title, when — the content cue that should trigger it, schema — the data shape,
guard — an optional "only use when…" constraint). Keep this in lock-step with native_composer._component.
"""

# group → ordered kinds it contains (also the variety axis the planner rotates across)
GROUPS = ["number", "chart", "compare", "list", "diagram", "dev", "media", "text", "feed", "cta"]

# kind: {group, title, when, schema, guard?}
CATALOG = {
    # ── numbers / metrics ────────────────────────────────────────────────
    "bignum":     {"group": "number", "title": "Số lớn hero", "when": "1 con số CHỦ ĐẠO cần nhấn (kỷ lục, %, tăng trưởng)",
                   "schema": 'data{big:"300",suffix:"%",label:"..",delta?:"+20%",strike?:true}'},
    "stats":      {"group": "number", "title": "3 thẻ số", "when": "≤3 số liệu ngắn cạnh nhau",
                   "schema": 'data{items:[["số","nhãn"],..≤3]}'},
    "stat_grid":  {"group": "number", "title": "Lưới số liệu", "when": "2-6 chỉ số (mỗi ô value+label+delta)",
                   "schema": 'data{stats:[{value:"300%",label:"Traffic",delta:"+120%"},..≤6]}'},
    "ratio_dots": {"group": "number", "title": "Tỉ lệ chấm", "when": "tỉ lệ X trên Y trực quan (đã tối ưu 9/12)",
                   "schema": 'data{total:12,marked:9,caption:".."}'},
    "ring":       {"group": "number", "title": "Vòng %", "when": "MỘT tỉ lệ % dạng vòng tròn",
                   "schema": 'data{pct:80,label:".."}'},
    "gauge":      {"group": "number", "title": "Đồng hồ đo", "when": "điểm hiệu năng/tốc độ/benchmark (kim cung 240°)",
                   "schema": 'data{value:80,max?:100,unit?:"%",label:"..",display?:"6x"}'},
    "metric_rows": {"group": "number", "title": "Dòng chỉ số", "when": "vài chỉ số icon+nhãn+giá trị xếp DỌC (⭐ Sao 4.7K / Fork 1.3K)",
                   "schema": 'data{rows:[{label:"Sao",value:"4.7K",icon?:"⭐"},..≤6]}'},
    # ── charts / data-viz ────────────────────────────────────────────────
    "bars":       {"group": "chart", "title": "Thanh so sánh", "when": "so sánh vài hạng mục bằng thanh (0-100)",
                   "schema": 'data{items:[["nhãn",số0-100],..]}'},
    "chart":      {"group": "chart", "title": "Biểu đồ cột", "when": "cột dữ liệu tăng dần",
                   "schema": 'data{items:[["nhãn",số],..]}'},
    "linechart":  {"group": "chart", "title": "Đường xu hướng", "when": "xu hướng theo THỜI GIAN (traffic/rank qua các mốc)",
                   "schema": 'data{points:[["T1",120],["T2",180],..≤8],label?:".."}',
                   "guard": "CHỈ dùng khi có chuỗi số THẬT ≥3 mốc"},
    "donut":      {"group": "chart", "title": "Vòng cơ cấu", "when": "phần trong tổng (cơ cấu/thị phần) — dạng vành",
                   "schema": 'data{segments:[["Mobile",60],["Desktop",40],..≤6],center?:"..",label?:".."}',
                   "guard": "CHỈ dùng khi có ≥2 phần có số"},
    "pie":        {"group": "chart", "title": "Bánh đặc", "when": "phần trong tổng — dạng bánh ĐẶC (miếng quạt tô kín)",
                   "schema": 'data{segments:[["A",60],["B",40],..≤6],label?:".."}',
                   "guard": "CHỈ dùng khi có ≥2 phần có số"},
    "timeline":   {"group": "chart", "title": "Dòng thời gian", "when": "mốc thời gian/lộ trình/lịch sử phát triển",
                   "schema": 'data{items:[["mốc","tiêu đề","phụ?"],..≤5]}'},
    # ── compare ──────────────────────────────────────────────────────────
    "compare":    {"group": "compare", "title": "2 cột đối lập", "when": "A vs B / trước-sau (thay vì X thì Y)",
                   "schema": 'data{left:["tiêu đề",["ý",..]],right:["tiêu đề",["ý",..]],mode?:"beforeafter"}'},
    "comparison_grid": {"group": "compare", "title": "Bảng so sánh", "when": "bảng N cột × M tiêu chí, cột THẮNG tô nổi",
                   "schema": 'data{cols:[{name:"..",winner?:true},..≤4],rows:[["tiêu chí","ô1","ô2"],..]}'},
    "split_reveal": {"group": "compare", "title": "Trước/Sau 2 ảnh", "when": "before/after bằng 2 ẢNH (tự tìm theo concept)",
                   "schema": 'data{left:{concept:"..",label:"Trước"},right:{concept:"..",label:"Sau"}}'},
    # ── lists ────────────────────────────────────────────────────────────
    "checklist":  {"group": "list", "title": "Danh sách trạng thái", "when": "các mục có trạng thái xong/đang/khóa",
                   "schema": 'data{items:[["việc","done|doing|locked"],..]}'},
    "steps":      {"group": "list", "title": "Các bước", "when": "quy trình tuần tự các bước",
                   "schema": 'data{items:[["tiêu đề","phụ"],..]}'},
    "feature":    {"group": "list", "title": "Emoji + tiêu đề", "when": "danh sách tính năng emoji+tiêu đề+phụ",
                   "schema": 'data{items:[["emoji","tiêu đề","phụ"],..]}'},
    "badges":     {"group": "list", "title": "Huy hiệu", "when": "vài nhãn/thành tựu ngắn",
                   "schema": 'data{items:["..",..]}'},
    "icongrid":   {"group": "list", "title": "Lưới icon", "when": "lưới tính năng emoji+nhãn",
                   "schema": 'data{items:[["emoji","nhãn"],..]}'},
    "chiprow":    {"group": "list", "title": "Hàng chip", "when": "danh sách ≥3 mục ngắn (công cụ/tương thích) — xếp NGANG",
                   "schema": 'data{items:["..",..≤6]}'},
    "pill_stack": {"group": "list", "title": "Chồng nút chọn", "when": "các lựa chọn/gói xếp DỌC (chọn hướng), 1 cái có thể active",
                   "schema": 'data{items:[{label:"..",icon?:"..",active?:true},..≤5]}'},
    "strike_list": {"group": "list", "title": "Gạch bỏ cách cũ", "when": "before→after: gạch bỏ 'cách cũ' rồi chốt cách mới (mạnh retention)",
                   "schema": 'data{items:["cách cũ 1","cách cũ 2",..≤5], conclusion?:"cách mới"}'},
    "tabs":       {"group": "list", "title": "Danh sách theo tab", "when": "danh sách theo CẤP ĐỘ/NHÓM (Cơ bản/Nâng cao)",
                   "schema": 'data{tabs:["Cơ bản","Nâng cao",..≤4],active:0,items:[["nội dung","done|doing|locked"],..≤6]}'},
    # ── diagrams ─────────────────────────────────────────────────────────
    "hub":        {"group": "diagram", "title": "Trung tâm + vệ tinh", "when": "1 trung tâm toả ra nhiều nhánh",
                   "schema": 'data{center:"..",nodes:["..",..≤8],line?:true}'},
    "concept_build": {"group": "diagram", "title": "Sơ đồ giải thích", "when": "GIẢI THÍCH cách một thứ HOẠT ĐỘNG (A→B→C, gồm gì)",
                   "schema": 'data{nodes:[{label:"..",x:0-1,y:0-1,shape?:"box|chip|tile|note",role?:".."},..≤9],edges?:[[0,1],..],frames?:[..]}'},
    "org_diagram": {"group": "diagram", "title": "Sơ đồ tổ chức", "when": "node cha + lưới con (con giữ/loại)",
                   "schema": 'data{parent:"..",nodes:[{label:".."},{label:"..",kept?:true},{label:"..",dim?:true},..≤12]}'},
    "layer_stack": {"group": "diagram", "title": "Các tầng xếp chồng", "when": "kiến trúc nhiều tầng (nền→đỉnh)",
                   "schema": 'data{title:"..",layers:[{label:"..",glyph?:"..",sub?:"..",accent?:true},..≤6]}'},
    # ── dev / code ───────────────────────────────────────────────────────
    "terminal":   {"group": "dev", "title": "Cửa sổ terminal", "when": "DÒNG LỆNH $ (cài đặt/chạy)",
                   "schema": 'data{lines:[["$","lệnh"],["out","kết quả"],..]}'},
    "codecard":   {"group": "dev", "title": "Thẻ code/JSON", "when": "SOURCE/JSON có tên file (KHÁC terminal là lệnh $)",
                   "schema": 'data{file:"config.json",lines:["dòng 1",..≤12]}'},
    "filetree":   {"group": "dev", "title": "Cây thư mục", "when": "cấu trúc thư mục/repo",
                   "schema": 'data{title:"repo/",items:[["📁","tên"],["📄","tên","chú thích"]]}'},
    "repo":       {"group": "dev", "title": "Thẻ GitHub repo", "when": "giới thiệu repo (sao, ngôn ngữ, giấy phép)",
                   "schema": 'data{name:"..",stars:"..",tags:["..",..],desc?:".."}'},
    # ── media / mockup ───────────────────────────────────────────────────
    "photocard":  {"group": "media", "title": "Mẹo + ảnh thật", "when": "mẹo/tip minh hoạ bằng ẢNH THẬT (tự tìm)",
                   "schema": 'data{title:"..",desc:"..",num?:"4",total?:"5",concept?:"từ khoá tìm ảnh"}'},
    "mockup":     {"group": "media", "title": "Cửa sổ trình duyệt/app", "when": "khung app/trình duyệt (ảnh chụp thật)",
                   "schema": 'data{title:"..",img?:"..",tiles?:[..]}'},
    "annotated_screenshot": {"group": "media", "title": "Ảnh có khung chú ý", "when": "ảnh + khoanh vùng quan trọng (tự tìm)",
                   "schema": 'data{concept:"từ khoá",marks:[{x:0-1,y:0-1,w:0-1,h:0-1,label:".."},..≤4]}'},
    "chat":       {"group": "media", "title": "Hội thoại tin nhắn", "when": "mô tả 'hỏi AI → AI trả lời'",
                   "schema": 'data{messages:[{from:"user",text:".."},{from:"ai",text:".."},..≤6]}'},
    "people":     {"group": "media", "title": "Người/đội ngũ", "when": "giới thiệu người/đội/cộng đồng (avatar + tên + vai trò)",
                   "schema": 'data{items:[{name:"..",role?:"..",img?:"url"},..≤5]}'},
    "notification": {"group": "media", "title": "Thẻ thông báo (mockup)", "when": "hook dạng 'bạn vừa nhận thông báo…' / app báo tin",
                   "schema": 'data{app?:"..",title:"..",text:"..",time?:".."}'},
    "phone":      {"group": "media", "title": "Mockup điện thoại/app", "when": "khoe sản phẩm/app: khung điện thoại + màn hình nội dung",
                   "schema": 'data{title:"..",screen:["dòng",..≤5]}'},
    # ── text / emphasis ──────────────────────────────────────────────────
    "quote":      {"group": "text", "title": "Trích dẫn", "when": "câu nói/nhận định đáng nhớ",
                   "schema": 'data{text:"..",by?:".."}'},
    "tip":        {"group": "text", "title": "Box mẹo 💡", "when": "một mẹo/lưu ý ngắn",
                   "schema": 'data{text:"..",title?:".."}'},
    "callout":    {"group": "text", "title": "Câu nhấn", "when": "một câu tuyên bố mạnh, 1 cụm tô accent",
                   "schema": 'data{text:"..",items?:[".."]}'},
    "alert":      {"group": "text", "title": "Cảnh báo", "when": "beat cảnh báo/rủi ro/lưu ý",
                   "schema": 'data{role:"danger|caution",title:"..",items?:[".."],text?:".."}'},
    "divider":    {"group": "text", "title": "Vách ngăn phần", "when": "chia phần/chương (Phần 1, Bước 2)",
                   "schema": 'data{num:"01",title:"..",sub?:".."}'},
    # ── feed ─────────────────────────────────────────────────────────────
    "ticker_feed": {"group": "feed", "title": "Dòng hoạt động", "when": "dòng sự kiện cuộn (mỗi dòng label+text+time)",
                   "schema": 'data{items:[{label:"..",text:"..",time:"..",glyph?:".."},..≤6]}'},
    "social":     {"group": "feed", "title": "Bài đăng mạng XH (mockup)", "when": "trích 1 nhận định/quote dạng bài đăng social (KHÔNG số follower giả)",
                   "schema": 'data{name:"..",handle?:"..",text:"..",likes?:"..",comments?:".."}'},
    # ── cta ──────────────────────────────────────────────────────────────
    "cta":        {"group": "cta", "title": "Kêu gọi hành động", "when": "cảnh cuối: theo dõi/đăng ký/lưu/chia sẻ",
                   "schema": 'data{variant?:"subscribe|url|star|comment|follow",keyword?:".."}'},
}

# kinds intentionally NOT offered to the LLM picker (rendered by other paths / niche)
_MENU_SKIP = {"gittree"}   # git-graph = niche/demo; keep renderable but off the menu


def _effective():
    """Built-in CATALOG + frame_synth-generated frames (the self-grown kho). Generated frames are
    merged in so they appear in the menu, by_group, kinds and count as in-sync in selfcheck."""
    merged = dict(CATALOG)
    try:
        import frame_synth
        for k, v in frame_synth.catalog_entries().items():
            if k not in merged:              # never shadow a built-in
                merged[k] = v
    except Exception:
        pass
    return merged


def kinds():
    return list(_effective().keys())


def groups():
    return list(GROUPS)


def by_group(g):
    return [k for k, v in _effective().items() if v.get("group") == g]


def entry(kind):
    return _effective().get(kind)


def menu(header=True):
    """Generate the LLM component menu (Vietnamese) from the catalog — the SINGLE source the picker uses,
    so every frame in the library is offered (nothing goes stale/missing → richer, more varied videos)."""
    lines = []
    if header:
        lines.append("MENU component (chọn cái HỢP NHẤT với nội dung cảnh; bỏ qua nếu không rõ):")
    for k, v in _effective().items():
        if k in _MENU_SKIP:
            continue
        guard = f" [{v['guard']}]" if v.get("guard") else ""
        lines.append(f"- {k} ({v['title']}): {v['when']}.{guard} {v['schema']}")
    lines.append("QUY TẮC: KHÔNG bịa số/tên; chỉ dùng dữ liệu có trong cảnh. Tiếng Việt. Số trong bars là 0-100.")
    return "\n".join(lines)


def selfcheck(engine_kinds):
    """Drift guard: compare the catalog against the render engine's actual kinds. Returns
    {missing_in_catalog, missing_in_engine} — both empty = in sync."""
    cat = set(_effective()) | _MENU_SKIP
    eng = set(engine_kinds)
    # generated frames render via native_composer's frame_synth fallback, not a hard-coded branch —
    # so they legitimately won't appear in engine_kinds; don't flag them as engine-missing.
    try:
        import frame_synth
        gen = set(frame_synth.kinds())
    except Exception:
        gen = set()
    return {"missing_in_catalog": sorted(eng - cat), "missing_in_engine": sorted(cat - eng - gen)}


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(f"FRAME STUDY — {len(CATALOG)} frames across {len(GROUPS)} groups")
    for g in GROUPS:
        print(f"  {g:9}: {', '.join(by_group(g))}")
    print("\n--- generated menu (first 5 lines) ---")
    print("\n".join(menu().splitlines()[:5]))
