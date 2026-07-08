# -*- coding: utf-8 -*-
"""Clone batch 2 — news/concept reference videos (hand-authored per MASTER_VIDEO_SPEC).
Mix of templates + freeform. Claims kept truthful/qualitative (no invented numbers)."""
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN")); sys.path.insert(0, ROOT)
from scene_composer import compose
import native_composer as nc
OUT = os.path.join(ROOT, "8_WORKSPACE", "clones")

JOBS = {}

# 1) codebase-memory-mcp — benchmark-news (giảm token bằng knowledge graph local)
JOBS["codebase-memory-mcp"] = ("benchmark-news", "tech",
  ["Mỗi lượt chat, agent đọc lại toàn bộ codebase và đốt token.",
   "Có một MCP dùng knowledge graph chạy ngay trên máy bạn.",
   "Nó cắt giảm chi phí token tới chín mươi chín phần trăm.",
   "Gửi cả codebase lên cloud thì tốn, graph local thì gọn.",
   "Vì sao cách này đáng dùng.",
   "Dữ liệu ở lại máy bạn, workflow nhẹ hơn hẳn.",
   "Local, an toàn, tiết kiệm.",
   "Theo dõi SEOSONA để xem thêm thủ thuật AI."],
  [("Agent đốt token", "mỗi lượt?"), ("Knowledge graph", "chạy local"), ("Token cost", "-99%"),
   ("Cloud hay Local?", "đâu lợi hơn"), ("Vì sao", "đáng dùng"), ("Nhẹ & an toàn", "ngay trên máy"),
   ("Local", "& tiết kiệm"), ("Theo dõi SEOSONA", "xem thêm mỗi ngày")],
  {0: {"big": "-99%", "label": "CHI PHÍ TOKEN"},
   2: {"items": [("-99%", "chi phí token"), ("Local", "chạy trên máy"), ("Graph", "knowledge graph")]},
   3: {"left": ("Gửi codebase lên cloud", ["Tốn token", "Lộ dữ liệu", "Chậm"]),
       "right": ("Knowledge graph local", ["Tiết kiệm token", "Dữ liệu riêng tư", "Nhẹ"])},
   4: {"items": [("💸", "Tiết kiệm", "-99% token"), ("🔒", "Riêng tư", "data ở máy bạn"), ("⚡", "Nhẹ", "workflow gọn")]},
   5: {"big": "Local", "label": "CHẠY NGAY TRÊN MÁY BẠN"},
   6: {"items": ["LOCAL", "TIẾT KIỆM", "RIÊNG TƯ", "MCP"]}},
  {"token": "tâu cừn", "MCP": "em xi pi", "codebase": "cốt bây", "graph": "gráp", "local": "lâu cồ", "AI": "ây ai"})

# 2) loop-keyword — opinion-insight (LOOP là gì)
JOBS["loop-keyword"] = ("opinion-insight", "insight",
  ["LOOP — từ khoá đang được nhắc rất nhiều trong giới AI. Vậy nó là gì?",
   "Đó là cách AI Agent tự lặp: làm, quan sát, rồi tự sửa.",
   "Một vòng lặp khép kín giúp agent tự cải thiện.",
   "Nó thay đổi cách chúng ta giao việc cho AI.",
   "Một điều đáng ghi nhớ về tương lai AI Agent.",
   "Tự động hoá ở mức cao hơn ta từng nghĩ.",
   "Cùng SEOSONA tìm hiểu sâu hơn về AI Agent."],
  [("LOOP", "là gì?"), ("Làm – quan sát", "– tự sửa"), ("Vòng lặp", "tự cải thiện"),
   ("Thay đổi", "cách giao việc"), ("Điều", "đáng ghi nhớ"), ("Tự động hoá", "mức cao hơn"),
   ("Theo dõi SEOSONA", "cùng tìm hiểu")],
  {2: {"text": "LOOP là vòng lặp khép kín: AI tự làm, tự quan sát kết quả, rồi tự điều chỉnh.", "by": "Giải thích bởi SEOSONA"},
   3: {"items": [("🔁", "Tự lặp", "làm → quan sát → sửa"), ("🤖", "Tự chủ", "ít cần giám sát"), ("📈", "Tự cải thiện", "tốt dần qua mỗi vòng")]},
   4: {"title": "GHI NHỚ", "text": "Tương lai không phải ra lệnh từng bước — mà giao mục tiêu cho agent tự lặp tới đích."},
   5: {"big": "Tự chủ", "label": "HƯỚNG ĐI CỦA AI AGENT"}},
  {"LOOP": "lup", "Agent": "ây dần", "AI": "ây ai"})

