"""Regression test for discovery._relevant — the on-domain filter for the unattended feed.

Bug fixed: DOMAIN_KW matched short keywords as bare substrings, so 'ai ' caught the trailing
'-ai' in extremely common Vietnamese words (hai/sai/tai/vai/mai/chai = two/wrong/ear/role/
tomorrow/bottle) and flooded the autonomous discovery feed with off-domain news. Short ambiguous
keywords now match as WHOLE WORDS (\\b, re.UNICODE).
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import discovery as d  # noqa: E402


class RelevanceFilterTests(unittest.TestCase):
    OFF_TOPIC = [
        "Hai người đàn ông cướp ngân hàng",   # 'hai' (two) — must NOT match 'ai'
        "Đáp án sai của thí sinh",             # 'sai' (wrong)
        "Tai nạn giao thông nghiêm trọng",     # 'tai' (accident)
        "Vai trò của phụ huynh",               # 'vai' (role)
        "Giá chai nước tăng cao",              # 'chai' (bottle)
        "Ngày mai trời nắng đẹp",              # 'mai' (tomorrow)
        "Bàn thắng phút cuối của đội tuyển",   # sports, no domain word
    ]
    ON_TOPIC = [
        "Google cập nhật thuật toán SEO",
        "AI đang thay đổi ngành marketing",    # standalone 'ai'
        "Cách viết content chuẩn SEO",
        "ChatGPT và tương lai tìm kiếm",
        "Ứng dụng LLM trong RAG",              # whole-word llm + rag
        "Chiến lược GPT cho doanh nghiệp",
    ]

    def test_off_topic_rejected(self):
        for t in self.OFF_TOPIC:
            self.assertFalse(d._relevant(t), f"should be OFF-domain: {t!r}")

    def test_on_topic_kept(self):
        for t in self.ON_TOPIC:
            self.assertTrue(d._relevant(t), f"should be ON-domain: {t!r}")

    def test_excluded_collision_still_blocked(self):
        # the Park Hang-seo footballer collides with 'seo' but EXCLUDE_KW must win.
        self.assertFalse(d._relevant("HLV Park Hang-seo dẫn dắt tuyển bóng đá"))


if __name__ == "__main__":
    unittest.main()
