# SCRIPT WRITING PIPELINE — the ONE path all video narration goes through

**Read this first.** Every SEOSONA video script (news, course, agent-written) flows through the same six
stages with the same rules and the same verification. One rulebook, one writer, one gate — so nothing
ships fabricated, off-brand, or repetitive. This doc is the map; the code is `4_BRAIN/script_writer.py`.

> WHY this exists: before 2026-07, four separate writers (make_video, video_engine/scene_writer, the
> Scene-Composer agent, course_planner) each had their OWN copy of the rules and their OWN (or NO)
> verification. That let English + a mis-read number ("119,765" → "…phẩy…") + repeated scenes ship
> un-caught. This pipeline unifies them.

## The six stages (each has an input → output → GATE)

| # | Stage | Input → Output | GATE (fail → action) | Code |
|---|-------|----------------|----------------------|------|
| 1 | **FETCH** | url / topic / SRT / facts → `SourceData` | must end with real `raw_text`; a bare TOPIC auto-**RESEARCHes** the web first (else `unsourced=True`) | `script_writer.fetch()` → `researcher.research()` (Google News RSS free; **Firecrawl** cleans bodies + **PageSpeed** adds real Web-Vitals when the topic names a URL) |
| 2 | **ANALYZE** | `SourceData` → `KeyFacts{claims, numbers, entities}` | every fact traces to the real source fields / text only | `script_writer.analyze()` |
| 3 | **REASON** | `KeyFacts` → `Angle` | angle must build on the facts | `angle_finder.find_angles()` (via `reason()`) |
| 4 | **PLAN** | `Angle` → `Outline` (5–9 scenes) | no two scenes share a focus; each gets a suggested component+block (real vocab) → writer↔library coupling | `script_writer.plan()` / `suggest_component()` |
| 5 | **WRITE** | `Outline` + `KeyFacts` → `Script` | grounded prompt; rules loaded from MASTER_VIDEO_SPEC | `script_writer.write()` |
| 6 | **VERIFY** | `Script` → `VerifyResult` | **5 gates below** — any hard error → rewrite (bounded loop) | `script_writer.verify()` |

### The VERIFY gates (stage 6) — applied to EVERY path
1. **English leak** — `news_video_standards.validate_vietnamese_news_script` (Vietnamese narration only).
2. **FULL traceability** — every number/entity spoken must trace to `KeyFacts` (numbers match within the
   same order of magnitude + rounding tolerance, so "119 nghìn" ≈ 119,787 but "900 nghìn"/"5 triệu" are
   rejected as fabricated). `unsourced` topics → un-sourced names are hard errors too.
