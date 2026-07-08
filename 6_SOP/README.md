# 6_SOP — Standard Operating Procedures (index)

40 SOPs, grouped below for navigation. Kept flat (not subfoldered) because they are
cross-referenced by skills/agents and actively edited — moving them would break refs.
To add a new SOP, drop it here and add a line to the right group below.

## 🎬 Production — how to make each output
| SOP | Use for |
|-----|---------|
| `video_production_sop.md` | the core video production procedure |
| `tech_news_faceless_sop.md` | faceless Vietnamese tech-news videos (the default format) |
| `COURSE_VIDEO_SOP.md` | course/knowledge (talking-head): current pipeline (course_video.py + course_planner + splice matrix) + B2B-expert aesthetic |
| `talking_head_sop.md` | engine #2 overview: edit filmed/screen-rec footage with REAL voice (see COURSE_VIDEO_SOP for the course pipeline) |
| `repurposer_sop.md` | long-to-short repurposing |
| `carousel_sop.md` | social carousels |
| `thumbnail_sop.md` | thumbnails |
| `SEOSONA_VIDEO_AUTONOMOUS_TEMPLATE_FACTORY.md` | the autonomous template-factory flow |

## ✍️ Script & Architecture
| SOP | Use for |
|-----|---------|
| `SCRIPT_WRITING_PIPELINE.md` | the ONE path all narration goes through (6 stages: research→analyze→reason→plan→write→verify + LLM cascade) |
| `VIDEO_ARCHITECTURE.md` | one shared spine + two branches (news animated vs talking-head footage): what's shared vs branch-specific |
| `EFFECT_LIBRARY_PLAN.md` | native effect/SFX/transition library (4th library layer) build plan |

## 🎙️ Voice & Audio
| SOP | Use for |
|-----|---------|
| `voice_cloning_tts_sop.md` | voice cloning / TTS procedure |
| `VOICE_TTS_ENGINE_ROUTING.md` | which TTS engine to use (**OmniVoice primary → VieNeu backup**; single router, no dead branches; edge-tts/F5/LoRA/fish removed) |
| `brand_voice_sop.md` | SEOSONA brand voice rules |
| `CHIQUYET_VOICE_STYLE.md` | CQA branch: Chí Quyết rhythm/style profile (from 19.6h lectures) + LoRA clone voice (brand=cqa only) |

## 🖥️ Render Engine (HyperFrames)
| SOP | Use for |
|-----|---------|
| `RENDER_ENGINE_DECISION.md` | engine decision (HyperFrames sole) + render config + recipes |
| `HYPERFRAMES_INTEGRATION.md` | HyperFrames integration details + vendor-dir source-of-truth map |
| `REFERENCE_TO_VIDEO_SOP.md` | reference-to-video conversion procedure |
| `TEMPLATE_MAP.md` | template library map |

## 📣 Publishing & SEO
| SOP | Use for |
|-----|---------|
| `publishing_checklist.md` | pre-publish checklist |
| `youtube_seo_sop.md` | YouTube SEO |
| `YOUTUBE_CHANNEL_OPERATIONS_MCP.md` | channel operations (MCP) |
| `GOOGLE_DRIVE_SHEETS_LAYER.md` | Drive/Sheets management layer — publish-output vs manage-everything (two roles); credential setup |
| `SEO_CONTENT_STRATEGY.md` | content strategy |

## 🗺️ System, Operation & Maps
| SOP | Use for |
|-----|---------|
| `AUTONOMOUS_FACTORY_LOOP.md` | 🌟 NORTH-STAR: the autonomous self-improving factory (OODA loop, component blueprint, guardrails, build plan) |
| `SELF_IMPROVEMENT_LOOP.md` | 🔄 How the SYSTEM learns & upgrades itself — 9-stage capability loop (discover→analyze→security→decide→adapt→build→verify→wire→record); umbrella over vetting/ingestion/eval/freshness |
| `LLM_CODING_DISCIPLINE.md` | Agent behavior guardrails (Karpathy 4: think-before-coding · simplicity-first · surgical-changes · goal-driven) — pairs with persona Execution Contracts |
| `EVAL_FLYWHEEL.md` | Qualitative QA: Gemini-as-judge grades narration/brand/visual (free) + regression eval set — `npm run eval` |
| `MASTER_OPERATION.md` | top-level operation manual |
| `SEOSONA_VIDEO_RECONNECTION_MAP.md` | how the system pieces connect (resolver contract, OS binding, audit semantics) |
| `SEOSONA_WORKFLOW_BOUNDARY_MAP.md` | workflow boundaries |
| `PRODUCT_ROADMAP.md` | product roadmap |
| `LOOP_OPERATING_SOP.md` | operating the autonomous loop safely (circuit breaker + STOP kill-switch) |
| `REPO_VETTING_SOP.md` | vetting external repos before ingesting (take pattern, not artifact) |
| `DEPENDENCIES.md` | dependencies & APIs status |
| `DASHBOARD_BUILD_PLAN.md` | management dashboard phased build plan |
| `UPGRADE_BACKLOG.md` | upgrade backlog from repo vetting |
| `QA_CAPTIONS_FINDINGS.md` | QA findings — RULE #1 captions & timing sync |

## 🎨 Design & Automation
| SOP | Use for |
|-----|---------|
| `UX_UI_DESIGN_GUIDELINES.md` | UX/UI + visual design (incl. Light Mode law) |

---

> **Consolidated (2026-06-27):** 3 non-production SOPs were moved to
> (removed) (recoverable, not deleted):
> `EXTERNAL_VIDEO_REPO_CAPABILITY_MAP.md` (one-time 2026-06-19 ingestion decision log),
> `INGESTION_RULES.md` (knowledge-ingestion protocol — see `2_KNOWLEDGE/INGESTION_INDEX.md`),
> `OBSCURA_BROWSER_AUTOMATION.md` (optional browser runtime one-pager).
