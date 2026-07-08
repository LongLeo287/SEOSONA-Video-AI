# -*- coding: utf-8 -*-
"""Clone batch 5 — final reference videos to complete full coverage of the 30."""
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN")); sys.path.insert(0, ROOT)
from scene_composer import compose
import native_composer as nc
OUT = os.path.join(ROOT, "8_WORKSPACE", "clones")
J = {}

J["claude-skills-lesson"] = ("tool-walkthrough", "tech",
  ["Bạn muốn Claude Code nhớ và lặp lại đúng cách làm của bạn?",
   "Skills giúp biến kinh nghiệm thành năng lực tái sử dụng.",
   "Đóng gói quy trình một lần, dùng lại mãi mãi.",
   "Tạo một skill chỉ với vài bước.",
   "Sau đó gọi lại bất cứ lúc nào.",
   "Làm lại từ đầu thì mệt, có skill thì nhanh.",
   "Miễn phí, có sẵn trong Claude Code.",
   "Theo dõi SEOSONA để học thêm về Claude Code."],
  [("Claude Code", "nhớ cách làm?"), ("Skills", "kinh nghiệm → năng lực"), ("Đóng gói", "1 lần dùng mãi"),
   ("Tạo skill", "vài bước"), ("Gọi lại", "bất cứ lúc nào"), ("Làm lại", "hay dùng skill?"),
   ("Miễn phí", "có sẵn"), ("Theo dõi SEOSONA", "xem thêm")],
  {0: {"big": "Skills", "label": "KINH NGHIỆM → NĂNG LỰC"},
   2: {"owner": "Anthropic", "name": "Claude Code · Skills", "stars": "MẸO",
       "desc": "Đóng gói quy trình/kinh nghiệm thành skill tái sử dụng cho Claude Code.",
       "tags": ["Skill", "Claude Code", "Tái sử dụng"], "btn": "Tìm hiểu"},
   3: {"title": "~/.claude/skills", "lines": [("$", "tạo file SKILL.md"), ("$", "mô tả quy trình của bạn"), ("ok", "Skill sẵn sàng dùng lại")]},
   4: {"items": [("Đóng gói quy trình", ""), ("Gọi lại bất kỳ lúc nào", ""), ("Chia sẻ cho nhóm", "")]},
   5: {"left": ("Làm lại mỗi lần", ["Tốn thời gian", "Hay quên bước", "Khó nhất quán"]),
       "right": ("Dùng Skills", ["Đóng gói 1 lần", "Nhất quán", "Tái sử dụng"])},
   6: {"items": ["SKILL", "TÁI SỬ DỤNG", "CLAUDE CODE", "MIỄN PHÍ"]}},
  {"Claude": "clốt", "Skills": "sờ kiu", "Code": "cốt", "SKILL": "sờ kiu", "AI": "ây ai"})

J["design-md-stitch"] = ("repo-showcase", "tech",
  ["Bạn muốn giao diện đẹp mà không cần thuê designer?",
   "Google Stitch open-source định dạng DESIGN.md.",
   "Bảy mươi brand đẳng cấp được curated sẵn, từ Stripe tới Apple.",
   "Tham khảo phong cách thiết kế thì rối, DESIGN.md thì gọn.",
   "Lấy về chỉ với một lệnh.",
   "Hơn sáu mươi bảy nghìn sao trên GitHub.",
   "Miễn phí, mã nguồn mở.",
   "Vào GitHub DESIGN.md để thử. Theo dõi SEOSONA."],
  [("Giao diện đẹp", "không cần designer?"), ("Google Stitch", "DESIGN.md"), ("70 brand", "curated sẵn"),
   ("Tự mò style", "hay dùng sẵn?"), ("Cách lấy", "1 lệnh"), ("Được tin dùng", "67.8k sao"),
   ("Miễn phí", "& mã nguồn mở"), ("Theo dõi SEOSONA", "xem thêm")],
  {0: {"big": "70", "label": "BRAND ĐẲNG CẤP CURATED"},
   2: {"owner": "Google", "name": "Stitch · DESIGN.md", "stars": "67.8K",
       "desc": "Định dạng DESIGN.md open-source: 70 brand curated (Stripe, Vercel, Linear, Apple...).",
       "tags": ["Design", "70 brand", "Mã nguồn mở"], "btn": "Tải miễn phí"},
   3: {"left": ("Tự mò phong cách", ["Mất thời gian", "Thiếu nhất quán"]),
       "right": ("DESIGN.md", ["70 brand sẵn", "Chuẩn & đẹp", "Mã nguồn mở"])},
   4: {"title": "~/design", "lines": [("$", "lấy DESIGN.md cho dự án"), ("ok", "70 brand sẵn sàng dùng")]},
   5: {"big": "67.8K", "label": "★  GITHUB STARS"},
   6: {"items": ["MIỄN PHÍ", "MÃ NGUỒN MỞ", "70 BRAND", "GOOGLE"]}},
  {"DESIGN": "đi zai", "Stitch": "sờ tích", "Google": "gu gồ", "Stripe": "sờ trai", "Apple": "áp pồ", "AI": "ây ai"})

