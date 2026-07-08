# -*- coding: utf-8 -*-
"""Pick a HyperFrames registry block to ENRICH a scene by content — automatically + on-brand.

Design split: the 14 hand-built components (bignum/stats/steps/compare/tip/…) are a CASE LIBRARY —
each is a proven pattern for a content case, the default scaffold for every scene, and the place to add
a NEW case when one shows up. The 97 registry blocks are the BEAUTY layer on top: rendered through
`hf_blocks` which AUTO-BRAND-SKINS them to the SEOSONA palette (blue #2A5BDA / coral #E2724D), so they
match the brand instead of fighting it. This picker chooses a block automatically when a scene's content
clearly calls for one the components can't do as well (real code, a UI mockup, a cinematic beat).

ON by default (auto); opt OUT with `SEOSONA_USE_BLOCKS=0`. Conservative (strong keyword match only) and
the caller caps how many blocks a single video may use. See `2_KNOWLEDGE/hyperframes/FACTORY_BLOCK_PALETTE.md`.
"""
import os
from importlib import import_module

# (keywords, block) — content cue → the registry block that shows it best. First match wins, so the
# MORE SPECIFIC rules go first. All blocks verified present in 5_FRAMEWORK/hf_engine/registry/blocks.
# Keep cues fairly specific so a block only fires when it genuinely fits (still capped per video).
_RULES = [
    # — code / dev —
    (("đoạn mã", "dòng lệnh", "câu lệnh", " terminal", "command line", " code ", "lập trình", "hàm số", "cú pháp"),
     "code-snippet-dark-modern"),
    (("code diff", "so sánh code", "trước và sau khi sửa", "pull request", "thay đổi dòng", "commit"),
     "code-diff"),
    # — money / data —
    (("doanh thu", "lợi nhuận", "kiếm tiền", "triệu đô", "tỷ đồng", "định giá", "gọi vốn", "raised"),
     "apple-money-count"),
    (("biểu đồ", "tăng trưởng", "thống kê", "số liệu", "phần trăm tăng", "benchmark", "tốc độ gấp"),
     "data-chart"),
    # — geography / market —
    (("bản đồ", "thị trường toàn cầu", "các quốc gia", "khu vực", "trên thế giới", "lan rộng"),
     "us-map"),
    # — social proof —
    (("instagram", "lượt theo dõi", "viral", "triệu view", "follower"), "instagram-follow"),
    (("reddit", "thảo luận cộng đồng", "bình luận sôi nổi", "diễn đàn"), "reddit-post"),
    (("spotify", "podcast", "playlist", "nghe nhạc"), "spotify-card"),
    # — UI / product —
    (("giao diện", "ui/ux", " ui ", " app ", "ứng dụng", "thông báo đẩy", "notification", "macos", " ios"),
     "macos-notification"),
    (("liquid glass", "kính mờ", "widget", "ios 26"), "liquid-glass-widgets"),
    (("demo sản phẩm", "showcase", "giới thiệu ứng dụng", "mockup 3d"), "app-showcase"),
    # — process / flow —
    (("quy trình", "luồng xử lý", "sơ đồ", "pipeline", "flowchart", "các bước kết nối"), "flowchart"),
    # — emphasis / transition effects —
    # NOTE: the registry's transition demos (glitch/cinematic-zoom/light-leak/…) are GALLERY cards, not
    # data-driven clips — they render fixed showcase chrome ("Cinematic Zoom / Prompt / SCENE A / 07 14").
    # `hf_blocks` only recolours them, never replaces that text, so overlaying one dumps gallery chrome
    # into a real video. They are barred in `_KNOWN_BAD` below; transitions are handled by effect_library.
    (("tổng kết lại", "lời kết", "đăng ký kênh", "cảm ơn đã xem"), "logo-outro"),
]


