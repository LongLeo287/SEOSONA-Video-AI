# -*- coding: utf-8 -*-
"""Clone batch 4 — remaining reference videos to reach full coverage of the 30."""
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN")); sys.path.insert(0, ROOT)
from scene_composer import compose
import native_composer as nc
OUT = os.path.join(ROOT, "8_WORKSPACE", "clones")
J = {}

J["archify-diagrams"] = ("tool-walkthrough", "tech",
  ["Mô tả hệ thống bằng lời rồi tự tay vẽ sơ đồ kiến trúc rất mất thời gian.",
   "Archify biến mô tả thành sơ đồ kiến trúc đẹp ngay trong chat.",
   "Là skill cho Claude, Codex CLI và opencode.",
   "Cài đặt nhanh, dùng được ngay.",
   "Chỉ cần mô tả, Archify lo phần còn lại.",
   "Vẽ tay thì lâu, Archify thì tức thì.",
   "Mã nguồn mở, miễn phí dùng.",
   "Vào GitHub Archify để thử. Theo dõi SEOSONA."],
  [("Vẽ sơ đồ", "tốn thời gian?"), ("Archify", "mô tả → sơ đồ"), ("Skill cho", "Claude & Codex"),
   ("Cài đặt", "nhanh gọn"), ("Chỉ cần", "mô tả bằng lời"), ("Vẽ tay", "hay tự động?"),
   ("Miễn phí", "& mã nguồn mở"), ("Theo dõi SEOSONA", "xem thêm")],
  {0: {"big": "Chat", "label": "MÔ TẢ → SƠ ĐỒ KIẾN TRÚC"},
   2: {"owner": "Archify", "name": "Archify", "stars": "OSS",
       "desc": "Skill biến mô tả hệ thống thành sơ đồ kiến trúc đẹp — cho Claude, Codex CLI, opencode.",
       "tags": ["Skill", "Sơ đồ", "Mã nguồn mở"], "btn": "Tải miễn phí"},
   3: {"title": "~/archify", "lines": [("$", "thêm skill archify vào Claude"), ("$", "mô tả hệ thống của bạn"), ("ok", "Sơ đồ kiến trúc sẵn sàng")]},
   4: {"items": [("Cho Claude", ""), ("Cho Codex CLI", ""), ("Cho opencode", "")]},
   5: {"left": ("Vẽ sơ đồ tay", ["Tốn thời gian", "Khó cập nhật"]),
       "right": ("Archify", ["Tức thì", "Đẹp & chuẩn", "Ngay trong chat"])},
   6: {"items": ["SKILL", "SƠ ĐỒ", "MÃ NGUỒN MỞ", "AI"]}},
  {"Archify": "ác chi phai", "Claude": "clốt", "Codex": "cô đếch", "opencode": "âu pừn cốt", "AI": "ây ai"})

J["codex-ollama-local"] = ("tool-walkthrough", "tech",
  ["Codex không chỉ chạy với model của OpenAI.",
   "Đây là cách dùng Ollama để đổi Codex sang model local.",
   "Một cấu hình đơn giản giúp bạn chủ động hơn.",
   "Cài Ollama và trỏ Codex sang đó.",
   "Vài bước là xong.",
   "Lưu cấu hình để dùng lại cho Codex App.",
   "Local, tiết kiệm, riêng tư.",
   "Theo dõi SEOSONA để xem thêm thủ thuật."],
  [("Codex", "chỉ chạy OpenAI?"), ("Ollama", "đổi sang local"), ("Codex", "+ Ollama"),
   ("Cài đặt", "& trỏ model"), ("Cách dùng", "vài bước"), ("Cloud", "hay Local?"),
   ("Local", "& riêng tư"), ("Theo dõi SEOSONA", "xem thêm")],
  {0: {"big": "Local", "label": "MODEL CHẠY TRÊN MÁY BẠN"},
   2: {"owner": "Codex", "name": "Codex + Ollama", "stars": "MẸO",
       "desc": "Đổi Codex sang model chạy local bằng Ollama — chủ động, tiết kiệm, riêng tư.",
       "tags": ["Local", "Ollama", "Codex"], "btn": "Xem cách"},
   3: {"title": "~/codex", "lines": [("$", "ollama pull <model>"), ("$", "cấu hình Codex trỏ Ollama"), ("ok", "Codex chạy model local")]},
   4: {"items": [("Cài Ollama", ""), ("Trỏ Codex sang local", ""), ("Lưu cấu hình", "")]},
   5: {"left": ("Dùng cloud", ["Tốn phí", "Cần mạng", "Phụ thuộc"]),
       "right": ("Local + Ollama", ["Miễn phí", "Chạy offline", "Chủ động"])},
   6: {"items": ["LOCAL", "OLLAMA", "TIẾT KIỆM", "RIÊNG TƯ"]}},
  {"Codex": "cô đếch", "Ollama": "âu la ma", "OpenAI": "âu pừn ai", "local": "lâu cồ", "model": "mô đồ"})

