# -*- coding: utf-8 -*-
"""SEO demo — prove the engine makes SEO/Marketing videos (SEOSONA's core domain),
not just AI/dev. Uses the brand's own 'SEO truyền thống vs SEO thời AI' framing."""
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN")); sys.path.insert(0, ROOT)
from scene_composer import compose
import native_composer as nc
OUT = os.path.join(ROOT, "8_WORKSPACE", "clones")
J = {}

# 1) SEO thời AI — từ Top 10 sang được AI trích dẫn (seo-explainer)
J["seo-ai-shift"] = ("seo-explainer", "news",
  ["Lên Top 10 Google không còn là đích đến cuối cùng.",
   "Vì khách hàng giờ hỏi thẳng AI thay vì lướt mười kết quả.",
   "SEO truyền thống nhắm Top 10, SEO thời AI nhắm được AI trích dẫn.",
   "Cách để AI chọn trích dẫn nội dung của bạn.",
   "Những nơi nội dung của bạn cần xuất hiện.",
   "Một điều cốt lõi cần ghi nhớ.",
   "Đây là kỷ nguyên tối ưu cho công cụ tạo sinh.",
   "Theo dõi SEOSONA để làm chủ SEO thời AI."],
  [("Top 10 Google", "không còn là đích?"), ("Khách hàng", "giờ hỏi AI"), ("SEO truyền thống", "vs SEO thời AI"),
   ("Cách tối ưu", "cho AI trích dẫn"), ("Xuất hiện", "ở đâu?"), ("Điều", "cốt lõi"),
   ("GEO", "kỷ nguyên mới"), ("Theo dõi SEOSONA", "làm chủ SEO thời AI")],
  {0: {"big": "Top 10?", "label": "KHÔNG CÒN LÀ ĐÍCH CUỐI CÙNG"},
   2: {"left": ("SEO truyền thống", ["Mục tiêu Top 10 Google", "Tập trung từ khoá volume lớn", "Lên trang kết quả"]),
       "right": ("SEO thời AI", ["Được AI trích dẫn", "Xuất hiện trong AI Overview", "Nội dung đủ tin cậy"])},
   3: {"items": [("Nội dung đủ tin cậy", ""), ("Trả lời trực tiếp câu hỏi", ""),
                 ("Cấu trúc rõ cho AI đọc", ""), ("Tăng uy tín thương hiệu", "")]},
   4: {"items": [("🤖", "AI Overview", "ngay đầu trang Google"), ("💬", "ChatGPT & AI Mode", "được trích làm nguồn"),
                 ("🏆", "E-E-A-T", "uy tín & đáng tin")]},
   5: {"title": "GHI NHỚ", "text": "Đừng chỉ tối ưu cho Google — hãy tối ưu để AI tin và trích dẫn bạn."},
   6: {"big": "GEO", "label": "TỐI ƯU CHO CÔNG CỤ TẠO SINH"}},
  {"SEO": "sê ô", "AI": "ây ai", "Google": "gu gồ", "GEO": "giê ô", "ChatGPT": "chát gi pi ti",
   "Overview": "âu vơ viu", "Top": "tóp"})

# 2) Google AI Overview thay đổi traffic (seo-explainer, góc tin tức)
J["seo-ai-overview"] = ("seo-explainer", "news",
  ["Google đưa AI Overview lên đầu trang kết quả tìm kiếm.",
   "Câu trả lời hiện ngay, người dùng ít click vào website hơn.",
   "Traffic kiểu cũ giảm, nhưng cơ hội mới xuất hiện.",
   "Cách giữ lưu lượng trong thời AI Overview.",
   "Những gì thương hiệu cần làm ngay.",
   "Một điều quan trọng cần nhớ.",
   "Thích nghi sớm là lợi thế lớn.",
   "Theo dõi SEOSONA để bắt kịp thay đổi SEO."],
  [("Google", "AI Overview"), ("Câu trả lời", "hiện ngay"), ("Traffic cũ giảm", "cơ hội mới"),
   ("Cách giữ", "lưu lượng"), ("Thương hiệu", "cần làm gì?"), ("Điều", "cần nhớ"),
   ("Thích nghi sớm", "= lợi thế"), ("Theo dõi SEOSONA", "bắt kịp SEO")],
  {0: {"big": "AI", "label": "OVERVIEW LÊN ĐẦU TÌM KIẾM"},
   2: {"left": ("Tìm kiếm cũ", ["10 link xanh", "Phải click mới có câu trả lời", "Traffic về website"]),
       "right": ("AI Overview", ["Trả lời ngay đầu trang", "Ít click hơn", "Cần được AI trích dẫn"])},
   3: {"items": [("Nội dung trả lời trực tiếp", ""), ("Tối ưu cho đoạn trích", ""),
                 ("Xây thương hiệu được nhắc tên", ""), ("Đa kênh, không chỉ Google", "")]},
   4: {"items": [("📉", "Traffic cũ", "có thể giảm"), ("✍️", "Nội dung sâu", "đáng được trích"),
                 ("📣", "Thương hiệu", "được AI nhắc tên")]},
   5: {"title": "GHI NHỚ", "text": "Mục tiêu mới không chỉ là click — mà là được AI nhắc và tin tưởng."},
   6: {"big": "Sớm", "label": "THÍCH NGHI = LỢI THẾ CẠNH TRANH"}},
  {"SEO": "sê ô", "AI": "ây ai", "Google": "gu gồ", "Overview": "âu vơ viu", "traffic": "trép phích"})

if __name__ == "__main__":
    sel = sys.argv[1] if len(sys.argv) > 1 else None
    for slug, (tpl, mood, SEG, HEAD, DATA, LEX) in J.items():
        if sel and slug != sel: continue
        print(f"\n===== {slug} ({tpl}, bgm={mood}) =====")
        content = compose(tpl, segments=SEG, headings=HEAD, scene_data=DATA, lexicon=LEX)
        nc.make_video_from_template(tpl, content, os.path.join(OUT, slug),
                                    output=os.path.join(OUT, slug + ".mp4"), music=mood)
    print("\nDONE")
