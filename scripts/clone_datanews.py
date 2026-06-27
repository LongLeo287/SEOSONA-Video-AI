# -*- coding: utf-8 -*-
"""Task B — chuyển video data-heavy sang template data-news (hero + chart + mockup)
để khác biệt mạnh về visual. Số liệu before/after thật (6×, -99%, -80%)."""
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN")); sys.path.insert(0, ROOT)
from scene_composer import compose
import native_composer as nc
OUT = os.path.join(ROOT, "8_WORKSPACE", "clones")
J = {}

# data-news scenes: [bignum(hero), null, chart, mockup, feature, compare, tip, cta]
J["kimi-highspeed"] = ("upbeat",
  ["Kimi K2.7 HighSpeed nhanh gấp sáu lần bản tiêu chuẩn.",
   "Một bản tăng tốc dành riêng cho việc viết code.",
   "Nhìn vào biểu đồ tốc độ giữa hai bản.",
   "Bảng thông số nhanh của phiên bản mới.",
   "Vì sao bản HighSpeed đáng thử ngay.",
   "Đặt bản thường cạnh HighSpeed trên cùng tác vụ.",
   "Tốc độ cao giúp vòng lặp viết code nhanh và mượt hơn.",
   "Theo dõi SEOSONA để xem thêm tin AI mỗi ngày."],
  [("Kimi HighSpeed", "nhanh gấp 6×"), ("Bản tăng tốc", "cho coding"), ("Tốc độ", "trực quan"),
   ("Tổng quan", "phiên bản"), ("Vì sao", "đáng thử"), ("Thường", "vs HighSpeed"),
   ("Tốc độ", "= năng suất"), ("Theo dõi SEOSONA", "xem thêm mỗi ngày")],
  {0: {"big": "6×", "label": "NHANH HƠN BẢN THƯỜNG"},
   2: {"title": "Tốc độ phản hồi", "items": [("HighSpeed", 100, "6×"), ("K2.7 thường", 17, "1×")]},
   3: {"url": "kimi.ai/highspeed", "tiles": [("6×", "nhanh hơn"), ("K2.7", "phiên bản"), ("Code", "tối ưu"), ("Giữ", "chất lượng")]},
   4: {"items": [("⚡", "Nhanh", "gấp 6 lần"), ("🧩", "Coding", "tối ưu cho code"), ("🎯", "Chất lượng", "không đổi")]},
   5: {"left": ("K2.7 thường", ["Tốc độ chuẩn", "Chờ lâu hơn"]), "right": ("HighSpeed", ["Nhanh 6 lần", "Tức thì", "Giữ chất lượng"])},
   6: {"title": "GHI NHỚ", "text": "Phản hồi nhanh giúp vòng lặp code ngắn lại — làm việc đỡ ngắt mạch."}},
  {"Kimi": "ki mi", "HighSpeed": "hai sì pít", "K2.7": "ca hai chấm bảy"})

