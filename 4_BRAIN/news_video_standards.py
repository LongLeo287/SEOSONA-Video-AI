import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence
import json
import os


WORD_PATTERN = re.compile(
    r"24/7|Next\.js|[A-Za-zÀ-ỹ0-9]+(?:[+#/-][A-Za-zÀ-ỹ0-9]+)*",
    re.UNICODE,
)

CORE_PRONUNCIATION_LEXICON: Dict[str, str] = {
    "AI": "ây ai",
    "A.I.": "ây ai",
    "SEO": "séo",
    "SEOSONA": "séo sô na",
    "Search": "sớt",
    "GitHub": "gít hắp",
    "Google": "gu gồ",
    "YouTube": "diu túp",
    "TikTok": "tích tóc",
    "Facebook": "phây búc",
    "OpenAI": "âu pần ây ai",
    "ChatGPT": "chát gi pi ti",
    "LLM": "eo eo em",
    "MCP": "em si pi",
    "API": "ây pi ai",
    "RAG": "rác",
    "Next.js": "next chấm giây ét",
    "24/7": "hai mươi tư trên bảy",
    "24h": "hai mươi tư giờ",
    # common English tech terms — Vietnamese phonetics so the male VN voice reads them
    # acceptably (VieNeu is a VN TTS; raw English would be mispronounced).
    "Claude": "clốt", "Codex": "cô đếch", "Cursor": "cơ sơ", "Docker": "đốc cơ",
    "Ollama": "âu la ma", "Gemini": "giê mi nai", "Kimi": "ki mi", "Grok": "grốc",
    "Anthropic": "ăn thro pic", "Microsoft": "mai cờ rô sốt", "Apple": "áp pồ",
    "GPU": "gi pi diu", "CPU": "xi pi diu", "IDE": "ai đi i", "CLI": "xi eo ai",
    "SQL": "ét qiu eo", "HTML": "hát ti em eo", "CSS": "xi ét ét", "JS": "giây ét",
    "npm": "en pi em", "pip": "píp", "Markdown": "mác đao", "token": "tâu cừn",
    "prompt": "prom", "model": "mô đồ", "agent": "ây dần", "Agent": "ây dần",
    "local": "lâu cồ", "cloud": "cờ lao", "open source": "âu pừn sọt", "code": "cốt",
    "coding": "cô đinh", "schema": "sờ kê ma", "backlink": "béc linh", "traffic": "trép phích",
    "Overview": "âu vơ viu", "benchmark": "ben mác", "stream": "sì trim", "endpoint": "en point",
    "MIT": "em ai ti", "E-E-A-T": "i i ây ti", "GEO": "giê ô", "AEO": "ây i ô",
    "Stripe": "sờ trai", "Vercel": "vơ xeo", "Linear": "li ni a", "HuggingFace": "hâ ging phây",
    "ByteDance": "bai đừn", "DeepClaude": "đip clốt", "LocalAI": "lâu cô eo ai",
    "Voicebox": "vois bóc", "Artifacts": "a ti phách", "Skills": "sờ kiu", "Skill": "sờ kiu",
    # added 2026-06-29 (English-pronunciation pass) — terms that recur in repo videos but
    # were missing; phonetics follow the conventions above (G→"gi", H→"hát", spelled-out).
    "GPT": "gi pi ti", "Git": "gít", "Python": "pai thon", "JavaScript": "gia va sờ cơ ríp",
    "TypeScript": "típ sờ cơ ríp", "Linux": "li núc", "Windows": "quin đâu",
    "Kubernetes": "ku bơ nét", "framework": "phrêm uốc", "repo": "rê pô",
    "URL": "diu a eo", "SDK": "ét đi cây", "UI": "diu ai", "UX": "diu ích",
    "JSON": "giây sần", "HTTP": "hát ti ti pi", "HTTPS": "hát ti ti pi ét",
    "GitLab": "gít láp", "VS Code": "vi ét cốt", "Node": "nốt", "Nodejs": "nốt giây ét",
}

