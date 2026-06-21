import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from pipeline_manager import run_pipeline

script = """
Xin chào mọi người. Hôm nay chúng ta sẽ cùng phân tích sự thay đổi của Google Search và OpenAI. 
Người dùng AI Search đang làm thay đổi hoàn toàn luật chơi SEO trong năm 2026. 
Doanh nghiệp của bạn đã sẵn sàng cho kỷ nguyên AI chưa?
"""

run_pipeline(script, brand="cqa", mode="create", aspect_ratio="9:16", project_name="DEMO_CQA_MALE")