J["codebase-memory-mcp"] = ("tech",
  ["Mỗi lượt chat, agent đọc lại toàn bộ codebase và đốt token.",
   "Có một MCP dùng knowledge graph chạy ngay trên máy bạn.",
   "Biểu đồ chi phí token trước và sau khi dùng.",
   "Bảng tổng quan nhanh của công cụ.",
   "Vì sao cách này đáng dùng.",
   "Gửi cả codebase lên cloud hay dùng graph local.",
   "Tiết kiệm token mà dữ liệu vẫn ở lại máy bạn.",
   "Theo dõi SEOSONA để xem thêm thủ thuật AI."],
  [("Agent đốt token", "mỗi lượt?"), ("Knowledge graph", "chạy local"), ("Chi phí token", "trước & sau"),
   ("Tổng quan", "công cụ"), ("Vì sao", "đáng dùng"), ("Cloud", "hay Local?"),
   ("Tiết kiệm", "& an toàn"), ("Theo dõi SEOSONA", "xem thêm")],
  {0: {"big": "-99%", "label": "CHI PHÍ TOKEN"},
   2: {"title": "Chi phí token mỗi lượt", "items": [("Không MCP", 100, "100%"), ("Có MCP", 4, "-99%")]},
   3: {"url": "github.com/codebase-memory", "tiles": [("-99%", "token"), ("Local", "trên máy"), ("Graph", "tri thức"), ("Riêng tư", "data ở máy")]},
   4: {"items": [("💸", "Tiết kiệm", "-99% token"), ("🔒", "Riêng tư", "data ở máy bạn"), ("⚡", "Nhẹ", "workflow gọn")]},
   5: {"left": ("Gửi codebase lên cloud", ["Tốn token", "Lộ dữ liệu", "Chậm"]), "right": ("Graph local", ["Tiết kiệm token", "Riêng tư", "Nhẹ"])},
   6: {"title": "GHI NHỚ", "text": "Cho agent một bộ nhớ tri thức local — bớt đọc lại, bớt đốt token."}},
  {"token": "tâu cừn", "MCP": "em xi pi", "codebase": "cốt bây", "graph": "gráp", "agent": "ây dần"})

J["hindsight-learn"] = ("tech",
  ["Debug đi debug lại cùng một lỗi rất mất thời gian.",
   "Hindsight trên HuggingFace giúp AI tự học từ lỗi.",
   "Biểu đồ thời gian debug trước và sau.",
   "Bảng tổng quan nhanh của công cụ.",
   "Vì sao cách này đáng chú ý.",
   "Tự sửa lỗi tay hay để AI tự học.",
   "Tiết kiệm thời gian mà không cần fine-tune.",
   "Theo dõi SEOSONA để xem thêm về AI Agent."],
  [("Debug lặp lại", "tốn thời gian?"), ("Hindsight", "AI học từ lỗi"), ("Thời gian debug", "trước & sau"),
   ("Tổng quan", "công cụ"), ("Vì sao", "đáng chú ý"), ("Tay", "hay tự học?"),
   ("Tiết kiệm", "không fine-tune"), ("Theo dõi SEOSONA", "xem thêm")],
  {0: {"big": "-80%", "label": "THỜI GIAN DEBUG"},
   2: {"title": "Thời gian debug", "items": [("Tự sửa tay", 100, "100%"), ("Có Hindsight", 20, "-80%")]},
   3: {"url": "huggingface.co/hindsight", "tiles": [("-80%", "thời gian"), ("0", "fine-tune"), ("Tự học", "từ lỗi"), ("HF", "HuggingFace")]},
   4: {"items": [("🧠", "Tự học", "từ lỗi đã gặp"), ("⏱️", "Nhanh", "-80% thời gian"), ("🔧", "Gọn", "không fine-tune")]},
   5: {"left": ("Tự sửa lỗi tay", ["Lặp lại", "Tốn thời gian", "Dễ quên"]), "right": ("Hindsight", ["Tự học từ lỗi", "Không fine-tune", "Cải thiện dần"])},
   6: {"title": "GHI NHỚ", "text": "Cho AI học từ lỗi cũ — bớt lặp lại, debug nhanh hơn nhiều."}},
  {"Hindsight": "hai sai", "HuggingFace": "hâ ging phây", "debug": "đi bấc", "fine-tune": "phai tiun"})

if __name__ == "__main__":
    sel = sys.argv[1] if len(sys.argv) > 1 else None
    for slug, (mood, SEG, HEAD, DATA, LEX) in J.items():
        if sel and slug != sel: continue
        print(f"\n===== {slug} (data-news, bgm={mood}) =====")
        content = compose("data-news", segments=SEG, headings=HEAD, scene_data=DATA, lexicon=LEX)
        nc.make_video_from_template("data-news", content, os.path.join(OUT, slug),
                                    output=os.path.join(OUT, slug + ".mp4"), music=mood)
    print("\nDONE")