_lexicon_path = os.path.join(os.path.dirname(__file__), 'lexicon.json')
try:
    with open(_lexicon_path, 'r', encoding='utf-8') as _f:
        _raw_lexicon = json.load(_f)
        PRONUNCIATION_LEXICON: Dict[str, str] = dict(CORE_PRONUNCIATION_LEXICON)
        for key, value in _raw_lexicon.items():
            clean_key = key.replace(r'\b', '')
            if clean_key:
                PRONUNCIATION_LEXICON[clean_key] = value
except Exception as e:
    print(f"[Warning] Could not load lexicon.json in news_video_standards: {e}")
    PRONUNCIATION_LEXICON: Dict[str, str] = dict(CORE_PRONUNCIATION_LEXICON)

VIETNAMESE_ASCII_ALLOWLIST = {
    "ai",
    "anh",
    "ban",
    "bo",
    "cai",
    "cho",
    "co",
    "con",
    "cua",
    "da",
    "dang",
    "day",
    "de",
    "den",
    "di",
    "do",
    "duoc",
    "giu",
    "hay",
    "ho",
    "hoc",
    "khong",
    "la",
    "lai",
    "lam",
    "len",
    "mot",
    "nam",
    "nay",
    "neu",
    "nguoi",
    "nhanh",
    "nhat",
    "nhung",
    "noi",
    "qua",
    "ra",
    "roi",
    "sau",
    "se",
    "tao",
    "theo",
    "thi",
    "toi",
    "trong",
    "tu",
    "va",
    "van",
    "ve",
    "voi",
}

# English function words used to detect a DUMPED English sentence. Deliberately EXCLUDES "to"/"in"/"an" —
# they are also common VIETNAMESE words (to=big, in=print, an=in "an toàn"/"an ninh"=safe/security), so
# they false-flagged legitimate Vietnamese scripts as English leaks. Real English still trips plenty of
# the remaining markers (the/is/for/and/with/of/…) plus the ≥10-consecutive-unknown-ASCII run.
ENGLISH_PROSE_MARKERS = {
    "a",
    "and",
    "are",
    "as",
    "by",
    "changing",
    "every",
    "for",
    "from",
    "has",
    "have",
    "is",
    "marketer",
    "marketers",
    "of",
    "on",
    "the",
    "this",
    "with",
}


@dataclass(frozen=True)
class TtsPlan:
    display_text: str
    tts_text: str
    display_words: List[str]
    tts_words: List[str]
    tts_word_to_display_index: List[int]


@dataclass(frozen=True)
class ScriptValidation:
    is_valid: bool
    disallowed_terms: List[str]


def tokenize_words(text: str) -> List[str]:
    return WORD_PATTERN.findall(str(text or ""))


def _term_pattern(term: str) -> re.Pattern:
    return re.compile(
        rf"(?<![A-Za-z0-9À-ỹ]){re.escape(term)}(?![A-Za-z0-9À-ỹ])",
        re.IGNORECASE | re.UNICODE,
    )


def _lookup_pronunciation(word: str) -> str:
    folded = word.casefold()
    for term, pronunciation in PRONUNCIATION_LEXICON.items():
        if term.casefold() == folded:
            return pronunciation
    return word


def prepare_tts_script(display_text: str) -> TtsPlan:
    """Create a separate pronunciation script while preserving display text."""
    tts_text = str(display_text or "")
    for term in sorted(PRONUNCIATION_LEXICON, key=len, reverse=True):
        tts_text = _term_pattern(term).sub(PRONUNCIATION_LEXICON[term], tts_text)

    display_words = tokenize_words(display_text)
    tts_words: List[str] = []
    mapping: List[int] = []
    for idx, display_word in enumerate(display_words):
        spoken_words = tokenize_words(_lookup_pronunciation(display_word))
        if not spoken_words:
            spoken_words = [display_word]
        tts_words.extend(spoken_words)
        mapping.extend([idx] * len(spoken_words))

    return TtsPlan(
        display_text=str(display_text or ""),
        tts_text=tts_text,
        display_words=display_words,
        tts_words=tts_words,
        tts_word_to_display_index=mapping,
    )


