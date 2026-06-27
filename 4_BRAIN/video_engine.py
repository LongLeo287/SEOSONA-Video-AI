# -*- coding: utf-8 -*-
"""SEOSONA unified video engine — the single render brain (native_composer path).

Replaces the legacy `pipeline_manager.py` (HTML render-project engine). One entry,
`run_pipeline(...)`, handles every input mode and produces a finished SEOSONA video:

  - create   : a text/script OR a GitHub repo URL  → synthesized branded video
  - scrape   : a website URL  → scrape + SEO script → synthesized branded video
  - repurpose: a long MP4/SRT → transcript → hook analysis → vertical shorts
  - download : (handled by the router) YouTube/Drive → file → repurpose

Synthesis is rendered by `native_composer` (voice + RULE #1 captions + HyperFrames
native render + ducked-BGM/SFX mix). Repurpose reuses the proven clipper skill.
GitHub one-shots reuse `make_video.make` (real stars/desc, no hallucinated data).

The deterministic text→scenes planner is an honest DRAFT: it uses the real script
text for narration + captions and derives 2-tone headings from keywords. The
Scene-Composer agent (an LLM) produces richer scenes via `.agents/skills/scene-composer`;
this module guarantees a valid video with no human in the loop. No paid APIs required.
"""
import os
import re
import sys
from importlib import import_module

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(__file__))

import native_composer as nc  # noqa: E402
import make_video as mv       # noqa: E402  (GitHub one-shot path)
import news_video_standards as nvs  # noqa: E402  (Vietnamese script quality gate)

WORKSPACE = os.path.join(ROOT, "8_WORKSPACE")


# ============================================================================ #
# Input detection (single source of truth — the router imports this).
# ============================================================================ #
def _is_github(value):
    if not isinstance(value, str):
        return False
    v = value.strip().lower()
    if "github.com/" in v:
        # a repo URL has owner/name after the host; bare github.com is not a repo
        tail = v.split("github.com/", 1)[1].strip("/")
        return len(tail.split("/")) >= 2
    # bare "owner/name" with no spaces/scheme and a single slash
    if re.fullmatch(r"[\w.-]+/[\w.-]+", value.strip()):
        return True
    return False


def detect_input_type(input_value):
    """Auto-detect the input and return (mode, processed_input)."""
    if not input_value:
        return "create", input_value

    if _is_github(input_value):
        return "create", input_value  # engine routes GitHub to the rich one-shot

    if isinstance(input_value, str) and (input_value.startswith("http://") or input_value.startswith("https://")):
        if "youtube.com" in input_value or "youtu.be" in input_value:
            return "download", input_value
        if "drive.google.com" in input_value:
            return "download", input_value
        return "scrape", input_value

    if isinstance(input_value, str) and os.path.isdir(input_value):
        return "repurpose", input_value

    if isinstance(input_value, str) and os.path.isfile(input_value):
        ext = os.path.splitext(input_value)[1].lower()
        if ext in (".srt", ".mp4", ".mkv", ".avi", ".mov", ".webm"):
            return "repurpose", input_value
        if ext in (".txt", ".md"):
            with open(input_value, "r", encoding="utf-8") as f:
                return "create", f.read()

    return "create", input_value


# ============================================================================ #
# Shared helpers
# ============================================================================ #
def _limit_words(text, max_words):
    words = (text or "").split()
    return " ".join(words[:max_words])