def enabled():
    # DEFAULT OFF (2026-07-03): an exhaustive audit found EVERY pickable registry block is a gallery DEMO
    # — it shows hardcoded chrome ("<Name> / Prompt / SCENE A"), fake data (apple-money-count's $5k count-up,
    # us-map's fake census, app-showcase's fitness stats, liquid-glass's widgets), or off-brand artifacts
    # (dark VS-Code theme, "figma.com", a "Pythom" typo). `hf_blocks` only RECOLOURS — it can't inject the
    # scene's real data — so assigning ANY block leaks demo content into a real video ("làm giả"). The
    # data-driven components ([[dataviz-component-family]]) already make videos rich. Re-enable with
    # SEOSONA_USE_BLOCKS=1 ONLY after hf_blocks learns to inject real data + the block is vetted safe.
    return os.environ.get("SEOSONA_USE_BLOCKS", "0") == "1"   # default OFF; opt in with =1


def _exists(name):
    try:
        hb = import_module("hf_blocks")
        return any(b["name"] == name for b in hb.list_blocks())
    except Exception:
        return False


# Registry blocks the picker must NEVER return, for THREE reasons:
#  1) RENDER-FAIL — HyperFrames reports zero duration despite a data-duration attr (verified 2026-07-01).
#  2) GALLERY-CHROME — a showcase DEMO card, not a data-driven clip: renders fixed text ("<Name> / Prompt /
#     SCENE A / NN 14"). `hf_blocks` only recolours, never replaces it, so overlaying composites gallery
#     chrome onto a real video (render-verified 2026-07-02 — cinematic-zoom leaked its prompt text).
#  3) FAKE-DATA — the block shows SPECIFIC hardcoded demo DATA (a $5k money count-up, chart bars, follower
#     counts, a playlist) that a viewer reads as FACTUAL. `hf_blocks` can't inject the scene's real data, so
#     it leaks fabricated figures — "làm giả". Render-verified 2026-07-03: a "Doanh thu" scene got
#     apple-money-count overlaying a fake "$5,169" count-up over the real 47% bignum.
# Extend as more are found; re-test before removing an entry.
_KNOWN_BAD = {
    "macos-notification",                                    # (1) zero-duration render
    "cinematic-zoom", "light-leak", "glitch", "shimmer-sweep",  # (2) transition-gallery demo cards
    "reddit-post",                                           # (2) ships "Prompt to change this title…" chrome
    "apple-money-count", "data-chart", "instagram-follow", "spotify-card",  # (3) fake money/chart/social data
    # exhaustive audit 2026-07-03 — every remaining pickable block is also unsafe:
    "us-map",                        # (3) fake census "Population Density by State / Source: U.S. Census"
    "liquid-glass-widgets",          # (3) fake iOS widget data (8.2K, battery, weather)
    "app-showcase",                  # (3) fake fitness stats (12.8 km, 45 min)
    "code-snippet-dark-modern",      # (2)+ dark VS-Code theme (off light-brand) + "Dark Modern VS Code Theme" title
    "code-diff",                     # (2) gallery title "Code Diff" + demo greet.js
    "flowchart",                     # (2) gallery title "Flowchart" + "Pythom" typo + "${word}" template artifact
    "logo-outro",                    # (2) gallery title "Logo Outro" + off-brand "figma.com"
}                                    # → NO registry block is currently safe; block assignment is default-OFF (enabled()).


def pick_block(text):
    """Return a fitting block name for `text`, or None. Conservative — strong matches only, gated."""
    if not enabled() or not text:
        return None
    low = " " + text.lower() + " "
    for kws, block in _RULES:
        if block in _KNOWN_BAD:
            continue
        if any(k in low for k in kws) and _exists(block):
            return block
    return None


if __name__ == "__main__":
    os.environ["SEOSONA_USE_BLOCKS"] = "1"
    for t in ["Đây là đoạn code Python để gọi API", "Giao diện app rất đẹp", "SEO bền vững là chìa khoá"]:
        print(f"  {t!r:50} -> {pick_block(t)}")
