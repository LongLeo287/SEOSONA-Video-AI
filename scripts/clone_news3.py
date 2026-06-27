# -*- coding: utf-8 -*-
"""Clone batch 3 — remaining reference videos (hand-authored per MASTER_VIDEO_SPEC).
Varied templates + BGM moods. Claims kept truthful/qualitative."""
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN")); sys.path.insert(0, ROOT)
from scene_composer import compose
import native_composer as nc
OUT = os.path.join(ROOT, "8_WORKSPACE", "clones")

J = {}

J["claude-artifacts"] = ("ai-news-flash", "news",
  ["Claude Code vừa update tính năng Artifacts.",
   "Biến mỗi phiên làm việc thành web sống động theo thời gian thực.",
   "Bạn xem kết quả trực quan và share cho cả nhóm ngay.",
   "Một nâng cấp đáng giá cho quy trình làm việc nhóm.",
   "Trực quan, real-time, dễ chia sẻ.",
   "Theo dõi SEOSONA để cập nhật Claude Code mới nhất."],
  [("Claude Code", "có Artifacts"), ("Phiên làm việc", "thành web sống"), ("Xem & share", "cho cả nhóm"),
   ("Nâng cấp", "cho teamwork"), ("Real-time", "& dễ share"), ("Theo dõi SEOSONA", "xem thêm")],
  {2: {"owner": "Anthropic", "name": "Claude Code · Artifacts", "stars": "MỚI",
       "desc": "Biến phiên làm việc thành web trực quan theo thời gian thực, share được cho nhóm.",
       "tags": ["Real-time", "Web sống động", "Teamwork"], "btn": "Tìm hiểu"},
   3: {"big": "Live", "label": "WEB THEO THỜI GIAN THỰC"},
   4: {"items": ["TRỰC QUAN", "REAL-TIME", "DỄ SHARE", "CLAUDE CODE"]}},
  {"Claude": "clốt", "Artifacts": "a ti phách", "Code": "cốt", "real-time": "ri eo tham", "AI": "ây ai"})

J["gemini-interactions-api"] = ("benchmark-news", "news",
  ["Google vừa ra mắt Interactions API cho Gemini.",
   "Một endpoint mới gói gọn rất nhiều khả năng.",
   "Những gì API này hỗ trợ.",
   "API rời rạc thì rối, một endpoint thì gọn.",
   "Vì sao developer nên chú ý.",
   "Một nền tảng thống nhất cho ứng dụng AI.",
   "Đa năng, gọn gàng, mạnh mẽ.",
   "Theo dõi SEOSONA để cập nhật API mới."],
  [("Gemini", "Interactions API"), ("Một endpoint", "nhiều khả năng"), ("Hỗ trợ", "những gì"),
   ("Rời rạc", "hay gộp?"), ("Vì sao", "đáng chú ý"), ("Nền tảng", "thống nhất"),
   ("Đa năng", "& gọn"), ("Theo dõi SEOSONA", "xem thêm")],
  {0: {"big": "1 API", "label": "GÓI NHIỀU KHẢ NĂNG"},
   2: {"items": [("Stream", "phản hồi liên tục"), ("Multi-turn", "chat nhiều lượt"), ("Tools", "gọi công cụ")]},
   3: {"left": ("Nhiều API rời", ["Khó tích hợp", "Code dài", "Dễ lỗi"]),
       "right": ("Interactions API", ["Một endpoint", "Đa năng", "Gọn gàng"])},
   4: {"items": [("🔀", "Đa năng", "text·stream·tool"), ("🧩", "Tích hợp", "một endpoint"), ("⚡", "Nhanh", "ít code hơn")]},
   5: {"big": "Gemini", "label": "NỀN TẢNG AI CỦA GOOGLE"},
   6: {"items": ["STREAMING", "MULTIMODAL", "TOOL USE", "GOOGLE"]}},
  {"Gemini": "giê mi nai", "API": "ây pi ai", "endpoint": "en point", "stream": "sì trim", "AI": "ây ai"})

