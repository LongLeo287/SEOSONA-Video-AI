# -*- coding: utf-8 -*-
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN")); sys.path.insert(0, ROOT)
from scene_composer import compose
import native_composer as nc
OUT = os.path.join(ROOT, "8_WORKSPACE", "clones")

# 1) benchmark-news — Gemini SQL 80% (stats + feature + compare + bignum)
SEG1 = ["Gemini vừa vượt mốc tám mươi phần trăm benchmark viết SQL.",
        "Bạn hỏi bằng ngôn ngữ tự nhiên, nó trả về câu SQL chuẩn.",
        "Những con số ấn tượng từ Gemini SQL phiên bản hai.",
        "Viết SQL bằng tay thì mệt, hỏi Gemini thì nhanh gọn.",
        "Vì sao Gemini SQL hai đáng chú ý.",
        "Một bước tiến lớn cho truy vấn dữ liệu bằng AI.",
        "Nhanh, chính xác, hỗ trợ nhiều cơ sở dữ liệu.",
        "Theo dõi SEOSONA để xem thêm tin AI mỗi ngày."]
HEAD1 = [("Gemini SQL", "80% benchmark"), ("Hỏi tự nhiên", "ra SQL chuẩn"), ("Con số", "ấn tượng"),
         ("Tay hay AI?", "đâu nhanh hơn"), ("Vì sao", "đáng chú ý"), ("Bước tiến", "truy vấn AI"),
         ("Nhanh & chính xác", "đa CSDL"), ("Theo dõi SEOSONA", "xem thêm mỗi ngày")]
DATA1 = {0: {"big": "80%", "label": "BENCHMARK VIẾT SQL"},
         2: {"items": [("80%", "độ chính xác"), ("2.0", "phiên bản"), ("NL→SQL", "ngôn ngữ tự nhiên")]},
         3: {"left": ("Viết SQL tay", ["Tốn thời gian", "Dễ sai cú pháp", "Phải thuộc schema"]),
             "right": ("Gemini SQL 2", ["Hỏi tự nhiên", "Tự sinh SQL", "Chính xác cao"])},
         4: {"items": [("🎯", "Chính xác", "80% benchmark"), ("⚡", "Nhanh", "trả lời tức thì"), ("🗣️", "Tự nhiên", "không cần học SQL")]},
         5: {"big": "2.0", "label": "GEMINI SQL PHIÊN BẢN MỚI"},
         6: {"items": ["NHANH", "CHÍNH XÁC", "ĐA CSDL", "GOOGLE"]}}
LEX1 = {"Gemini": "giê mi nai", "SQL": "ét qiu eo", "benchmark": "ben mác", "AI": "ây ai", "schema": "sờ kê ma", "NL": "en eo"}

# 2) opinion-insight — AI & trí tuệ con người (quote + feature + tip)
SEG2 = ["Khi AI lấy đi trí tuệ của con người, nó sẽ trả lại những gì?",
        "AI làm thay những việc lặp lại và tính toán nặng nhọc.",
        "Nhưng phần quý giá nhất, nó để lại cho ta.",
        "AI đang thay đổi cách chúng ta làm việc mỗi ngày.",
        "Một điều đáng để ghi nhớ.",
        "Phần mà AI khó thay thế được nhất.",
        "Theo dõi SEOSONA để cùng suy ngẫm về AI."]
HEAD2 = [("Khi AI lấy đi", "trí tuệ?"), ("AI làm thay", "việc lặp lại"), ("Phần quý nhất", "để lại cho ta"),
         ("AI thay đổi", "cách ta làm việc"), ("Điều", "đáng ghi nhớ"), ("Sáng tạo", "AI khó thay"),
         ("Theo dõi SEOSONA", "cùng suy ngẫm")]
DATA2 = {2: {"text": "AI lấy đi việc lặp lại, trả lại cho ta thời gian để sáng tạo và tư duy sâu.", "by": "Góc nhìn SEOSONA"},
         3: {"items": [("🧠", "Tư duy", "tập trung việc khó"), ("⏳", "Thời gian", "bớt việc tay chân"), ("🎨", "Sáng tạo", "phần con người giữ lại")]},
         4: {"title": "GHI NHỚ", "text": "Đừng đua tốc độ với AI — hãy dẫn đầu ở tư duy và sáng tạo."},
         5: {"big": "Sáng tạo", "label": "PHẦN AI KHÓ THAY THẾ NHẤT"}}
LEX2 = {"AI": "ây ai"}

JOBS = [("gemini-sql-benchmark", "benchmark-news", SEG1, HEAD1, DATA1, LEX1),
        ("ai-and-human-mind", "opinion-insight", SEG2, HEAD2, DATA2, LEX2)]

if __name__ == "__main__":   # guard so importing JOBS doesn't trigger a render
    sel = sys.argv[1] if len(sys.argv) > 1 else None
    for slug, tpl, SEG, HEAD, DATA, LEX in JOBS:
        if sel and slug != sel: continue
        print(f"\n===== {slug} ({tpl}) =====")
        content = compose(tpl, segments=SEG, headings=HEAD, scene_data=DATA, lexicon=LEX)
        nc.make_video_from_template(tpl, content, os.path.join(OUT, slug), output=os.path.join(OUT, slug + ".mp4"))
    print("\nDONE")