J["ai-studio-android"] = ("ai-news-flash", "news",
  ["Google AI Studio giờ build được Android app từ prompt.",
   "Prompt ý tưởng, sinh Kotlin và Jetpack Compose.",
   "Test bằng emulator, cài qua ADB rồi đưa lên thiết bị.",
   "Một bước tiến cho việc làm app bằng AI.",
   "Nhanh, trực quan, ít rào cản.",
   "Theo dõi SEOSONA để cập nhật công cụ AI."],
  [("Google AI Studio", "build Android"), ("Prompt", "→ Kotlin"), ("Test emulator", "cài qua ADB"),
   ("Bước tiến", "làm app AI"), ("Nhanh", "& ít rào cản"), ("Theo dõi SEOSONA", "xem thêm")],
  {2: {"owner": "Google", "name": "AI Studio · Android", "stars": "MỚI",
       "desc": "Prompt ý tưởng → sinh Kotlin + Jetpack Compose, test emulator, cài qua ADB.",
       "tags": ["Android", "Kotlin", "AI"], "btn": "Tìm hiểu"},
   3: {"big": "Prompt", "label": "→ ANDROID APP"},
   4: {"items": ["KOTLIN", "JETPACK COMPOSE", "EMULATOR", "GOOGLE"]}},
  {"Google": "gu gồ", "AI": "ây ai", "Android": "an đroi", "Kotlin": "cốt lin", "ADB": "ây đi bi", "prompt": "prom"})

J["hindsight-learn"] = ("benchmark-news", "tech",
  ["Debug đi debug lại cùng một lỗi rất mất thời gian.",
   "Hindsight trên HuggingFace giúp AI tự học từ lỗi.",
   "Không cần fine-tune mà vẫn cải thiện.",
   "Tự sửa thủ công thì lâu, để AI tự học thì nhanh.",
   "Vì sao cách này đáng chú ý.",
   "Một hướng đi thông minh cho AI Agent.",
   "Tiết kiệm thời gian, ít lặp lỗi.",
   "Theo dõi SEOSONA để xem thêm về AI Agent."],
  [("Debug lặp lại", "tốn thời gian?"), ("Hindsight", "AI học từ lỗi"), ("Không cần", "fine-tune"),
   ("Tay", "hay tự học?"), ("Vì sao", "đáng chú ý"), ("Hướng đi", "thông minh"),
   ("Tiết kiệm", "& ít lặp lỗi"), ("Theo dõi SEOSONA", "xem thêm")],
  {0: {"big": "-80%", "label": "THỜI GIAN DEBUG"},
   2: {"items": [("-80%", "thời gian debug"), ("0", "fine-tune"), ("Tự học", "từ lỗi")]},
   3: {"left": ("Tự sửa lỗi tay", ["Lặp lại", "Tốn thời gian", "Dễ quên"]),
       "right": ("Hindsight", ["Tự học từ lỗi", "Không fine-tune", "Cải thiện dần"])},
   4: {"items": [("🧠", "Tự học", "từ lỗi đã gặp"), ("⏱️", "Nhanh", "-80% thời gian"), ("🔧", "Gọn", "không fine-tune")]},
   5: {"big": "HuggingFace", "label": "NƠI CHIA SẺ MÔ HÌNH AI"},
   6: {"items": ["TỰ HỌC", "-80% DEBUG", "HUGGINGFACE", "AI AGENT"]}},
  {"Hindsight": "hai sai", "HuggingFace": "hâ ging phây", "debug": "đi bấc", "fine-tune": "phai tiun", "AI": "ây ai"})

