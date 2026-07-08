# -*- coding: utf-8 -*-
"""Single source of truth for the SEOSONA brand palette + CTA copy.

Mirrors the human brand contract `7_ASSETS/brand/SEOSONA/DESIGN.md` §2. ALL render code
(`native_composer`, `hf_blocks`, `talking_head_edit`, `video_engine`) imports its colours and
call-to-action copy from HERE, so each brand value lives in exactly ONE place. Change a colour
here and every pipeline (news + course/talking-head) follows. Light-mode brand law only.
"""

# --- Palette (DESIGN.md §2) ----------------------------------------------------------------
BLUE = "#2A5BDA"     # primary accent — headings, CTA, links, trust
CORAL = "#E2724D"    # secondary / warm accent
GREEN = "#16A34A"    # success / positive
AMBER = "#D97706"    # caution / "verify this" (darker than #F59E0B for contrast on light bg)
NAVY = "#16224A"     # caption pill + card-background ink (the karaoke pill)
INK = "#0F172A"      # deepest text ink
GREY = "#94A3B8"     # baseline / inactive / locked reference

ORANGE = CORAL       # back-compat alias (older code called coral "orange")

# the rotating scene accent set used by both pipelines
ACCENTS = {"blue": BLUE, "green": GREEN, "orange": CORAL}

# --- Semantic colour ROLES (from the 45-video craft study, 2026-07 --------------------------
# `2_KNOWLEDGE/hyperframes/craft/template-study-2026-07.md` §3). Meaning FIRST: a component asks
# for a role ("danger") and gets the brand hue that MEANS it — so the light render preserves the
# reference videos' semantics (glow→shadow) instead of hard-coding hues. CQA overrides the accent
# hues (blue/green/amber) via `native_composer.ACCENT_PALETTE`; the ROLE→meaning map is shared.
ROLES = {
    "emphasis": BLUE,    # the ONE highlighted word / hero keyword (max 1 per caption)
    "success":  GREEN,   # solution / free / confirmed ✓ / winner / speed
    "danger":   CORAL,   # error / cost / pain / deprecated / rejected / "not X"
    "caution":  AMBER,   # warning / "verify this" / reality-check
    "info":     "#3A4A6B",  # neutral data / secondary chips / the losing variant
    "baseline": GREY,    # old/human reference, locked/absent (grey, often strikethrough)
}


def ass_color(hex_color):
    """`#RRGGBB` → ASS `&H00BBGGRR` (libass stores colour as BGR). Used by the talking-head
    caption renderer so its colours come from this same palette instead of a hand-typed ASS code."""
    h = hex_color.lstrip("#")
    return f"&H00{h[4:6]}{h[2:4]}{h[0:2]}".upper()


# --- CTA / footer copy (was hardcoded across video_engine + native_composer) ----------------
CTA_FOLLOW = "Theo dõi SEOSONA"
CTA_TAGLINE = "Thủ thuật AI & lập trình mỗi ngày"
CTA_BUTTON = "👉 Theo dõi SEOSONA"
CTA_DEFAULT_LINE = "Theo dõi SEOSONA để xem thêm"
FOOTER_TAGLINE = "Share to be shared more"
