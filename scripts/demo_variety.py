# -*- coding: utf-8 -*-
"""Variety demo — hero bg + chart + mockup + feature + compare + tip + slower CTA.
Shows the engine is NOT one monotonous layout. Topic: Kimi K2.7 HighSpeed."""
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN")); sys.path.insert(0, ROOT)
import native_composer as nc
OUT = os.path.join(ROOT, "8_WORKSPACE", "clones")

S = [
    {"seg": "Kimi K2.7 HighSpeed nhanh gấp sáu lần bản tiêu chuẩn.", "kicker": "TIN NÓNG",
     "h1": "Kimi HighSpeed", "h2": "nhanh gấp 6×", "acc": "orange", "hero": True,
     "comp": ("bignum", {"big": "6×", "label": "NHANH HƠN BẢN THƯỜNG"})},
    {"seg": "Một bản tăng tốc dành riêng cho việc viết code.", "kicker": "SỰ KIỆN",
     "h1": "Bản tăng tốc", "h2": "cho coding", "acc": "blue"},
    {"seg": "Nhìn vào biểu đồ tốc độ giữa hai bản.", "kicker": "BIỂU ĐỒ",
     "h1": "Tốc độ", "h2": "trực quan", "acc": "green",
     "comp": ("chart", {"title": "Tốc độ phản hồi", "items": [
        ("HighSpeed", 100, "6×"), ("K2.7 thường", 17, "1×")]})},
    {"seg": "Bảng thông số nhanh của phiên bản mới.", "kicker": "THÔNG SỐ",
     "h1": "Tổng quan", "h2": "phiên bản", "acc": "blue",
     "comp": ("mockup", {"url": "kimi.ai/highspeed", "tiles": [
        ("6×", "nhanh hơn"), ("K2.7", "phiên bản"), ("Code", "tối ưu"), ("Giữ", "chất lượng")]})},
    {"seg": "Vì sao bản HighSpeed đáng thử ngay.", "kicker": "ĐIỂM CHÍNH",
     "h1": "Vì sao", "h2": "đáng thử", "acc": "orange",
     "comp": ("feature", {"items": [("⚡", "Nhanh", "gấp 6 lần"), ("🧩", "Coding", "tối ưu cho code"), ("🎯", "Chất lượng", "không đổi")]})},
    {"seg": "Đặt bản thường cạnh HighSpeed trên cùng tác vụ.", "kicker": "SO SÁNH",
     "h1": "Thường", "h2": "vs HighSpeed", "acc": "green",
     "comp": ("compare", {"left": ("K2.7 thường", ["Tốc độ chuẩn", "Chờ lâu hơn"]),
                          "right": ("HighSpeed", ["Nhanh 6 lần", "Tức thì", "Giữ chất lượng"])})},
    {"seg": "Tốc độ cao giúp vòng lặp viết code nhanh và mượt hơn.", "kicker": "GHI NHỚ",
     "h1": "Tốc độ", "h2": "= năng suất", "acc": "blue",
     "comp": ("tip", {"title": "GHI NHỚ", "text": "Phản hồi nhanh giúp vòng lặp code ngắn lại — làm việc đỡ ngắt mạch."})},
    {"seg": "Theo dõi SEOSONA để xem thêm tin AI mỗi ngày.", "kicker": "SEOSONA AI",
     "h1": "Theo dõi SEOSONA", "h2": "xem thêm mỗi ngày", "acc": "blue",
     "comp": ("cta", {"line": "Tin & thủ thuật AI mỗi ngày", "btn": "👉 Theo dõi SEOSONA"})},
]
LEX = {"Kimi": "ki mi", "HighSpeed": "hai sì pít", "K2.7": "ca hai chấm bảy", "coding": "cô đinh", "AI": "ây ai", "code": "cốt"}

nc.make_video_custom(os.path.join(OUT, "kimi-variety"), S, lexicon=LEX, music="upbeat",
                     output=os.path.join(OUT, "kimi-variety.mp4"))