J["hyperagent-fund"] = ("ai-news-flash", "upbeat",
  ["HyperAgent vừa mở quỹ The Founding 500.",
   "Mười triệu đô tín dụng inference cho 500 founder agent-first.",
   "Dành cho founder xây sản phẩm xoay quanh AI Agent.",
   "Một cú hích lớn cho hệ sinh thái agent.",
   "Cơ hội cho người xây dựng tương lai AI.",
   "Theo dõi SEOSONA để không bỏ lỡ cơ hội AI."],
  [("HyperAgent", "The Founding 500"), ("$10 triệu", "inference grants"), ("Cho 500", "founder agent-first"),
   ("Cú hích", "hệ sinh thái agent"), ("Cơ hội", "cho người xây"), ("Theo dõi SEOSONA", "xem thêm")],
  {0: {"big": "$10M", "label": "QUỸ INFERENCE GRANTS"},
   2: {"owner": "HyperAgent", "name": "The Founding 500", "stars": "MỚI",
       "desc": "Quỹ 10 triệu đô tín dụng inference cho 500 founder xây sản phẩm agent-first.",
       "tags": ["$10M", "500 founder", "Agent-first"], "btn": "Tìm hiểu"},
   3: {"big": "500", "label": "FOUNDER ĐƯỢC HỖ TRỢ"},
   4: {"items": ["$10 TRIỆU", "INFERENCE", "AGENT-FIRST", "FOUNDER"]}},
  {"HyperAgent": "hai pơ ây dần", "inference": "in phơ rần", "Agent": "ây dần", "AI": "ây ai"})

J["deepclaude"] = ("tool-walkthrough", "tech",
  ["Bạn muốn dùng Claude Code nhưng với model rẻ hơn nhiều lần?",
   "DeepClaude giúp bạn làm đúng điều đó.",
   "Kết hợp sức mạnh suy luận với model chi phí thấp.",
   "Cài đặt nhanh với vài dòng lệnh.",
   "Cách dùng rất đơn giản.",
   "Trả phí cao hay tối ưu chi phí, bạn chọn.",
   "Mã nguồn mở, miễn phí dùng.",
   "Vào GitHub DeepClaude để thử. Theo dõi SEOSONA."],
  [("Claude Code", "rẻ hơn?"), ("DeepClaude", "giải pháp"), ("Kết hợp", "suy luận + giá rẻ"),
   ("Cài đặt", "vài dòng lệnh"), ("Cách dùng", "đơn giản"), ("Phí cao", "hay tối ưu?"),
   ("Miễn phí", "& mã nguồn mở"), ("Theo dõi SEOSONA", "xem thêm")],
  {0: {"big": "↓ Chi phí", "label": "DÙNG CLAUDE RẺ HƠN"},
   2: {"owner": "DeepClaude", "name": "DeepClaude", "stars": "OSS",
       "desc": "Dùng Claude Code với model chi phí thấp hơn nhiều lần, giữ chất lượng suy luận.",
       "tags": ["Tiết kiệm", "Mã nguồn mở", "Reasoning"], "btn": "Tải miễn phí"},
   3: {"title": "~/deepclaude", "lines": [("$", "git clone <repo> && cd deepclaude"), ("$", "./run.sh"), ("ok", "Sẵn sàng dùng")]},
   4: {"items": [("Cấu hình model", ""), ("Kết hợp reasoning", ""), ("Tiết kiệm chi phí", "")]},
   5: {"left": ("Trả phí cao", ["Tốn tiền", "Khoá nhà cung cấp"]),
       "right": ("DeepClaude", ["Rẻ hơn nhiều lần", "Linh hoạt model", "Mã nguồn mở"])},
   6: {"items": ["TIẾT KIỆM", "MÃ NGUỒN MỞ", "LINH HOẠT", "AI"]}},
  {"DeepClaude": "đip clốt", "Claude": "clốt", "model": "mô đồ", "reasoning": "ri dơ ning", "AI": "ây ai"})

