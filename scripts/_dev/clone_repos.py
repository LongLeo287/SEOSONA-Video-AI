# -*- coding: utf-8 -*-
"""Clone the GitHub-repo reference videos into SEOSONA-brand videos.

Each entry below is HAND-AUTHORED content (script + 2-tone headings + component data)
written by the Scene-Composer — not auto-generated. Real numbers (stars/license) come
from fetch_github at run time. For every video this script:
  1. writes a prompt spec to 9_PROMPTS/video_scripts/<slug>.md (generic topic name,
     NOT the source video's long title),
  2. renders the video to 8_WORKSPACE/clones/<slug>.mp4.

Run:  python scripts/clone_repos.py            # all
      python scripts/clone_repos.py <slug>     # one
"""
import os, sys, json
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN")); sys.path.insert(0, ROOT)
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
from scene_composer import fetch_github, repo_data_slots, compose
import native_composer as nc

OUT = os.path.join(ROOT, "8_WORKSPACE", "clones")
PROMPTS = os.path.join(ROOT, "9_PROMPTS", "video_scripts")
os.makedirs(OUT, exist_ok=True); os.makedirs(PROMPTS, exist_ok=True)

BASE_LEX = {"GitHub": "gít hắp", "AI": "ây ai", "API": "ây pi ai", "MIT": "em ai ti",
            "SEOSONA": "sê ô sô na", "LLM": "eo eo em", "CLI": "xi eo ai", "PDF": "pi đi ép"}


# ===========================================================================
# Each video: slug (generic topic), repo, template, btn, script(SEG)/heading(HEAD),
# and data builders. data() receives the live `slots` so star counts are real.
# ===========================================================================
def V(slug, repo, template, title, topic, btn, seg, head, data_fn, lex):
    return dict(slug=slug, repo=repo, template=template, title=title, topic=topic,
                btn=btn, seg=seg, head=head, data_fn=data_fn, lex=lex)