J["free-llm-api"] = ("resource-list", "news",
  ["Trả tiền API AI mỗi tháng có làm bạn nản?",
   "FreeLLMAPI gom sức mạnh từ các gói miễn phí.",
   "Tổng hợp gần mười bốn nhà cung cấp AI hàng đầu.",
   "Bên trong có đủ model để bạn dùng thử.",
   "Lấy về chỉ với một lệnh.",
   "Cộng đồng đang cực kỳ chú ý trên GitHub.",
   "Miễn phí, mã nguồn mở.",
   "Vào GitHub FreeLLMAPI để thử. Theo dõi SEOSONA."],
  [("Trả tiền API", "mỗi tháng?"), ("FreeLLMAPI", "gói miễn phí"), ("14 nhà", "cung cấp AI"),
   ("Bên trong", "có gì?"), ("Cách lấy", "1 lệnh"), ("Đang gây bão", "trên GitHub"),
   ("Miễn phí", "& mã nguồn mở"), ("Theo dõi SEOSONA", "xem thêm")],
  {2: {"owner": "FreeLLMAPI", "name": "FreeLLMAPI", "stars": "HOT",
       "desc": "Gom các gói miễn phí của gần 14 nhà cung cấp AI hàng đầu vào một chỗ.",
       "tags": ["Miễn phí", "14 nhà cung cấp", "Mã nguồn mở"], "btn": "Xem kho"},
   3: {"items": [("Nhiều nhà cung cấp", ""), ("Gói miễn phí", ""), ("Nhiều model", ""), ("Cập nhật liên tục", "")]},
   4: {"title": "~/freellmapi", "lines": [("$", "git clone <repo>"), ("ok", "14 nhà cung cấp sẵn sàng")]},
   5: {"big": "~14", "label": "NHÀ CUNG CẤP AI MIỄN PHÍ"},
   6: {"items": ["MIỄN PHÍ", "14 NHÀ CC", "MÃ NGUỒN MỞ", "AI"]}},
  {"FreeLLMAPI": "phri eo eo em ây pi ai", "API": "ây pi ai", "LLM": "eo eo em", "model": "mô đồ", "AI": "ây ai"})

J["webapp-no-code"] = ("ai-news-flash", "upbeat",
  ["Đây là 3 công cụ AI làm web-app cho người không chuyên lập trình.",
   "Chỉ cần mô tả ý tưởng, AI dựng app cho bạn.",
   "Không cần biết code vẫn ra sản phẩm.",
   "Một cánh cửa mới cho người làm sản phẩm.",
   "Nhanh, dễ, ai cũng làm được.",
   "Theo dõi SEOSONA để xem chi tiết 3 công cụ."],
  [("3 công cụ AI", "làm web-app"), ("Mô tả ý tưởng", "AI dựng app"), ("Không cần", "biết code"),
   ("Cánh cửa mới", "làm sản phẩm"), ("Nhanh", "& dễ"), ("Theo dõi SEOSONA", "xem chi tiết")],
  {2: {"owner": "Tuyển chọn", "name": "3 công cụ no-code AI", "stars": "TOP 3",
       "desc": "Ba công cụ AI giúp người không chuyên lập trình dựng web-app từ mô tả.",
       "tags": ["No-code", "Web-app", "AI"], "btn": "Xem 3 công cụ"},
   3: {"big": "3", "label": "CÔNG CỤ NO-CODE AI"},
   4: {"items": ["NO-CODE", "TỪ MÔ TẢ", "RA WEB-APP", "DỄ DÙNG"]}},
  {"web-app": "guép áp", "no-code": "nâu cốt", "code": "cốt", "AI": "ây ai"})

J["token-saver-tools"] = ("resource-list", "tech",
  ["Claude Code âm thầm đốt token mỗi lượt vì đọc lại toàn bộ codebase.",
   "Có ba công cụ miễn phí giúp bạn cắt giảm điều đó.",
   "Tối ưu cách agent đọc và ghi nhớ code.",
   "Mỗi công cụ giải quyết một phần lãng phí.",
   "Cài đặt nhanh, dùng được ngay.",
   "Cộng đồng dev đang chia sẻ rất nhiều.",
   "Miễn phí, mã nguồn mở.",
   "Theo dõi SEOSONA để nhận trọn bộ 3 công cụ."],
  [("Claude Code", "đốt token?"), ("3 công cụ", "miễn phí"), ("Tối ưu", "đọc & nhớ code"),
   ("Mỗi công cụ", "1 phần lãng phí"), ("Cài đặt", "nhanh gọn"), ("Cộng đồng", "chia sẻ nhiều"),
   ("Miễn phí", "& mã nguồn mở"), ("Theo dõi SEOSONA", "nhận trọn bộ")],
  {2: {"owner": "Tuyển chọn", "name": "3 tool tiết kiệm token", "stars": "TOP 3",
       "desc": "Ba công cụ miễn phí giúp Claude Code bớt đốt token khi đọc lại codebase.",
       "tags": ["Tiết kiệm token", "Miễn phí", "Claude Code"], "btn": "Nhận 3 công cụ"},
   3: {"items": [("Tối ưu context", ""), ("Ghi nhớ code", ""), ("Bớt đọc lại", "")]},
   4: {"title": "~/tools", "lines": [("$", "cài 3 công cụ"), ("ok", "Tiết kiệm token ngay")]},
   5: {"big": "3", "label": "CÔNG CỤ MIỄN PHÍ"},
   6: {"items": ["TIẾT KIỆM TOKEN", "MIỄN PHÍ", "MÃ NGUỒN MỞ", "CLAUDE CODE"]}},
  {"Claude": "clốt", "token": "tâu cừn", "codebase": "cốt bây", "agent": "ây dần", "AI": "ây ai"})

if __name__ == "__main__":
    sel = sys.argv[1] if len(sys.argv) > 1 else None
    for slug, (tpl, mood, SEG, HEAD, DATA, LEX) in J.items():
        if sel and slug != sel: continue
        print(f"\n===== {slug} ({tpl}, bgm={mood}) =====")
        content = compose(tpl, segments=SEG, headings=HEAD, scene_data=DATA, lexicon=LEX)
        nc.make_video_from_template(tpl, content, os.path.join(OUT, slug),
                                    output=os.path.join(OUT, slug + ".mp4"), music=mood)
    print("\nDONE")