3. **Fabricated social-proof / unsafe** — `content_moderation.moderate`.
4. **Structure / busy heading** — `spec_lint.lint_scenes`.
5. **Repeated line** — the "trùng cảnh" check (no scene repeats another's sentence).

### No dropped / duplicated content — the guarantees
- **No silent drop.** `write()` warns when the LLM returns fewer scenes than asked; `generate_script()`
  adds a hard `rớt cảnh` error when `len(scenes) < n_scenes` → forces a rewrite instead of shipping short.
- **Rewrites actually correct.** `write(feedback=…)` injects the prior attempt's verify errors into the
  prompt, so a rewrite fixes the specific problem (was previously re-running the same prompt = no-op).
- **No duplicate focus.** `plan()` uses 10 distinct archetypes + a final de-dup pass → no two scenes
  share a focus (was repeating from n≥9).
- **No duplicate line.** Gate 5 catches repeats at write-time (→ rewrite) AND again at the render
  chokepoint (`enforce_before_render`) as a last line of defence.

## Where the rules + knowledge live (loaded at runtime — NOT hardcoded)
| Asset | Role |
|---|---|
| `9_PROMPTS/MASTER_VIDEO_SPEC.md` | **THE rulebook** — `script_writer.load_spec()` reads it; the writer prompt embeds its HARD RULES + HOW-TO-WRITE. Change a rule HERE, every path follows. |
| `9_PROMPTS/COURSE_SPLICE_PROMPT.md` | Course/knowledge splice rules (the owner's 2 prompts, verbatim). |
| `9_PROMPTS/video_scripts/*.md` (36) | Hand-authored sample scripts → few-shot style examples (`script_writer._fewshot()`). |
| `2_KNOWLEDGE/domain_skills/{copywriting,ogilvy,stop-slop,seo-audit,content-strategy}` | Craft knowledge behind hooks / anti-slop / SEO. |
| `news_video_standards.CORE_PRONUNCIATION_LEXICON` (94) | English→VN phonetics so the voice reads terms right. |

## Which writer runs (all now go through the pipeline)
| Pipeline | Entry | Writer | Verify |
|---|---|---|---|
| **B — GitHub one-shot** | `make_video.py <url>` | LLM `_gemini_script` (system prompt = the shared `script_writer._system_prompt()` → ONE rulebook + a small GitHub delta; no duplicated grounding) → deterministic fallback | `script_writer.verify()` gate + rewrite (fabrication triggers retry) |
| **C — freeform / news text** | `video_engine._create_from_text` | `scene_writer.write_scenes` → tries `script_writer.generate_script()` first (verified), then its own prompt, then deterministic | `script_writer.verify()` gate |
| **D — course/knowledge** | `course_planner.plan_course` | loads `COURSE_SPLICE_PROMPT.md` (100% real SRT text preserved) | **`spec_lint.lint_course` now auto-runs inside `plan_course`** (structure / duplicate part / hook / loop-back); traceability N/A — the words are the teacher's real transcript, nothing generated |
| **A — agent (highest quality)** | Scene-Composer skill (Claude) | Claude writes per `.agents/skills/scene-composer/SKILL.md` → MASTER_VIDEO_SPEC + domain_skills | **ENFORCED at render**: `native_composer.make_video` calls `script_writer.enforce_before_render()` — the agent path can no longer skip the language/dup/moderation/structure floor. `SEOSONA_VERIFY_STRICT=1` makes hard errors abort. |

## THE RULE for adding a new path
A new script source MUST go through all six stages of `script_writer` (at minimum call `verify()` before
render). **Do NOT hardcode a new system prompt** — extend the shared one, or load MASTER_VIDEO_SPEC.
No path may skip VERIFY. This is the guardrail against the fragmentation this pipeline just fixed.

## LLM chain (who actually writes) — REAL LLMs first, deterministic is the LAST resort
Script writing calls `llm_engine.generate_scenes_json()`, a REAL-LLM-only cascade in the owner's
preferred order: **Gemini → Z.ai GLM (free cloud) → OpenAI → Ollama (local/free) → Claude** — each
shape-validated (must return a non-empty `scenes` JSON), retrying the NEXT tier on failure/bad-shape. It NEVER touches the offline
social/thumbnail NLP router (which can't write scenes). Returns None only when EVERY real LLM fails →
the caller's deterministic template writer runs (grounded, honest, but formulaic) — a true last resort.
- **Gemini rotates multiple keys** (`GEMINI_API_KEY`, `GEMINI_API_KEY_2..10`, or comma `GEMINI_API_KEYS`)
  — a 429 on one key auto-falls to the next, multiplying the free quota (verified: key#1 exhausted →
  key#2 wrote the scenes).
- **Z.ai GLM-4.5-Flash** is a genuinely-free cloud tier (OpenAI-compatible, ~1 QPS) — more capable than
  a 12GB-local model; verified writing natural VN scenes. Effective cloud tier when all Gemini keys 429.
- **Ollama `gemma3:12b` is the always-on free floor** (`num_predict:2048` so scene JSON isn't truncated,
  `keep_alive:30m` so it stays warm). With it running, deterministic essentially never triggers even
  when every cloud tier is 429.
- **Claude ("bạn")** is dormant until `ANTHROPIC_API_KEY` is set; then it's an automated tier. Agent-mode
  (path A) remains the interactive "bạn" for hard topics.
- `SEOSONA_REQUIRE_LLM=1` → abort instead of ever using the deterministic writer (quality-strict mode).
Verification runs on whatever wrote it, LLM or deterministic.