def _extract_srt_from_media(media_path, srt_out_path):
    """Transcribe a media file to SRT via the switchable ASR router (PhoWhisper
    primary, faster-whisper/openai backups). Returns True/False (caller logs)."""
    try:
        _asr = import_module("2_SKILLS.srt_maker.asr_router")
        _srt = import_module("2_SKILLS.srt_maker")
        words = _asr.transcribe_words(media_path, language="vi")
        if not words:
            return False
        segments = _srt.group_words_to_segments(words)

        def _ts(sec):
            h = int(sec // 3600)
            m = int((sec % 3600) // 60)
            s = int(sec % 60)
            ms = int((sec - int(sec)) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

        lines = []
        for i, seg in enumerate(segments, 1):
            lines += [str(i), f"{_ts(seg['start'])} --> {_ts(seg['end'])}", (seg.get("text") or "").strip(), ""]
        if len(lines) <= 1:
            return False
        with open(srt_out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return True
    except Exception as e:
        print(f"[SRT Extract] failed for {media_path}: {e}")
        return False


# ============================================================================ #
# Text → scenes planner (deterministic backbone + optional LLM enrichment)
# ============================================================================ #
_STOP = set("là và của có không được một những các với cho khi này đó đã sẽ rất "
            "thì mà ở từ ra vào nên cũng để theo trên về the a an of to in is for".split())
_ACCENTS = ("blue", "green", "orange")
_H2_BANK = ["là gì?", "vì sao hot?", "điểm chính", "đáng chú ý", "cần biết",
            "nổi bật", "thực tế", "tóm lại"]


def _split_sentences(text):
    text = re.sub(r"\s+", " ", (text or "").strip())
    parts = re.split(r"(?<=[.!?…])\s+", text)
    return [p.strip(" .") for p in parts if p.strip(" .")]


def _keywords(text, n=2):
    """Top content words by frequency (drops stopwords/short tokens). Honest draft —
    headings are derived from the real text, never invented."""
    toks = re.findall(r"[\wÀ-ỹ]+", (text or "").lower())
    freq = {}
    for t in toks:
        if len(t) < 3 or t in _STOP:
            continue
        freq[t] = freq.get(t, 0) + 1
    top = sorted(freq, key=lambda k: (-freq[k], k))[:n]
    return [w.capitalize() for w in top]


def _heading(seg, idx, total):
    kws = _keywords(seg, 2)
    if idx == 0:
        h1 = kws[0] if kws else "SEOSONA"
        return h1, "có gì hot?"
    if idx == total - 1:
        return "Theo dõi SEOSONA", "xem thêm mỗi ngày"
    h1 = kws[0] if kws else "Điểm chính"
    h2 = _H2_BANK[idx % len(_H2_BANK)]
    return h1, h2


def _scene_count(n_sent):
    return max(4, min(7, n_sent // 2 + 2))


def _llm_plan(script_text):
    """Best-effort LLM scene plan. Returns a list of scene dicts or None. Only used
    when it returns the exact schema; otherwise the deterministic planner is used."""
    if not (os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")):
        return None  # no real LLM available — the offline router can't honor this schema
    try:
        llm = import_module("llm_engine")
        sys_p = ("Bạn là Scene-Composer của SEOSONA. Chia kịch bản thành 5-7 cảnh video dọc. "
                 "Trả JSON {\"scenes\":[{\"seg\":\"câu thoại\",\"h1\":\"...\",\"h2\":\"...\"}]}. "
                 "seg là tiếng Việt tự nhiên, h1+h2 là tiêu đề 2 dòng ngắn.")
        out = llm.generate_json_from_prompt(sys_p, script_text)
        scenes = out.get("scenes") if isinstance(out, dict) else None
        if isinstance(scenes, list) and 3 <= len(scenes) <= 9 \
           and all(isinstance(s, dict) and s.get("seg") for s in scenes):
            return scenes
    except Exception as e:
        print(f"[video_engine] LLM plan unavailable ({e}); using deterministic planner.")
    return None


def plan_scenes(script_text):
    """script text → (segments, scenes) ready for native_composer.make_video.

    `scenes` items: {kicker, h1, h2, acc, hero, comp:(kind,data)|None}.
    """
    sentences = _split_sentences(script_text)
    if not sentences:
        sentences = [_limit_words(script_text, 40) or "SEOSONA Video"]

    plan = _llm_plan(script_text)
    if plan:
        groups = [[s["seg"]] for s in plan]
        forced_heads = [(s.get("h1", ""), s.get("h2", "")) for s in plan]
    else:
        n = _scene_count(len(sentences))
        # distribute sentences across n scenes as evenly as possible
        groups, forced_heads = [], None
        per = max(1, len(sentences) // n)
        idx = 0
        for i in range(n):
            take = per if i < n - 1 else len(sentences) - idx
            grp = sentences[idx:idx + max(1, take)] or [sentences[-1]]
            groups.append(grp)
            idx += len(grp)
        groups = [g for g in groups if g]

    total = len(groups)
    segments, scenes = [], []
    used_stats = False
    for i, grp in enumerate(groups):
        seg = " ".join(grp).strip()
        if not seg.endswith((".", "!", "?")):
            seg += "."
        if forced_heads:
            h1, h2 = forced_heads[i]
            if not h1:
                h1, h2 = _heading(seg, i, total)
        else:
            h1, h2 = _heading(seg, i, total)
        acc = _ACCENTS[i % len(_ACCENTS)]
        comp = None
        hero = False

        if i == 0:
            hero = True  # full-bleed accent intro (breaks the centered-card sameness)
        elif i == total - 1:
            comp = ("cta", {"line": "Thủ thuật AI & lập trình mỗi ngày",
                            "btn": "👉 Theo dõi SEOSONA"})
        else:
            nums = re.findall(r"\d[\d.,]*%?", seg)
            short = len(re.findall(r"[\wÀ-ỹ]+", seg)) <= 12
            if nums and not used_stats:
                used_stats = True
                comp = ("stats", {"items": [(num, "") for num in nums[:3]]})
            elif short:
                comp = ("quote", {"text": seg.rstrip("."), "by": ""})
            # else: text-only scene (heading + animated karaoke captions)

        segments.append(seg)
        scenes.append({"kicker": "SEOSONA", "h1": h1, "h2": h2,
                       "acc": acc, "hero": hero, "comp": comp})
    return segments, scenes


# ============================================================================ #
# Mode handlers
# ============================================================================ #
def _create_github(target, project_dir, output, theme):
    """Rich GitHub one-shot (real metadata, auto template + theme)."""
    out = mv.make(target, theme=(theme or "light"), output=output, project_dir=project_dir)
    score_output(out, "seosona")
    maybe_publish(out, project_dir, os.path.basename(project_dir), str(target), "seosona")
    return out


def _vietnamese_gate(script_text):
    """RULE: SEOSONA scripts are Vietnamese — block raw English prose. Strict by
    default (SEOSONA_STRICT_VIETNAMESE_NEWS=1); set to 0 to warn instead of raise."""
    try:
        validation = nvs.validate_vietnamese_news_script(script_text)
    except Exception as e:
        print(f"[video_engine] VN gate skipped ({e}).")
        return
    if getattr(validation, "is_valid", True):
        return
    terms = ", ".join(getattr(validation, "disallowed_terms", [])[:12])
    msg = f"Vietnamese script gate failed — disallowed English prose: {terms}"
    if os.getenv("SEOSONA_STRICT_VIETNAMESE_NEWS", "1") == "1":
        raise RuntimeError(msg)
    print(f"[video_engine] QUALITY WARNING: {msg}")


def _make_thumbnail(project_dir, scenes, segments, brand):
    try:
        thumb_maker = import_module("2_SKILLS.thumbnail_maker.thumbnail_generator")
        thumb_dir = os.path.join(project_dir, "Thumbnail")
        os.makedirs(thumb_dir, exist_ok=True)
        h1 = scenes[0].get("h1", "") if scenes else ""
        h2 = scenes[0].get("h2", "") if scenes else ""
        thumb_maker.generate_html_thumbnail(
            output_path=os.path.join(thumb_dir, "thumbnail.png"),
            top_label="SEOSONA" if brand == "seosona" else brand.upper(),
            main_title=(f"{h1} {h2}").strip() or "SEOSONA",
            hook=(segments[0] if segments else ""),
            cta="XEM NGAY", portrait_path=None, brand=brand,
        )
    except Exception as e:
        print(f"[video_engine] thumbnail skipped: {e}")


def score_output(output, brand="seosona"):
    """Quality gate on a finished video (best-effort, non-fatal). Runs on EVERY
    create entrypoint so direct make_video / news batches are scored too."""
    try:
        qs = import_module("quality_scorer")
        report = qs.score_video(output, brand=brand)
        verdict = "PASS" if report.get("pass") else "FAIL"
        print(f"[quality] {report.get('score', '?')}/100 ({verdict})")
        return report
    except Exception as e:
        print(f"[quality] scoring skipped: {e}")
        return None


def maybe_publish(output, project_dir, project_name, script_text="", brand="seosona"):
    """STEP 8 (optional) — publish if SEOSONA_PUBLISH is set (e.g. "google_drive,youtube").
    Credential-gated per destination; never breaks the render."""
    targets = os.environ.get("SEOSONA_PUBLISH", "").strip()
    if not targets:
        return None
    try:
        ag = os.path.join(ROOT, "1_AGENTS")
        if ag not in sys.path:
            sys.path.insert(0, ag)
        from publisher_agent import publish as _publish
        thumb = os.path.join(project_dir, "Thumbnail", "thumbnail.png")
        product = {"video": output, "title": project_name}
        if os.path.exists(thumb):
            product["thumbnail"] = thumb
        try:
            from seo_optimizer.youtube_seo import generate_youtube_metadata
            kw = [w for w in project_name.replace("_", " ").replace("-", " ").split()
                  if len(w) > 2][:5] or [project_name]
            hook = (script_text or project_name).strip().split(".")[0][:120]
            seo = generate_youtube_metadata(hook, kw, {}, video_duration=60)
            product.update({"title": seo["title"], "description": seo["description"], "tags": seo["tags"]})
            print(f"[publish] SEO metadata: {seo['title']}")
        except Exception as se:
            print(f"[publish] SEO enrich skipped: {se}")
        dests = [d.strip() for d in targets.split(",") if d.strip()]
        print(f"[publish] → {', '.join(dests)}")
        return _publish(product, destinations=dests,
                        save_report_to=os.path.join(project_dir, "publish_report.json"))
    except Exception as e:
        print(f"[publish] step failed (non-fatal): {e}")
        return None


def _scrape_capture(url, project_dir, max_shots=3):
    """Capture source-page screenshots (B-roll → project_dir/broll/) + a text 'mockup'
    card built from real page headings. Best-effort: needs Playwright; returns the
    mockup data dict or None. (HyperFrames scenes can't composite raw images, so the
    screenshots are saved as assets and the on-screen card is the text mockup.)"""
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        print(f"[scrape] screenshots skipped (Playwright unavailable): {e}")
        return None
    broll = os.path.join(project_dir, "broll")
    os.makedirs(broll, exist_ok=True)
    domain = url.split("//")[-1].split("/")[0]
    lines = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2500)
            for i in range(max_shots):
                page.screenshot(path=os.path.join(broll, f"shot_{i}.png"))
                page.evaluate("window.scrollBy(0, 800)")
                page.wait_for_timeout(400)
            try:
                heads = page.eval_on_selector_all(
                    "h1,h2,h3", "els => els.slice(0,4).map(e=>e.innerText.trim()).filter(Boolean)")
                lines = [h[:60] for h in heads][:4]
            except Exception:
                pass
            browser.close()
        print(f"[scrape] captured {max_shots} screenshots → {broll}")
    except Exception as e:
        print(f"[scrape] screenshot capture failed: {e}")
        return None
    return {"url": domain, "lines": lines or [domain]}


def _create_from_text(script_text, project_dir, output, theme, brand="seosona", mockup=None):
    _vietnamese_gate(script_text)
    segments, scenes = plan_scenes(script_text)
    if mockup and len(scenes) >= 3:
        # show the source page as a text mockup card on an early middle scene
        scenes[1]["comp"] = ("mockup", mockup)
    print(f"[video_engine] create: {len(scenes)} scenes from {len(segments)} segments")
    out = nc.make_video(project_dir, segments, scenes, output=output,
                        theme=(theme or "light"), brand=brand)
    _make_thumbnail(project_dir, scenes, segments, brand)
    score_output(out, brand)
    maybe_publish(out, project_dir, os.path.basename(project_dir), script_text, brand)
    return out


def _scrape_to_text(url):
    scraper = import_module("1_AGENTS.scraper_agent.scraper")
    scraped = scraper.scrape_article(url)
    if scraped and scraped.get("content"):
        print(f"[scrape] '{scraped.get('title')}' ({scraped.get('word_count')} words)")
        try:
            writer = import_module("1_AGENTS.seo_writer_agent.writer").SeoWriterAgent()
            script_json = writer.generate_script(scraped)
            text = (script_json or {}).get("narrator_text", "")
            if not text and isinstance(script_json, dict) and "scenes" in script_json:
                text = " ".join(s.get("narrator_text", "") for s in script_json["scenes"])
            if text:
                return text
        except Exception as e:
            print(f"[scrape] SEO writer failed ({e}); using trimmed article body.")
        return _limit_words(scraped["content"], 200)
    print("[scrape] scraping failed/empty.")
    return None


def _repurpose(media_path, project_dir, brand, project_name):
    srt_dir = os.path.join(project_dir, "SRT")
    thumb_dir = os.path.join(project_dir, "Thumbnail")
    os.makedirs(srt_dir, exist_ok=True)
    os.makedirs(thumb_dir, exist_ok=True)

    real_srt = os.path.join(srt_dir, f"{project_name}_source.srt")
    is_srt = str(media_path).lower().endswith(".srt")
    if is_srt:
        real_srt = media_path
    elif not _extract_srt_from_media(media_path, real_srt):
        print("[REPURPOSE] WARNING: transcript extraction failed — hooks may be unreliable.")

    analyzer = import_module("1_AGENTS.repurposer_agent.srt_analyzer")
    clipper = import_module("2_SKILLS.video_clipper.clipper")
    thumb_maker = import_module("2_SKILLS.thumbnail_maker.thumbnail_generator")

    hooks = analyzer.analyze_srt_for_hooks(real_srt) or []
    outputs = []
    for hook in hooks:
        out_name = os.path.join(project_dir, f"{project_name}_Part{hook['id']}.mp4")
        if not is_srt:
            clipper.cut_and_format_short(media_path, hook["start"], hook["end"], out_name)
            outputs.append(out_name)
        thumb_out = os.path.join(thumb_dir, f"{project_name}_Part{hook['id']}_Thumbnail.png")
        try:
            thumb_maker.generate_html_thumbnail(
                output_path=thumb_out, top_label="BẢN TIN", main_title="VIDEO SHORTS",
                hook=hook.get("hook_text", ""), cta="XEM NGAY", portrait_path=None, brand=brand,
            )
        except Exception as e:
            print(f"[REPURPOSE] thumbnail failed for part {hook['id']}: {e}")
    print(f"[REPURPOSE] {len(outputs)} shorts → {project_dir}")
    return {"project_dir": project_dir, "outputs": outputs}


# ============================================================================ #
# Public entry — signature-compatible with the legacy pipeline_manager.
# ============================================================================ #
def run_pipeline(script_text, brand="seosona", mode="create", aspect_ratio="9:16", project_name=None):
    if not project_name:
        from datetime import datetime
        project_name = f"{brand.upper()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    if mode == "carousel":
        raise RuntimeError(
            "Carousel and image workflows are not video workflows. "
            "Use scripts/workflow_social_post.py or `npm run post:image`."
        )

    project_dir = os.path.join(WORKSPACE, project_name)
    os.makedirs(project_dir, exist_ok=True)
    output = os.path.join(project_dir, "FINAL.mp4")
    theme = "light"  # brand law: light mode only

    print(f"[video_engine] mode={mode} brand={brand} ratio={aspect_ratio} → {project_name}")

    try:
        if mode == "repurpose":
            return _repurpose(script_text, project_dir, brand, project_name)

        if mode == "scrape":
            text = _scrape_to_text(script_text)
            if not text:
                raise RuntimeError(f"Scrape produced no usable script from: {script_text}")
            mockup = _scrape_capture(script_text, project_dir)  # screenshots + source card
            return _create_from_text(text, project_dir, output, theme, brand, mockup=mockup)

        # create (text or GitHub)
        if _is_github(script_text):
            return _create_github(script_text, project_dir, output, theme)
        return _create_from_text(script_text, project_dir, output, theme, brand)
    except Exception:
        _cleanup_incomplete(project_dir)
        raise


def _cleanup_incomplete(project_dir):
    """Delete the project dir if the render failed before any real output exists
    (no .mp4/.srt/.png that isn't an intermediate). Mirrors the old engine."""
    if not os.path.isdir(project_dir):
        return
    for root_d, _dirs, files in os.walk(project_dir):
        for fn in files:
            low = fn.lower()
            if low.endswith((".mp4", ".srt", ".png")) and "_raw" not in low \
               and "scene_" not in low and "voice." not in low:
                return  # a real product file exists — keep it
    try:
        import shutil
        shutil.rmtree(project_dir)
        print(f"[video_engine] cleaned up incomplete project: {project_dir}")
    except Exception as e:
        print(f"[video_engine] cleanup failed for {project_dir}: {e}")


if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "SEOSONA Video Factory tự động sản xuất video tiếng Việt bằng AI."
    brand = sys.argv[2] if len(sys.argv) > 2 else "seosona"
    ratio = sys.argv[3] if len(sys.argv) > 3 else "9:16"
    name = sys.argv[4] if len(sys.argv) > 4 else None
    mode, processed = detect_input_type(inp)
    print(run_pipeline(processed, brand=brand, mode=mode, aspect_ratio=ratio, project_name=name))
