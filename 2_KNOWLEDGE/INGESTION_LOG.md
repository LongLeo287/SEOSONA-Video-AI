# Ingestion log

Audit trail of every external repo/knowledge ingested into SEOSONA Video. Process:
`6_SOP/REPO_VETTING_SOP.md`. One line per ingestion: date · source · license · what · where · why.

| Date | Source | License | What was taken | Where | Why |
|------|--------|---------|----------------|-------|-----|
| 2026-06-29 | boraoztunc/skills | Apache-2.0 (ogilvy: MIT) | 13 domain SKILL.md (SEO, copywriting, content, CRO, design/UX) | `2_KNOWLEDGE/domain_skills/` | ground video content in real SEO/marketing/design expertise |
| 2026-06-29 | nextlevelbuilder/ui-ux-pro-max-skill | MIT | 4 design SKILL.md (design-system, brand, ui-styling, banner-design) | `2_KNOWLEDGE/domain_skills/` | deeper on-screen/design + brand + thumbnail craft (non-dup with boraoztunc) |
| 2026-06-29 | VinAIResearch/PhoWhisper (vinai/PhoWhisper-medium) | BSD-3 | CT2 int8 convert → bundled model | 7_ASSETS/models/phowhisper-medium-ct2 | best VN ASR (−40% WER vs Whisper); medium = ~2x faster/½ size of large, ~same WER |
| 2026-06-29 | D:\SEOSONA AIideo talking heads (4 reels) | reference | style references (caption/card/transition craft) | 2_KNOWLEDGE/style_references/talking_head/ | learn talking-head editing craft + new template ideas (SKILL.md was dup → skipped) |
| 2026-06-29 | SEOSONA proposals (2 PDF, internal) | internal/own | extracted text (markitdown) → brand facts | 3_MEMORY/brand_memory/proposals_extracted/ + filled .claude/product-marketing-context.md | learn the real SEOSONA brand (services/C.B.O/proof/CTA) |
| 2026-06-29 | coderamp-labs/gitingest | MIT | pip dependency (CLI repo→text digest) | requirements.txt | SYSTEM: turn any repo into one text blob for fast analysis/vetting |
| 2026-06-29 | facebook/astryx | MIT | REFERENCE only (design-system/token patterns) | REPO_WATCHLIST.md | FACTORY: SEOSONA has DESIGN.md+craft; reference astryx for token/system ideas, don't vendor the React lib |
| 2026-06-29 | microsoft/markitdown | MIT | pip dependency + wrapper | `2_KNOWLEDGE/scripts/ingest_source.py` + requirements.txt | SYSTEM: turn any PDF/DOCX/URL → clean markdown to learn from (ingestion capability) |
| 2026-06-27 | nexu-io/open-design | Apache-2.0 | HyperFrames craft (motion-principles, css-patterns, palettes, transitions) | `2_KNOWLEDGE/hyperframes/craft/` | richer, on-brand motion for the 14 components |
| 2026-06-27 | digitalsamba/claude-code-video-toolkit | MIT | WPM-pacing insight + ffmpeg/brand refs | `2_KNOWLEDGE/external_toolkits/claude-code-video-toolkit/` | fix voice pacing variance (ported into native_composer) |

| 2026-06-29 | swivid/f5-tts | MIT code / **CC-BY-NC weights** | F5 BACKUP voice path (gated, subprocess-isolated) | `2_SKILLS/voice_cloner/f5_backup.py` + voice_router | redundant clone-voice backup; DORMANT (base non-commercial; needs commercial VN ckpt) |
| 2026-06-29 | yt-dlp/yt-dlp | Unlicense | (planned) footage-sourcing util — pin as tool | (backlog) `scripts/source_footage.py` | robust download for course footage |

| 2026-06-29 | huytranvan2010/AI-auto-generate-video | (analyzed) | sync principle: audio=master clock, captions from real audio timings (not estimated) | applied →  ASR-anchored karaoke | fix karaoke-voice drift |

| 2026-06-29 | hoquanghai/Auto-Create-Video | MIT | (analyzed) confirms scene-level audio-master sync (HyperFrames, VN); port idea: 8ms boundary micro-fade + SFX-from-measured-starts | (backlog) | sync validation + anti-click |

| 2026-06-29 | k2-fsa/OmniVoice | Apache-2.0 | (analyzed) VN TTS + clone YES but NO word-timestamps + torch2.8 conflict → not sync-friendly | REPO_WATCHLIST | future VN A/B only |

| 2026-06-29 | (lineage note) | — | AI-auto-generate-video = FORK of hoquanghai/Auto-Create-Video; both build on nexu-io/html-video (HTML→video) + use k2-fsa/OmniVoice (local VN TTS server :8123, NO SRT) | — | understand the repo family |
| 2026-06-30 | huytranvan2010/AI-auto-generate-video + loha-video-maker SKILL | MIT (repo) | CRAFT adopted (re-skinned to brand, light-only): liquid brand-colour depth blobs (gsap), fitText auto-scale, semantic SFX override, REAL screenshot in mockup/repo scene (Playwright via system Edge), multi-screenshot (2 imgs/video), verify-gate wiring + ready-to-post sidecars (voice.mp3/script.txt/caption.txt) | `4_BRAIN/native_composer.py` · `make_video.py` · `scripts/capture_shot.js` | FACTORY: design-led visuals + post-ready output. Their dark-neon palette + OmniVoice NOT taken |
| 2026-06-30 | google/agents-cli | Apache-2.0 | (analyzed) PATTERN only — "Quality Flywheel" → built native `eval_judge.py` (Gemini-vision judge, 3-tier fallback) + `eval_run.py` + `1_CONFIG/eval_datasets/`. Skill-authoring patterns noted | `4_BRAIN/eval_judge.py` · `eval_run.py` · `6_SOP/EVAL_FLYWHEEL.md` | SYSTEM/QA: qualitative judge metadata can't do. Google-Cloud/Vertex/BigQuery/GEPA REJECTED (paid/cloud, conflict free-local) |

## Rejected (logged so we don't re-evaluate)
| Source | Why rejected |
|--------|--------------|
| fishaudio/fish-speech | non-commercial license + torch 2.8 (breaks env) |
| coqui-ai/TTS | unmaintained (shut down) + no Vietnamese |
| RVC-Boss/GPT-SoVITS, OpenMOSS/MOSS-TTSD, voice-pro, voicebox | no Vietnamese |
| K07VN/capcut-tts-api | no LICENSE + reverse-engineered cloud API |
| WEIFENG2333/VideoCaptioner | GPL-3.0 |
| social-auto-upload, opencut, palmier-pro, capcut-cli, openreel | whole apps/editors or no license — reference only |
| ToolJet, Prometheus | whole low-code/monitoring platforms — over-engineer a local log dashboard |
| firecrawl, browser-use, Scrapling | heavy crawl/browser frameworks — native RSS fetch (requests+xml) is the right size |
| MoneyPrinterTurbo, KrillinAI, autoshorts | full video pipelines — would conflict with native_composer (don't rebuild) |
| gsap/anime/lottie skills (boraoztunc) | duplicate — SEOSONA already has the HyperFrames craft library |
| awesome-seo (awesomelistsio/teles), awesome-ui (kevindeasis), awesome-digital-marketing (paulbradish) | **no LICENSE file** → not vendored (SOP step 2); referenced by link in `domain_skills/INDEX.md` |
