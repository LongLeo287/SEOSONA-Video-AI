# -*- coding: utf-8 -*-
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN")); sys.path.insert(0, ROOT)
import video_engine as ve, native_composer as nc
script = ("Google vừa tung bản cập nhật lớn ảnh hưởng bốn mươi phần trăm kết quả tìm kiếm. "
          "Khi người dùng hỏi thẳng trợ lý AI thay vì lướt Google, SEO buộc phải thay đổi. "
          "Trước đây ta nhắm Top mười và chạy theo lượng tìm kiếm của từ khoá. "
          "Mẹo quan trọng nhất là nội dung phải đủ uy tín để AI trích dẫn bạn. "
          "Hơn sáu mươi phần trăm truy vấn giờ kèm câu trả lời AI ngay trên trang. "
          "Theo dõi SEOSONA để cập nhật thủ thuật SEO mỗi ngày.")
segs, scenes = ve.plan_scenes(script)
out = os.path.join(ROOT, "8_WORKSPACE", "clones", "_test-planner.mp4")
nc.make_video(os.path.join(ROOT, "8_WORKSPACE", "clones", "_test-planner"), segs, scenes,
              output=out, brand="seosona", music="news")
