# -*- coding: utf-8 -*-
"""Freeform demo — build a video with NO template, components assembled by content."""
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN")); sys.path.insert(0, ROOT)
import native_composer as nc

# "Kimi K2.7 HighSpeed nhanh gấp 6 lần" — a CUSTOM mix: bignum→text→stats→compare→feature→tip→cta
SCENES = [
    {"seg": "Kimi K2.7 HighSpeed nhanh gấp sáu lần bản tiêu chuẩn.", "kicker": "TIN NÓNG",
     "h1": "Kimi HighSpeed", "h2": "nhanh gấp 6×", "acc": "orange", "comp": ("bignum", {"big": "6×", "label": "NHANH HƠN BẢN THƯỜNG"})},
    {"seg": "Kimi vừa ra mắt bản tăng tốc dành riêng cho việc viết code.", "kicker": "SỰ KIỆN",
     "h1": "Bản tăng tốc", "h2": "cho coding", "acc": "blue"},
    {"seg": "Những con số đáng chú ý của phiên bản mới.", "kicker": "CON SỐ",
     "h1": "Con số", "h2": "ấn tượng", "acc": "blue",
     "comp": ("stats", {"items": [("6×", "tốc độ"), ("K2.7", "phiên bản"), ("HighSpeed", "chế độ mới")]})},
    {"seg": "Đặt bản thường cạnh HighSpeed trên cùng một tác vụ.", "kicker": "SO SÁNH",
     "h1": "Thường", "h2": "vs HighSpeed", "acc": "green",
     "comp": ("compare", {"left": ("K2.7 thường", ["Tốc độ chuẩn", "Chờ lâu hơn", "Cùng kết quả"]),
                          "right": ("HighSpeed", ["Nhanh 6 lần", "Phản hồi tức thì", "Chất lượng giữ nguyên"])})},
    {"seg": "Vì sao bản HighSpeed đáng để thử ngay.", "kicker": "ĐIỂM CHÍNH",
     "h1": "Vì sao", "h2": "đáng thử", "acc": "orange",
     "comp": ("feature", {"items": [("⚡", "Nhanh", "gấp 6 lần"), ("🧩", "Coding", "tối ưu cho code"), ("🎯", "Chất lượng", "không đổi")]})},
    {"seg": "Tốc độ cao giúp vòng lặp viết code nhanh và mượt hơn.", "kicker": "GHI NHỚ",
     "h1": "Tốc độ", "h2": "= năng suất", "acc": "blue",
     "comp": ("tip", {"title": "GHI NHỚ", "text": "Phản hồi nhanh giúp vòng lặp code ngắn lại — làm việc đỡ ngắt mạch."})},
    {"seg": "Theo dõi SEOSONA để xem thêm tin AI mỗi ngày.", "kicker": "SEOSONA AI",
     "h1": "Theo dõi SEOSONA", "h2": "xem thêm mỗi ngày", "acc": "blue",
     "comp": ("cta", {"line": "Tin & thủ thuật AI mỗi ngày", "btn": "👉 Theo dõi SEOSONA"})},
]
LEX = {"Kimi": "ki mi", "HighSpeed": "hai sì pít", "K2.7": "ca hai chấm bảy", "coding": "cô đinh", "AI": "ây ai"}

nc.make_video_custom(os.path.join(ROOT, "8_WORKSPACE", "clones", "kimi-highspeed"), SCENES,
                     lexicon=LEX, music="news",
                     output=os.path.join(ROOT, "8_WORKSPACE", "clones", "kimi-highspeed.mp4"))