def _estimate_word_data(words: Sequence[str], duration: float, span=None) -> List[dict]:
    """Spread words proportionally by char weight. With `span=(t0,t1)` it distributes over
    the REAL speech envelope from ASR (respects leading/trailing silence) instead of a flat
    0..duration guess — used when per-word ASR timing can't be trusted but its overall
    span can."""
    if not words:
        return []
    duration = max(0.3, float(duration or 0.3))
    if span:
        t0, t1 = float(span[0]), float(span[1])
        lead_in = max(0.0, t0)
        tail_pad = max(0.0, duration - min(duration, t1))
    else:
        lead_in = 0.08
        tail_pad = 0.08
    gap = 0.025 if len(words) > 1 else 0.0
    total_weight = sum(max(1, len(word)) for word in words)
    total_gap = gap * max(0, len(words) - 1)
    usable = max(0.2, duration - lead_in - tail_pad - total_gap)
    cursor = lead_in
    out = []
    for word in words:
        word_duration = max(0.05, usable * max(1, len(word)) / total_weight)
        end = min(duration - tail_pad, cursor + word_duration)
        out.append({"word": word, "start": cursor, "end": end})
        cursor = min(duration - tail_pad, end + gap)
    return out


def align_tts_boundaries_to_display_words(
    plan: TtsPlan,
    tts_boundaries: Iterable[dict],
    duration: float,
) -> List[dict]:
    """Map pronunciation word boundaries back onto the exact display words."""
    boundaries = [item for item in tts_boundaries if str(item.get("word", "")).strip()]
    n = len(plan.display_words)
    if not boundaries or not n:
        return _estimate_word_data(plan.display_words, duration)

    def _b_start(b):
        return float(b.get("start", 0.0))

    def _b_end(b):
        return float(b.get("start", 0.0)) + max(0.05, float(b.get("duration", 0.25)))

    # The real speech envelope (first..last heard word) — usable even when the ASR text
    # itself is unreliable; lets the estimate respect leading/trailing silence. Only trust
    # it when it covers a plausible fraction of the clip (a too-short envelope means the
    # ASR also got the timing wrong → flat full-duration estimate is safer).
    env = (min(_b_start(b) for b in boundaries), max(_b_end(b) for b in boundaries))
    _span = env if (env[1] - env[0]) > max(1.0, 0.4 * duration) else None

    # PLAUSIBILITY GUARD: if ASR returned far fewer words than the spoken script, the take
    # is likely low-quality/hallucinated — its per-word timings are garbage, so don't trust
    # them; spread display words smoothly over the real envelope instead.
    if len(boundaries) < 0.6 * max(1, len(plan.tts_words)):
        return _estimate_word_data(plan.display_words, duration, span=_span)

    # 0.6 ≤ ratio < 1: ASR heard fewer words than were spoken. The index-based 1:1 map below
    # assumes no dropped words — one missed ASR word shifts EVERY later index, so captions drift
    # in the back half. Anchor each display word to the ASR word at its PROPORTIONAL position
    # instead (robust to dropped words; still real ASR timing = audio-master, not an even guess).
    if len(boundaries) < len(plan.tts_words):
        n2, m2 = len(plan.display_words), len(boundaries)
        anchored = []
        for j, w in enumerate(plan.display_words):
            si = min(m2 - 1, int(j * m2 / n2))
            ei = max(si, min(m2 - 1, int((j + 1) * m2 / n2 - 1e-9)))
            s, e = _b_start(boundaries[si]), _b_end(boundaries[ei])
            anchored.append({"word": w, "start": max(0.0, s),
                             "end": min(float(duration), max(s + 0.05, e))})
        for i in range(1, len(anchored)):       # monotonic, non-overlapping
            if anchored[i]["start"] < anchored[i - 1]["start"]:
                anchored[i]["start"] = anchored[i - 1]["start"]
            if anchored[i - 1]["end"] > anchored[i]["start"]:
                anchored[i - 1]["end"] = anchored[i]["start"]
            if anchored[i - 1]["end"] <= anchored[i - 1]["start"]:
                anchored[i - 1]["end"] = anchored[i - 1]["start"] + 0.02
            if anchored[i]["end"] <= anchored[i]["start"]:
                anchored[i]["end"] = anchored[i]["start"] + 0.05
        return anchored

    # Index-based grouping (ASR word i ↔ spoken word i ↔ display word mapping[i]).
    grouped: Dict[int, List[dict]] = {idx: [] for idx in range(n)}
    for boundary_idx, boundary in enumerate(boundaries):
        if boundary_idx >= len(plan.tts_word_to_display_index):
            break
        display_idx = plan.tts_word_to_display_index[boundary_idx]
        if display_idx in grouped:
            grouped[display_idx].append(boundary)

    real = {}
    for idx in range(n):
        g = grouped[idx]
        if g:
            real[idx] = (max(0.0, min(_b_start(b) for b in g)), max(_b_end(b) for b in g))

    # If too few display words got real timing, fall back to the envelope estimate.
    if len(real) < 0.5 * n:
        return _estimate_word_data(plan.display_words, duration, span=_span)

    # PARTIAL-REAL: keep real timing where ASR matched; linearly interpolate the gaps
    # (was all-or-nothing → one missed word dumped the whole scene to a flat estimate).
    filled = sorted(real)
    aligned = []
    for idx in range(n):
        if idx in real:
            start, end = real[idx]
        else:
            prev = max([i for i in filled if i < idx], default=None)
            nxt = min([i for i in filled if i > idx], default=None)
            if prev is not None and nxt is not None:
                gap = max(0.0, real[nxt][0] - real[prev][1]); steps = nxt - prev
                start = real[prev][1] + gap * ((idx - prev - 1) / steps)
                end = real[prev][1] + gap * ((idx - prev) / steps)
            elif prev is not None:
                start = real[prev][1]; end = start + 0.25
            elif nxt is not None:
                end = real[nxt][0]; start = max(0.0, end - 0.25)
            else:
                start, end = 0.0, 0.25
        aligned.append({"word": plan.display_words[idx],
                        "start": max(0.0, start),
                        "end": min(float(duration), max(start + 0.05, end))})

    # Enforce monotonic, non-overlapping order (interpolated gaps can otherwise overlap).
    for i in range(1, len(aligned)):
        if aligned[i]["start"] < aligned[i - 1]["start"]:
            aligned[i]["start"] = aligned[i - 1]["start"]
        if aligned[i - 1]["end"] > aligned[i]["start"]:
            aligned[i - 1]["end"] = aligned[i]["start"]
        if aligned[i - 1]["end"] <= aligned[i - 1]["start"]:
            aligned[i - 1]["end"] = aligned[i - 1]["start"] + 0.02
        if aligned[i]["end"] <= aligned[i]["start"]:
            aligned[i]["end"] = aligned[i]["start"] + 0.05
    return aligned


def validate_vietnamese_news_script(text: str) -> ScriptValidation:
    """Flag obvious English prose while allowing approved technical terms."""
    allowed_terms = {term.casefold() for term in PRONUNCIATION_LEXICON}
    disallowed = []
    unknown_ascii_run = []
    for word in tokenize_words(text):
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9+#./-]*", word):
            unknown_ascii_run = []
            continue
        lowered = word.casefold()
        if lowered in allowed_terms or lowered in VIETNAMESE_ASCII_ALLOWLIST:
            unknown_ascii_run = []
            continue
        if word.isupper() and len(word) <= 5:
            unknown_ascii_run = []
            continue
        if lowered in ENGLISH_PROSE_MARKERS:
            disallowed.append(word)
            unknown_ascii_run = []
            continue
        unknown_ascii_run.append(word)
        if len(unknown_ascii_run) >= 10:
            disallowed.extend(unknown_ascii_run)
            unknown_ascii_run = []
    return ScriptValidation(is_valid=not disallowed, disallowed_terms=disallowed)