J["cc-switch"] = ("tool-walkthrough", "tech",
  ["Mở hàng chục cửa sổ dòng lệnh rồi gõ cấu hình phức tạp rất mệt mỏi.",
   "cc-switch giúp bạn đổi cấu hình Claude Code dễ dàng.",
   "Quản lý nhiều profile chỉ trong một chỗ.",
   "Cài đặt nhanh với vài dòng lệnh.",
   "Đổi cấu hình chỉ với một thao tác.",
   "Gõ tay thì rối, cc-switch thì gọn.",
   "Mã nguồn mở, miễn phí dùng.",
   "Vào GitHub cc-switch để thử. Theo dõi SEOSONA."],
  [("Đổi cấu hình", "mệt mỏi?"), ("cc-switch", "đổi config dễ"), ("Quản lý", "nhiều profile"),
   ("Cài đặt", "vài dòng lệnh"), ("Đổi config", "một thao tác"), ("Gõ tay", "hay cc-switch?"),
   ("Miễn phí", "& mã nguồn mở"), ("Theo dõi SEOSONA", "xem thêm")],
  {0: {"big": "1 click", "label": "ĐỔI CẤU HÌNH CLAUDE CODE"},
   2: {"owner": "cc-switch", "name": "cc-switch", "stars": "OSS",
       "desc": "Đổi và quản lý nhiều cấu hình Claude Code dễ dàng, không cần gõ tay phức tạp.",
       "tags": ["Config", "Claude Code", "Mã nguồn mở"], "btn": "Tải miễn phí"},
   3: {"title": "~/cc-switch", "lines": [("$", "cài cc-switch"), ("$", "cc-switch use <profile>"), ("ok", "Đã đổi cấu hình")]},
   4: {"items": [("Nhiều profile", ""), ("Đổi 1 thao tác", ""), ("Gọn gàng", "")]},
   5: {"left": ("Gõ config tay", ["Rối", "Dễ sai", "Mất thời gian"]),
       "right": ("cc-switch", ["1 thao tác", "Quản lý tập trung", "Gọn"])},
   6: {"items": ["CONFIG", "CLAUDE CODE", "MÃ NGUỒN MỞ", "GỌN"]}},
  {"cc-switch": "xi xi suýt", "Claude": "clốt", "config": "con phích", "profile": "prô phai"})

J["rag-fusion"] = ("opinion-insight", "insight",
  ["RAG fusion — một kỹ thuật giúp truy hồi thông tin tốt hơn cho AI.",
   "Thay vì một truy vấn, nó tạo nhiều góc hỏi khác nhau.",
   "Rồi hợp nhất kết quả để ra câu trả lời chính xác hơn.",
   "Nó thay đổi cách AI tìm kiếm tri thức.",
   "Một điều đáng ghi nhớ khi xây hệ RAG.",
   "Chất lượng truy hồi tốt hơn rõ rệt.",
   "Cùng SEOSONA tìm hiểu sâu hơn về RAG."],
  [("RAG fusion", "là gì?"), ("Nhiều góc hỏi", "thay vì một"), ("Hợp nhất", "kết quả"),
   ("Thay đổi", "cách AI tìm tri thức"), ("Điều", "đáng ghi nhớ"), ("Truy hồi", "tốt hơn rõ"),
   ("Theo dõi SEOSONA", "cùng tìm hiểu")],
  {2: {"text": "RAG fusion tạo nhiều truy vấn từ một câu hỏi, rồi hợp nhất kết quả để truy hồi chính xác hơn.", "by": "Giải thích bởi SEOSONA"},
   3: {"items": [("🔎", "Đa truy vấn", "nhiều góc hỏi"), ("🔗", "Hợp nhất", "gộp kết quả"), ("🎯", "Chính xác", "ngữ cảnh tốt hơn")]},
   4: {"title": "GHI NHỚ", "text": "Một câu hỏi nhìn từ nhiều góc sẽ cho ngữ cảnh đầy đủ hơn — nền tảng của RAG tốt."},
   5: {"big": "RAG", "label": "TRUY HỒI TĂNG CƯỜNG CHO AI"}},
  {"RAG": "rác", "fusion": "phiu giần", "AI": "ây ai"})

if __name__ == "__main__":
    sel = sys.argv[1] if len(sys.argv) > 1 else None
    for slug, (tpl, mood, SEG, HEAD, DATA, LEX) in J.items():
        if sel and slug != sel: continue
        print(f"\n===== {slug} ({tpl}, bgm={mood}) =====")
        content = compose(tpl, segments=SEG, headings=HEAD, scene_data=DATA, lexicon=LEX)
        nc.make_video_from_template(tpl, content, os.path.join(OUT, slug),
                                    output=os.path.join(OUT, slug + ".mp4"), music=mood)
    print("\nDONE")
