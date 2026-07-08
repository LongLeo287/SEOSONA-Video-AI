# -*- coding: utf-8 -*-
"""Knowledge video — "Mindset viết content chuẩn SEO" (distilled from D:\SRT real course
transcript). SEOSONA voice: mentor, mindset-first, quality>quantity. Short 9:16, ~50s."""
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN")); sys.path.insert(0, ROOT)
import native_composer as nc

SCENES = [
    {"seg": "Content là yếu tố xếp hạng quan trọng bậc nhất trong SEO, đừng xem nhẹ điều này.",
     "kicker": "CONTENT SEO", "h1": "Content", "h2": "yếu tố số 1", "acc": "orange", "hero": True,
     "comp": ("bignum", {"big": "#1", "label": "YẾU TỐ XẾP HẠNG TRONG SEO"})},
    {"seg": "Chưa từng có website nào content kém chất lượng mà tồn tại bền vững trên Google.",
     "kicker": "SỰ THẬT", "h1": "Content kém", "h2": "không trụ lâu", "acc": "blue"},
    {"seg": "Nhiều người chi rất mạnh cho content nhưng vẫn thất bại, vì sao lại như vậy?",
     "kicker": "NGHỊCH LÝ", "h1": "Chi mạnh", "h2": "vẫn thất bại", "acc": "green"},
    {"seg": "Vấn đề không nằm ở thiếu tiền hay thiếu người viết, mà ở thiếu đúng mindset.",
     "kicker": "GỐC RỄ", "h1": "Thiếu", "h2": "mindset đúng", "acc": "orange",
     "comp": ("compare", {"left": ("Mindset sai", ["Viết càng nhiều càng tốt", "Viết càng dài càng tốt", "Chăm chăm chỉ số tool"]),
                          "right": ("Mindset đúng", ["Giải đúng nhu cầu tìm kiếm", "Chất lượng hơn số lượng", "Lấy người dùng làm trọng tâm"])})},
    {"seg": "Hãy viết để giải quyết đúng vấn đề người dùng đang tìm, chứ không phải để chiều thuật toán.",
     "kicker": "NGUYÊN TẮC", "h1": "Viết cho", "h2": "người dùng", "acc": "blue",
     "comp": ("feature", {"items": [("🎯", "Đúng ý định tìm kiếm", "trả lời thứ họ thật sự cần"),
                                    ("🏆", "Đủ E-E-A-T", "trải nghiệm, chuyên môn, uy tín"),
                                    ("📈", "Bền vững", "an toàn trước mọi thuật toán")]})},
    {"seg": "Nội dung chất lượng, đáng tin mới giúp bạn vừa lên top vừa chuyển đổi được khách hàng.",
     "kicker": "GHI NHỚ", "h1": "Chất lượng", "h2": "mới bền", "acc": "green",
     "comp": ("tip", {"title": "GHI NHỚ", "text": "Mindset đúng quan trọng hơn ngân sách: content chất lượng, giải đúng nhu cầu, lấy người dùng làm trọng tâm."})},
    {"seg": "Theo dõi SEOSONA để học trọn bộ mindset và kỹ thuật viết content chuẩn SEO.",
     "kicker": "SEOSONA AI", "h1": "Theo dõi SEOSONA", "h2": "làm chủ Content SEO", "acc": "blue",
     "comp": ("cta", {"line": "Khóa Content SEO Mastery — học content chuẩn SEO", "btn": "👉 Theo dõi SEOSONA"})},
]
LEX = {"SEO": "sê ô", "E-E-A-T": "i i ây ti", "Google": "gu gồ", "AI": "ây ai", "top": "tóp", "content": "con tần", "website": "web sai"}
CAPTION = "Mindset viết Content chuẩn SEO - đừng chi tiền sai cách #SEO #ContentSEO #SEOSONA (9x16)"
out = os.path.join(ROOT, "8_WORKSPACE", "clones", CAPTION + ".mp4")
nc.make_video_custom(os.path.join(ROOT, "8_WORKSPACE", "clones", "content-mindset-seo"), SCENES,
                     lexicon=LEX, music="insight", output=out)
import shutil
if os.path.exists(out): shutil.copy(out, os.path.join(ROOT, "8_WORKSPACE", "clones", "content-mindset-seo.mp4"))