# 3) seedance-video — ai-news-flash (tin ngắn, tạo video AI)
JOBS["seedance-video"] = ("ai-news-flash", "news",
  ["Seedance hai chấm năm vừa ra mắt, ông hoàng tạo video thế hệ mới.",
   "Chất lượng video AI lên một tầm cao mới.",
   "Tạo video từ mô tả, chuyển động mượt và tự nhiên.",
   "Một bước nhảy lớn cho sáng tạo nội dung bằng AI.",
   "Nhanh, đẹp, dễ dùng.",
   "Theo dõi SEOSONA để cập nhật công cụ AI mới nhất."],
  [("Seedance 2.5", "ra mắt"), ("Video AI", "tầm cao mới"), ("Từ mô tả", "ra video"),
   ("Bước nhảy", "sáng tạo AI"), ("Nhanh", "& đẹp"), ("Theo dõi SEOSONA", "xem thêm")],
  {2: {"owner": "ByteDance", "name": "Seedance 2.5", "stars": "MỚI", "desc": "Mô hình tạo video AI thế hệ mới, chuyển động mượt và chân thực.",
       "tags": ["Video AI", "Text-to-Video", "Thế hệ mới"], "btn": "Xem demo"},
   3: {"big": "2.5", "label": "SEEDANCE PHIÊN BẢN MỚI"},
   4: {"items": ["MƯỢT", "CHÂN THỰC", "NHANH", "DỄ DÙNG"]}},
  {"Seedance": "sít đan", "AI": "ây ai", "ByteDance": "bai đừn"})

# 4) spacex-cursor — ai-news-flash (tin M&A) — giữ qualitative, không bịa số
JOBS["spacex-cursor"] = ("ai-news-flash", "news",
  ["Có tin SpaceX đang muốn mua lại Cursor bằng cổ phiếu.",
   "Động thái đưa Grok Build vào cuộc đua công cụ lập trình AI.",
   "Cursor là một trong những IDE AI được dùng nhiều nhất.",
   "Cuộc đua trực diện với Claude Code và Codex.",
   "Một thương vụ đáng chú ý của giới công nghệ.",
   "Theo dõi SEOSONA để không bỏ lỡ tin AI nóng."],
  [("SpaceX", "muốn mua Cursor"), ("Grok Build", "vào cuộc đua"), ("Cursor", "IDE AI hot"),
   ("Đối đầu", "Claude Code & Codex"), ("Thương vụ", "đáng chú ý"), ("Theo dõi SEOSONA", "tin AI nóng")],
  {2: {"owner": "Anysphere", "name": "Cursor", "stars": "HOT", "desc": "IDE tích hợp AI, một trong những công cụ lập trình AI phổ biến nhất.",
       "tags": ["IDE AI", "Lập trình", "Phổ biến"], "btn": "Tìm hiểu"},
   3: {"big": "AI IDE", "label": "CUỘC ĐUA CÔNG CỤ LẬP TRÌNH"},
   4: {"items": ["SPACEX", "GROK BUILD", "CURSOR", "M&A"]}},
  {"SpaceX": "sờ pây ích", "Cursor": "cơ sơ", "Grok": "grốc", "Codex": "cô đếch", "IDE": "ai đi i", "AI": "ây ai"})

HEADMAP = {}  # head lists are the 2nd item per job tuple above (index 2)

if __name__ == "__main__":
    sel = sys.argv[1] if len(sys.argv) > 1 else None
    for slug, (tpl, mood, SEG, HEAD, DATA, LEX) in JOBS.items():
        if sel and slug != sel: continue
        print(f"\n===== {slug} ({tpl}) =====")
        content = compose(tpl, segments=SEG, headings=HEAD, scene_data=DATA, lexicon=LEX)
        nc.make_video_from_template(tpl, content, os.path.join(OUT, slug),
                                    output=os.path.join(OUT, slug + ".mp4"), music=mood)
    print("\nDONE")
