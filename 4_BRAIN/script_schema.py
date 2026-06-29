# -*- coding: utf-8 -*-
"""SEOSONA Video — Script & Template schema validation.

Borrowed from huytranvan2010/AI-auto-generate-video's zod contract (analysed
2026-06-29): validate the content BEFORE rendering so bad input fails fast with a
clear message instead of producing a broken video. Pure pydantic (already a dep) +
a soft "lint" pass for poster discipline (char limits) and RULE #1 (no emoji/URLs in
the spoken text).

Two shapes:
  • CONTENT — what scene_composer.compose() returns / native_composer consumes:
      {segments: [str], scenes: [{h1, h2, kicker?, data?}], lexicon?: {}}
  • TEMPLATE — a 7_ASSETS/templates/*.json file:
      {name, aspect, scenes: [{component, accent, kicker_hint, hero}], ...}

`validate_content` / `validate_template` return {ok, errors, warnings}. Structural
problems are ERRORS (block render); poster-discipline char limits are WARNINGS (the
char budgets live in 7_ASSETS/templates/CATALOG.md).
"""
from typing import Any, Optional
import re

from pydantic import BaseModel, ValidationError, field_validator

ASPECTS = {"9:16", "16:9", "1:1"}
ACCENTS = {"blue", "green", "orange"}

# Poster discipline (warnings) — mirrors CATALOG.md slot budgets.
LIMITS = {"kicker": 24, "h1": 24, "h2": 24}
SEGMENT_MAX_WORDS = 45   # one idea per scene; longer → split into more scenes

# Emoji / symbols that must never reach the TTS (RULE #1: voice text is clean).
_EMOJI = re.compile("[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF←-⇿⌀-⏿]")
_VOICE_BANNED = re.compile(r"[→&%$#=]|https?://|www\.")


# ----------------------------------------------------------------- CONTENT
class ContentScene(BaseModel):
    h1: str
    h2: str
    kicker: Optional[str] = None
    data: Optional[dict] = None

    @field_validator("h1", "h2")
    @classmethod
    def _nonempty(cls, v):
        if not v or not str(v).strip():
            raise ValueError("must be non-empty")
        return v


class Content(BaseModel):
    segments: list[str]
    scenes: list[ContentScene]
    lexicon: dict[str, str] = {}

    @field_validator("segments")
    @classmethod
    def _seg_nonempty(cls, v):
        if not v or not all(str(s).strip() for s in v):
            raise ValueError("segments must be a non-empty list of non-empty strings")
        return v


def validate_content(content: dict) -> dict:
    errors, warnings = [], []
    try:
        c = Content(**content)
    except ValidationError as e:
        return {"ok": False, "errors": [str(x["loc"]) + ": " + x["msg"] for x in e.errors()],
                "warnings": []}

    # structural: one segment per scene (native_composer groups words by segment→scene)
    if len(c.segments) != len(c.scenes):
        errors.append(f"segments ({len(c.segments)}) must equal scenes ({len(c.scenes)}) "
                      f"— one narration segment per scene")

    for i, sc in enumerate(c.scenes):
        for slot in ("kicker", "h1", "h2"):
            val = getattr(sc, slot, None)
            if val and len(val) > LIMITS[slot]:
                warnings.append(f"scene[{i}].{slot} is {len(val)} chars (>{LIMITS[slot]}); "
                                f"poster layout — keep it short")
    for i, seg in enumerate(c.segments):
        if _EMOJI.search(seg) or _VOICE_BANNED.search(seg):
            errors.append(f"segments[{i}] contains emoji/URL/symbol — RULE #1: spoken text "
                          f"must be clean (move emoji to on-screen fields)")
        n = len(seg.split())
        if n > SEGMENT_MAX_WORDS:
            warnings.append(f"segments[{i}] is {n} words (>{SEGMENT_MAX_WORDS}); split into "
                            f"more scenes for a faster cut")
    return {"ok": not errors, "errors": errors, "warnings": warnings}


# ----------------------------------------------------------------- TEMPLATE
class TemplateScene(BaseModel):
    component: Optional[str] = None
    accent: Optional[str] = None
    kicker_hint: Optional[str] = None
    hero: bool = False


class Template(BaseModel):
    name: str
    aspect: str = "9:16"
    scenes: list[TemplateScene]

    @field_validator("aspect")
    @classmethod
    def _aspect(cls, v):
        if v not in ASPECTS:
            raise ValueError(f"aspect must be one of {sorted(ASPECTS)}")
        return v


def validate_template(tpl: dict) -> dict:
    errors, warnings = [], []
    try:
        t = Template(**tpl)
    except ValidationError as e:
        return {"ok": False, "errors": [str(x["loc"]) + ": " + x["msg"] for x in e.errors()],
                "warnings": []}
    if not t.scenes:
        errors.append("template has no scenes")
    for i, sc in enumerate(t.scenes):
        if sc.accent and sc.accent not in ACCENTS:
            warnings.append(f"scene[{i}].accent '{sc.accent}' not in {sorted(ACCENTS)}")
    return {"ok": not errors, "errors": errors, "warnings": warnings}


if __name__ == "__main__":
    import sys, json
    if len(sys.argv) > 1:  # validate a template file
        tpl = json.load(open(sys.argv[1], encoding="utf-8"))
        print(json.dumps(validate_template(tpl), ensure_ascii=False, indent=2))
    else:
        demo = {"segments": ["Xin chào anh em.", "Hôm nay học SEO."],
                "scenes": [{"h1": "SEO", "h2": "2026"}, {"h1": "Bắt đầu", "h2": "ngay"}]}
        print(json.dumps(validate_content(demo), ensure_ascii=False, indent=2))
