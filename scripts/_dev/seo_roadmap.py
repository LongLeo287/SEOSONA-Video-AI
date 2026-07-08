# -*- coding: utf-8 -*-
"""SEO video — "Lộ trình làm SEO thời AI" (roadmap). FREEFORM.
~11 câu đầy đủ -> 45–55s (theo skill: 8–12 câu cho 45–60s). Tên file = caption đăng."""
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN")); sys.path.insert(0, ROOT)
import native_composer as nc

SCENES = [
    {"seg": "Làm SEO thời AI mà không có lộ trình rõ ràng thì rất dễ lạc hướng và lãng phí công sức.",
     "kicker": "SEO 2025", "h1": "Lộ trình SEO", "h2": "thời AI", "acc": "orange", "hero": True,
     "comp": ("bignum", {"big": "5 bước", "label": "LỘ TRÌNH SEO THỜI AI"})},
    {"seg": "Khi khách hàng hỏi thẳng trợ lý AI thay vì lướt mười kết quả trên Google, cách làm SEO buộc phải thay đổi.",
     "kicker": "BỐI CẢNH", "h1": "Khách hàng", "h2": "giờ hỏi AI", "acc": "blue"},
    {"seg": "Trước đây ta nhắm vào Top 10 và chạy theo từ khoá có lượng tìm kiếm lớn.",
     "kicker": "CŨ vs MỚI", "h1": "SEO truyền thống", "h2": "vs SEO thời AI", "acc": "blue",
     "comp": ("compare", {"left": ("SEO truyền thống", ["Mục tiêu Top 10 Google", "Chạy theo từ khoá volume", "Lên trang kết quả"]),
                          "right": ("SEO thời AI", ["Được AI trích dẫn", "Xuất hiện trong AI Overview", "Nội dung đủ tin cậy"])})},
    {"seg": "Giờ mục tiêu mới là được AI chọn và trích dẫn nội dung của bạn làm nguồn đáng tin.",
     "kicker": "MỤC TIÊU MỚI", "h1": "Được AI", "h2": "trích dẫn", "acc": "green"},
    {"seg": "Và đây là năm bước trong lộ trình, làm tuần tự từ trên xuống dưới.",
     "kicker": "LỘ TRÌNH", "h1": "Làm theo", "h2": "thứ tự", "acc": "green",
     "comp": ("steps", {"items": [
        ("Nghiên cứu ý định tìm kiếm", "hiểu người dùng thật sự cần gì"),
        ("Nội dung đáng tin E-E-A-T", "trả lời sâu, có chuyên môn"),
        ("Tối ưu cho AI đọc & trích", "heading rõ, schema, đoạn trích"),
        ("Xây uy tín thương hiệu", "được nhắc tên, backlink chất"),
        ("Đo lường & tối ưu liên tục", "thứ hạng + lượt AI trích dẫn")]})},
    {"seg": "Quan trọng nhất là nội dung phải đủ chuyên môn và đáng tin cậy, đúng tinh thần E-E-A-T của Google.",
     "kicker": "QUAN TRỌNG NHẤT", "h1": "Nội dung", "h2": "đủ uy tín", "acc": "orange",
     "comp": ("feature", {"items": [("🎯", "Ý định người dùng", "đặt nhu cầu thật lên đầu"),
                                    ("🤖", "Thân thiện với AI", "để AI hiểu & trích nội dung"),
                                    ("🏆", "Uy tín thật", "E-E-A-T, không nhồi từ khoá")]})},
    {"seg": "Đừng quên cấu trúc nội dung rõ ràng để AI dễ đọc và lấy đoạn trích chính xác.",
     "kicker": "MẸO", "h1": "Cấu trúc", "h2": "cho AI đọc", "acc": "blue",
     "comp": ("tip", {"title": "GHI NHỚ", "text": "SEO thời AI = nội dung giải đáp đúng + đủ uy tín để AI tin và trích dẫn bạn."})},
    {"seg": "Cuối cùng, hãy đo lường cả thứ hạng truyền thống lẫn số lần bạn được AI nhắc tên.",
     "kicker": "ĐO LƯỜNG", "h1": "Đo cả hai", "h2": "chỉ số", "acc": "orange",
     "comp": ("bignum", {"big": "2 chỉ số", "label": "THỨ HẠNG + LƯỢT AI TRÍCH DẪN"})},
    {"seg": "Đi đúng lộ trình này, bạn sẽ được cả Google và AI cùng ưu tiên nội dung của mình.",
     "kicker": "TÁC ĐỘNG", "h1": "Google + AI", "h2": "cùng ưu tiên bạn", "acc": "green",
     "comp": ("bignum", {"big": "Google + AI", "label": "CÙNG CHỌN NỘI DUNG CỦA BẠN"})},
    {"seg": "Theo dõi SEOSONA để nhận trọn bộ lộ trình và thủ thuật SEO thời AI mỗi ngày.",
     "kicker": "SEOSONA AI", "h1": "Theo dõi SEOSONA", "h2": "làm chủ SEO thời AI", "acc": "blue",
     "comp": ("cta", {"line": "Lộ trình & thủ thuật SEO mỗi ngày", "btn": "👉 Theo dõi SEOSONA"})},
]
LEX = {"SEO": "sê ô", "AI": "ây ai", "Google": "gu gồ", "GEO": "giê ô", "E-E-A-T": "i i ây ti",
       "schema": "sờ kê ma", "backlink": "béc linh", "Overview": "âu vơ viu", "Top": "tóp"}

# RULE #7: tên file = caption đăng (hook có dấu + hashtag, tránh ký tự cấm)
CAPTION = "Lộ trình làm SEO thời AI - 5 bước được cả Google và AI ưu tiên #SEO #SEOthoiAI #digitalmarketing #SEOSONA (9x16)"
out = os.path.join(ROOT, "8_WORKSPACE", "clones", CAPTION + ".mp4")
nc.make_video_custom(os.path.join(ROOT, "8_WORKSPACE", "clones", "seo-roadmap-ai"), SCENES,
                     lexicon=LEX, music="news", output=out)
# also keep a stable short name copy for convenience
import shutil
if os.path.exists(out): shutil.copy(out, os.path.join(ROOT, "8_WORKSPACE", "clones", "seo-roadmap-ai.mp4"))