VIDEOS = [
    V("file-to-markdown", "microsoft/markitdown", "tool-walkthrough",
      "Biến mọi file thành Markdown chuẩn cho AI", "Công cụ chuyển đổi tài liệu",
      "Tải miễn phí",
      ["Bạn muốn nạp PDF, Word, Excel vào AI mà vẫn giữ nguyên cấu trúc?",
       "Microsoft vừa ra công cụ biến mọi file thành Markdown cực chuẩn.",
       "MarkItDown chuyển PDF, Office, ảnh và cả link YouTube sang Markdown.",
       "Cài đặt và dùng chỉ với vài dòng lệnh.",
       "Hỗ trợ rất nhiều định dạng đầu vào khác nhau.",
       "Copy thủ công thì rối, MarkItDown thì sạch và tự động.",
       "Hoàn toàn miễn phí, mã nguồn mở với giấy phép MIT.",
       "Vào GitHub MarkItDown để thử ngay. Theo dõi SEOSONA xem thêm thủ thuật."],
      [("Nạp file vào AI", "đúng chuẩn?"), ("Microsoft", "MarkItDown"), ("Mọi file", "→ Markdown"),
       ("Cài đặt", "1 lệnh pip"), ("Định dạng", "được hỗ trợ"), ("Thủ công", "hay tự động?"),
       ("Miễn phí", "& mã nguồn mở"), ("Theo dõi SEOSONA", "xem thêm mỗi ngày")],
      lambda s, gh: {
          0: {"big": gh["stars_h"], "label": "★  GITHUB STARS"},
          2: s["repo"],
          3: {"title": "~/markitdown", "lines": [("$", "pip install markitdown"),
              ("$", "markitdown baocao.pdf > baocao.md"), ("ok", "Đã chuyển sang Markdown")]},
          4: {"items": [("PDF & Word", ""), ("Excel & PowerPoint", ""), ("Ảnh & Audio", ""), ("YouTube & HTML", "")]},
          5: {"left": ("Copy thủ công", ["Mất định dạng", "Tốn thời gian", "Dễ sai sót"]),
              "right": ("MarkItDown", ["Giữ cấu trúc", "Tự động hoàn toàn", "Chuẩn cho LLM"])},
          6: {"items": s["badges"]},
      },
      {"Markdown": "mác đao", "MarkItDown": "mác ít đao", "Microsoft": "mai cờ rô sốt",
       "Word": "guợt", "Excel": "ích xeo", "PowerPoint": "pao pâu point", "YouTube": "diu túp",
       "HTML": "hát ti em eo", "pip": "píp"}),

    V("ai-agent-deepresearch", "bytedance/deer-flow", "repo-showcase",
      "AI Agent nghiên cứu sâu của ByteDance", "Agent nghiên cứu tự động",
      "Dùng miễn phí",
      ["Bạn tốn hàng giờ để tự tổng hợp thông tin cho một báo cáo?",
       "ByteDance vừa mở mã nguồn một AI Agent nghiên cứu sâu.",
       "DeerFlow tự tìm kiếm, đọc và tổng hợp thành báo cáo hoàn chỉnh.",
       "Tự code thì rối, DeerFlow điều phối nhiều bước gọn gàng.",
       "Khởi chạy chỉ với vài dòng lệnh.",
       "Được cộng đồng đón nhận cực nhanh trên GitHub.",
       "Miễn phí, mã nguồn mở, dùng được ngay.",
       "Vào GitHub DeerFlow để thử ngay. Theo dõi SEOSONA xem thêm."],
      [("Tự nghiên cứu", "tốn hàng giờ?"), ("ByteDance", "mở mã nguồn"), ("DeerFlow", "Agent nghiên cứu"),
       ("Tự làm", "hay để Agent?"), ("Khởi chạy", "vài dòng lệnh"), ("Được tin dùng", "trên GitHub"),
       ("Miễn phí", "& mã nguồn mở"), ("Theo dõi SEOSONA", "xem thêm mỗi ngày")],
      lambda s, gh: {
          0: {"big": "0₫", "label": "CHI PHÍ BẢN QUYỀN"},
          2: s["repo"],
          3: {"left": ("Tự code agent", ["Phức tạp", "Khó bảo trì", "Tốn thời gian"]),
              "right": ("DeerFlow", ["Điều phối sẵn", "Đa bước tự động", "Mã nguồn mở"])},
          4: {"title": "~/deer-flow", "lines": [("$", "git clone <repo> && cd deer-flow"),
              ("$", "uv run server.py"), ("ok", "Agent sẵn sàng nghiên cứu")]},
          5: {"big": gh["stars_h"], "label": "★  GITHUB STARS"},
          6: {"items": s["badges"]},
      },
      {"DeerFlow": "đia phờ lâu", "ByteDance": "bai đừn", "Agent": "ây dần", "uv": "diu vi"}),

    V("awesome-llm-collection", "Shubhamsaboo/awesome-llm-apps", "resource-list",
      "Kho hơn 100 dự án AI Agent và RAG", "Bộ sưu tập dự án mã nguồn mở",
      "Xem kho ngay",
      ["Bạn đang học cách xây dựng AI Agent và RAG nhưng thiếu mẫu thật?",
       "Có một kho tổng hợp hơn một trăm dự án AI đang gây chú ý.",
       "Awesome LLM Apps gom các ứng dụng Agent và RAG kèm mã nguồn.",
       "Bên trong có đủ chủ đề từ cơ bản đến nâng cao.",
       "Lấy về chỉ với một lệnh git clone.",
       "Hơn một trăm nghìn sao trên GitHub đã nói lên chất lượng.",
       "Hoàn toàn miễn phí và mã nguồn mở.",
       "Vào GitHub Awesome LLM Apps để học ngay. Theo dõi SEOSONA."],
      [("Học làm AI Agent", "thiếu mẫu?"), ("Kho dự án", "AI tổng hợp"), ("Awesome", "LLM Apps"),
       ("Bên trong", "có gì?"), ("Cách lấy", "1 lệnh git"), ("Được tin dùng", "hàng trăm nghìn"),
       ("Miễn phí", "& mã nguồn mở"), ("Theo dõi SEOSONA", "xem thêm mỗi ngày")],
      lambda s, gh: {
          2: s["repo"],
          3: {"items": [("AI Agent mẫu", ""), ("RAG ứng dụng thật", ""), ("Multi-agent", ""), ("Kèm mã nguồn", "")]},
          4: {"title": "~/awesome-llm-apps", "lines": [("$", "git clone <repo>"),
              ("$", "cd awesome-llm-apps"), ("ok", "Hơn 100 dự án sẵn sàng")]},
          5: {"big": gh["stars_h"], "label": "★  GITHUB STARS"},
          6: {"items": s["badges"]},
      },
      {"Awesome": "ô sầm", "RAG": "rác", "Agent": "ây dần", "Apps": "áp"}),

    V("leaked-system-prompts", "x1xhlol/system-prompts-and-models-of-ai-tools", "ai-news-flash",
      "Kho system prompt bị lộ của các AI tool", "Tổng hợp system prompt",
      "Xem kho ngay",
      ["System prompt là bí mật đứng sau mọi AI tool bạn đang dùng.",
       "Có một kho tổng hợp system prompt bị lộ của hàng loạt AI tool.",
       "Từ Cursor, v0 đến nhiều công cụ AI nổi tiếng khác.",
       "Hơn một trăm bốn mươi nghìn sao chỉ trong thời gian ngắn.",
       "Miễn phí, mã nguồn mở, cập nhật liên tục.",
       "Vào GitHub để khám phá ngay. Theo dõi SEOSONA xem thêm."],
      [("System Prompt", "bí mật của AI"), ("Kho prompt", "bị lộ"), ("Cursor, v0", "và hơn thế"),
       ("Được tin dùng", "hàng trăm nghìn"), ("Miễn phí", "& mã nguồn mở"), ("Theo dõi SEOSONA", "xem thêm")],
      lambda s, gh: {
          2: s["repo"],
          3: {"big": gh["stars_h"], "label": "★  GITHUB STARS"},
          4: {"items": s["badges"]},
      },
      {"prompt": "prom", "Cursor": "cơ sơ", "v0": "vi không"}),

    V("local-ai-engine", "mudler/LocalAI", "repo-showcase",
      "Chạy mọi model AI ngay trên máy, không cần GPU", "Engine AI chạy local",
      "Tải miễn phí",
      ["Trả tiền API AI mỗi tháng có làm bạn mệt mỏi?",
       "Có một engine chạy mọi model AI ngay trên máy bạn.",
       "LocalAI thay thẳng OpenAI API, không cần GPU.",
       "Cloud thì tốn phí và cần mạng, còn LocalAI miễn phí và offline.",
       "Cài đặt chỉ với một lệnh Docker duy nhất.",
       "Hơn bốn mươi bảy nghìn sao trên GitHub đã chứng minh sức hút.",
       "Hoàn toàn miễn phí, mã nguồn mở với giấy phép MIT.",
       "Vào GitHub LocalAI để thử ngay. Theo dõi SEOSONA xem thêm thủ thuật."],
      [("Trả tiền API AI", "mỗi tháng?"), ("Chạy AI", "ngay trên máy bạn"), ("LocalAI", "thay thẳng OpenAI"),
       ("Cloud hay Local?", "đâu hơn?"), ("Cài đặt", "1 lệnh Docker"), ("Được tin dùng bởi", "hàng vạn dev"),
       ("Miễn phí", "& mã nguồn mở"), ("Theo dõi SEOSONA", "xem thêm thủ thuật")],
      lambda s, gh: {
          0: {"big": "0₫", "label": "CHI PHÍ API / THÁNG"},
          2: s["repo"],
          3: {"left": ("Cloud API", ["Tốn phí hàng tháng", "Cần mạng", "Gửi data lên cloud"]),
              "right": ("LocalAI", ["Miễn phí 100%", "Chạy offline", "Dữ liệu riêng tư"])},
          4: {"title": "~/localai", "lines": [("$", "docker run -p 8080:8080 localai/localai"),
              ("$", "curl localhost:8080/v1/models"), ("ok", "Sẵn sàng thay OpenAI API")]},
          5: {"big": gh["stars_h"], "label": "★  GITHUB STARS"},
          6: {"items": s["badges"]},
      },
      {"LocalAI": "lâu cô eo ai", "OpenAI": "âu pừn ai", "Docker": "đốc cơ", "GPU": "gi pi diu"}),

    V("code-formatter", "prettier/prettier", "tool-walkthrough",
      "Hết tranh cãi tab hay space khi format code", "Công cụ format code",
      "Tải miễn phí",
      ["Bạn từng tốn hàng giờ căn chỉnh format code hay tranh cãi tab và space?",
       "Prettier giúp cả nhóm thống nhất một phong cách code duy nhất.",
       "Prettier là trình format code có quan điểm, chạy tự động.",
       "Cài đặt và format chỉ với vài dòng lệnh.",
       "Tích hợp được vào hầu hết editor và quy trình làm việc.",
       "Trước thì lộn xộn, sau khi dùng Prettier thì sạch đẹp nhất quán.",
       "Miễn phí, mã nguồn mở với giấy phép MIT.",
       "Vào GitHub Prettier để thử ngay. Theo dõi SEOSONA xem thêm."],
      [("Tab hay Space?", "hết tranh cãi"), ("Prettier", "thống nhất code"), ("Prettier", "trên GitHub"),
       ("Cài đặt", "1 lệnh npm"), ("Tích hợp", "mọi editor"), ("Trước", "& sau"),
       ("Miễn phí", "& mã nguồn mở"), ("Theo dõi SEOSONA", "xem thêm mỗi ngày")],
      lambda s, gh: {
          0: {"big": gh["stars_h"], "label": "★  GITHUB STARS"},
          2: s["repo"],
          3: {"title": "~/project", "lines": [("$", "npm install --save-dev prettier"),
              ("$", "npx prettier . --write"), ("ok", "Đã format toàn bộ dự án")]},
          4: {"items": [("Hỗ trợ JS, TS, CSS", ""), ("Tích hợp VS Code", ""), ("Chạy khi commit", "")]},
          5: {"left": ("Trước Prettier", ["Mỗi người một kiểu", "Tranh cãi tab/space", "Diff rối"]),
              "right": ("Có Prettier", ["Một phong cách", "Tự động format", "Diff sạch"])},
          6: {"items": s["badges"]},
      },
      {"Prettier": "prét ti ơ", "npm": "en pi em", "npx": "en pi ích", "format": "pho mát",
       "JS": "giây ét", "TS": "ti ét", "CSS": "xi ét ét", "commit": "cò mít"}),
]