J["voicebox-studio"] = ("tool-walkthrough", "tech",
  ["Bạn muốn tạo giọng nói AI mà chạy hoàn toàn trên máy mình?",
   "Voicebox là studio giọng nói AI mã nguồn mở.",
   "Gói luôn tạo giọng, thu âm và đọc chính tả.",
   "Cài đặt và chạy ngay trên máy bạn.",
   "Đầy đủ tính năng cho việc xử lý giọng nói.",
   "Gửi giọng lên cloud thì lo, chạy local thì yên tâm.",
   "Miễn phí, mã nguồn mở, riêng tư.",
   "Vào GitHub Voicebox để thử. Theo dõi SEOSONA."],
  [("Giọng nói AI", "chạy local?"), ("Voicebox", "studio giọng nói"), ("Tạo · thu", "· đọc chính tả"),
   ("Cài đặt", "ngay trên máy"), ("Tính năng", "đầy đủ"), ("Cloud", "hay Local?"),
   ("Miễn phí", "& riêng tư"), ("Theo dõi SEOSONA", "xem thêm")],
  {0: {"big": "100%", "label": "CHẠY TRÊN MÁY BẠN"},
   2: {"owner": "Voicebox", "name": "Voicebox", "stars": "OSS",
       "desc": "Studio giọng nói AI mã nguồn mở: tạo giọng, thu âm, đọc chính tả — chạy local.",
       "tags": ["Local", "Mã nguồn mở", "Giọng nói AI"], "btn": "Tải miễn phí"},
   3: {"title": "~/voicebox", "lines": [("$", "git clone <repo> && cd voicebox"), ("$", "python app.py"), ("ok", "Studio sẵn sàng")]},
   4: {"items": [("Tạo giọng AI", ""), ("Thu âm", ""), ("Đọc chính tả", "")]},
   5: {"left": ("Giọng nói trên cloud", ["Tốn phí", "Lộ dữ liệu giọng"]),
       "right": ("Voicebox local", ["Miễn phí", "Riêng tư 100%", "Đầy đủ tính năng"])},
   6: {"items": ["LOCAL", "MÃ NGUỒN MỞ", "RIÊNG TƯ", "GIỌNG AI"]}},
  {"Voicebox": "vois bóc", "AI": "ây ai", "local": "lâu cồ", "cloud": "cờ lao"})

J["opensource-roundup"] = ("resource-list", "news",
  ["Những dự án mã nguồn mở bạn nên biết, phần năm mươi ba.",
   "Tổng hợp các repo đang được cộng đồng AI chú ý.",
   "Mỗi dự án một ý tưởng đáng để thử.",
   "Bên trong có đủ chủ đề từ tool tới agent.",
   "Lấy về chỉ với một lệnh git clone.",
   "Cộng đồng đóng góp liên tục mỗi ngày.",
   "Miễn phí, mã nguồn mở, học được nhiều.",
   "Theo dõi SEOSONA để xem các phần tiếp theo."],
  [("Mã nguồn mở", "nên biết #53"), ("Tổng hợp", "repo hot"), ("Mỗi dự án", "1 ý tưởng"),
   ("Bên trong", "có gì?"), ("Cách lấy", "1 lệnh git"), ("Cộng đồng", "đóng góp mỗi ngày"),
   ("Miễn phí", "& học được nhiều"), ("Theo dõi SEOSONA", "phần tiếp theo")],
  {2: {"owner": "SEOSONA", "name": "Open Source #53", "stars": "TUYỂN",
       "desc": "Tuyển tập các dự án mã nguồn mở đang được cộng đồng AI chú ý — phần 53.",
       "tags": ["Tuyển tập", "AI", "Mã nguồn mở"], "btn": "Xem danh sách"},
   3: {"items": [("Tool AI hữu ích", ""), ("AI Agent mẫu", ""), ("Thư viện mới", ""), ("Đáng theo dõi", "")]},
   4: {"title": "~/awesome", "lines": [("$", "git clone <repo>"), ("ok", "Khám phá ngay")]},
   5: {"big": "#53", "label": "PHẦN MỚI NHẤT"},
   6: {"items": ["TUYỂN TẬP", "MÃ NGUỒN MỞ", "AI", "MỚI MỖI TUẦN"]}},
  {"repo": "rê pô", "git": "gít", "AI": "ây ai"})

if __name__ == "__main__":
    sel = sys.argv[1] if len(sys.argv) > 1 else None
    for slug, (tpl, mood, SEG, HEAD, DATA, LEX) in J.items():
        if sel and slug != sel: continue
        print(f"\n===== {slug} ({tpl}, bgm={mood}) =====")
        content = compose(tpl, segments=SEG, headings=HEAD, scene_data=DATA, lexicon=LEX)
        nc.make_video_from_template(tpl, content, os.path.join(OUT, slug),
                                    output=os.path.join(OUT, slug + ".mp4"), music=mood)
    print("\nDONE")
