# -*- coding: utf-8 -*-
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN")); sys.path.insert(0, ROOT)
import native_composer as nc
SCENES = [
    {"seg": "Học SEO thực chiến cùng Chi Quyết Academy, bắt đầu từ con số không.",
     "kicker": "CQA", "h1": "Học SEO", "h2": "thực chiến", "acc": "blue", "hero": True,
     "comp": ("bignum", {"big": "3 bước", "label": "BẮT ĐẦU LÀM SEO"})},
    {"seg": "Đầu tiên hãy hiểu người dùng tìm kiếm điều gì và vì sao.",
     "kicker": "BƯỚC 1", "h1": "Hiểu", "h2": "người dùng", "acc": "green",
     "comp": ("feature", {"items": [("🔍", "Ý định tìm kiếm", "họ thật sự cần gì"),
                                    ("📝", "Từ khoá gốc", "ngôn ngữ người dùng dùng"),
                                    ("🎯", "Mục tiêu rõ", "đo được kết quả")]})},
    {"seg": "Theo dõi Chi Quyết Academy để học SEO mỗi ngày nhé.",
     "kicker": "CQA", "h1": "Theo dõi", "h2": "Chi Quyết Academy", "acc": "orange",
     "comp": ("cta", {"line": "Học SEO thực chiến mỗi ngày", "btn": "👉 Theo dõi CQA"})},
]
out = os.path.join(ROOT, "8_WORKSPACE", "clones", "_test-cqa.mp4")
nc.make_video_custom(os.path.join(ROOT, "8_WORKSPACE", "clones", "_test-cqa"), SCENES,
                     music="upbeat", output=out, brand="cqa")