def write_prompt(v, gh, content):
    """Document the hand-authored content as a reusable prompt spec."""
    lines = [f"# {v['title']}", "",
             f"- **Chủ đề (template):** `{v['template']}` — {v['topic']}",
             f"- **Nguồn dữ liệu:** GitHub `{gh['full']}` — {gh['stars_h']}★, {gh.get('lang') or '—'}, {gh.get('license') or 'OSS'} (số liệu THẬT, fetch lúc render)",
             f"- **Output:** `8_WORKSPACE/clones/{v['slug']}.mp4`", "",
             "## Kịch bản (DISPLAY form — RULE #1)", ""]
    for i, (sg, (h1, h2)) in enumerate(zip(content["segments"], v["head"])):
        lines.append(f"{i}. **[{h1} / {h2}]** {sg}")
    lines += ["", "## Lexicon (phát âm)", "",
              "```", json.dumps(content["lexicon"], ensure_ascii=False, indent=2), "```", "",
              "## Cách tái tạo", "```bash",
              f"python scripts/clone_repos.py {v['slug']}", "```"]
    p = os.path.join(PROMPTS, f"{v['slug']}.md")
    open(p, "w", encoding="utf-8").write("\n".join(lines))
    return p


def run(v):
    gh = fetch_github(v["repo"])
    if gh.get("error"):
        print(f"!! {v['slug']}: fetch failed {gh['error']}"); return None
    slots = repo_data_slots(gh, btn=v["btn"])
    data = v["data_fn"](slots, gh)
    lex = dict(BASE_LEX); lex.update(v["lex"])
    content = compose(v["template"], segments=v["seg"], headings=v["head"], scene_data=data, lexicon=lex)
    pp = write_prompt(v, gh, content)
    print(f"[prompt] {pp}")
    out = os.path.join(OUT, f"{v['slug']}.mp4")
    nc.make_video_from_template(v["template"], content, os.path.join(OUT, v["slug"]), output=out)
    return out


if __name__ == "__main__":
    sel = sys.argv[1] if len(sys.argv) > 1 else None
    for v in VIDEOS:
        if sel and v["slug"] != sel: continue
        print(f"\n===== {v['slug']}  ({v['repo']} -> {v['template']}) =====")
        run(v)
    print("\nDONE")
