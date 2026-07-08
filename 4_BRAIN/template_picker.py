# -*- coding: utf-8 -*-
"""Pick the best video TEMPLATE (scene-arc archetype) for a content brief by keyword.

The library `7_ASSETS/templates/*.json` now has 20 archetypes. This maps a title/topic/brief → the
archetype whose scene arc fits it, so auto-generated videos vary their STRUCTURE (not one fixed arc).
First match wins → most specific rules first. Returns a template name, or `fallback` if nothing matches.
Mirror of `block_picker`, one level up (template = the whole plan; block = one enriching scene).
"""
import os

# (keywords, template) — content cue → the archetype that frames it best. Vietnamese + English.
_RULES = [
    (("top 5", "top 7", "top 10", "danh sách", "liệt kê", "5 công cụ", "7 cách", "những công cụ"), "listicle-top5"),
    (("vs ", " vs", "so sánh", "đối đầu", "khác nhau giữa", "nên chọn", "hay là"), "versus-deep"),
    (("lầm tưởng", "ngộ nhận", "sự thật", "đã chết", "có thật sự", "hiểu lầm", "myth"), "myth-buster"),
    (("case study", "câu chuyện", "thương hiệu", "đã tăng", "nhờ áp dụng", "thực chiến"), "case-study"),
    (("trước và sau", "before", "after", "lột xác", "biến đổi", "thay đổi ngoạn mục"), "transformation"),
    (("hỏi đáp", "câu hỏi thường gặp", "q&a", "faq", "giải đáp"), "faq"),
    (("ra mắt", "công bố", "vừa phát hành", "launch", "phiên bản mới", "cập nhật lớn"), "launch"),
    (("xu hướng", "trend", "đang lên", "mới nổi", "tương lai của", "sắp tới"), "trend-alert"),
    (("hướng dẫn", "tutorial", "cách làm", "từng bước", "step by step", "cài đặt"), "deep-tutorial"),
    (("mẹo nhanh", "thủ thuật", "1 mẹo", "tip nhanh", "bí kíp"), "quick-tip"),
    # existing content archetypes
    (("seo", "marketing", "ranking", "geo", "aeo", "google update"), "seo-explainer"),
    (("benchmark", "điểm số", "vượt", "kỷ lục", "nhanh gấp"), "benchmark-news"),
    (("góc nhìn", "quan điểm", "theo tôi", "trí tuệ", "triết lý"), "opinion-insight"),
    (("khái niệm", "là gì", "giải thích", "cơ chế", "hoạt động thế nào"), "insight-explainer"),
    (("tài nguyên", "kho ", "tổng hợp", "free", "miễn phí list"), "resource-list"),
]


# the 10 new content-shape archetypes (vs the older news/repo templates) — used to gate auto-selection
NEW_ARCHETYPES = {"listicle-top5", "versus-deep", "myth-buster", "case-study", "transformation",
                  "faq", "launch", "trend-alert", "deep-tutorial", "quick-tip"}


def pick_template(text, fallback="insight-explainer"):
    """Return the archetype template name best fitting `text` (a title/brief). `fallback` if no strong match."""
    if not text:
        return fallback
    low = " " + text.lower().replace("-", " ").replace("_", " ") + " "  # so 'top-10'/'x_vs_y' match
    for kws, tpl in _RULES:
        if any(k in low for k in kws):
            return tpl
    return fallback


if __name__ == "__main__":
    for t in ["Top 5 công cụ AI miễn phí", "ChatGPT vs Claude: nên chọn cái nào",
              "SEO đã chết chưa? Sự thật 2026", "Hướng dẫn cài n8n từng bước",
              "Câu chuyện 1 shop tăng 300% doanh thu", "Xu hướng GEO đang lên"]:
        print(f"  {pick_template(t):20} ← {t}")
