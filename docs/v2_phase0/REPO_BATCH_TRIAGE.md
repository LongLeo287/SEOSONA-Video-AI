# Repo Batch Triage — RAP Step 1 (dedup-first, metadata-only)

**Date:** 2026-07-15 · **Input:** `REPO_BATCH_INBOX.md` (~110 repos incl. bundled sub-repos).
**Method:** Light-touch classification only — NO cloning, NO CLI scans. Prior SEOSONA verdicts
(`2_KNOWLEDGE/INGESTION_LOG.md`) and roster coverage (`VIDEO_SKILL_AGENT_ROSTER.md`,
`BACHDYON_REFERENCE_ANALYSIS.md`) cited instead of re-derived. A handful of genuinely-unknown repos
had their README/license WebFetched (cheap) to classify honestly; where a license could not be cheaply
confirmed it is marked "unverified — confirm in deep-RAP" (no guessed licenses).

**Buckets:** A = owned/is-our-engine · B = already-vetted or roster-covered · C = skip (doctrine) ·
D = deep-RAP shortlist (survives to Step 2).

## Counts
| Bucket | Count |
|--------|-------|
| **A · OWNED / IS-OUR-ENGINE** | 6 |
| **B · ALREADY-VETTED / ALREADY-COVERED** | 54 |
| **C · SKIP (doctrine)** | 33 |
| **D · DEEP-RAP SHORTLIST** | 5 |
| **Total distinct repo lines** | 98 |

(The inbox's "~110" counts remotion's 6 bundled sub-repos and the nexu-io/anthropics/openai skill
variants as separate items; deduped to distinct repos this is 98.)

---

## A · OWNED / IS-OUR-ENGINE (6) — no action
| Repo | Capability | License | Cited | Rationale |
|------|-----------|---------|-------|-----------|
| k2-fsa/OmniVoice | VN TTS + voice clone | Apache-2.0 | engine doctrine; INGESTION_LOG 2026-06-29 | **OUR core voice engine** (voice_router/omnivoice_engine). |
| openai/whisper | ASR base | MIT | asr_router doctrine | Our ASR = PhoWhisper-large-ct2 (Whisper architecture); Whisper is the tool we already build on. |
| greensock/GSAP | Web animation | MIT (now fully free) | hyperframes render | Our HyperFrames render drives **seek-safe GSAP** already. |
| microsoft/playwright | Headless browser render | Apache-2.0 | INGESTION_LOG (capture_shot.js, element_maker) | Tool we already use for HTML→frame seek-render + screenshots. |
| yt-dlp/yt-dlp | Media downloader | Unlicense | INGESTION_LOG 2026-06-29 (source_footage) | Tool we already pin for footage sourcing. |
| FFmpeg/FFmpeg | Encode/mux/filters | LGPL/GPL (tool, not vendored) | native_composer doctrine | Core render/mux tool we already invoke. |

---

## B · ALREADY-VETTED / ALREADY-COVERED (54) — cite verdict/role, no deep-RAP
| Repo | Capability | License | Prior verdict / roster role | Rationale |
|------|-----------|---------|-----------------------------|-----------|
| greensock/gsap-skills | GSAP agent instructions | MIT | INGESTION_LOG 2026-06-30 REFERENCE | ~90% dup with `hyperframes/craft/motion-recipes`. |
| heygen-com/hyperframes | HTML→video render engine | Noncommercial | prior HyperFrames verdict (NC REFERENCE) | We OWN the engine lineage (5_FRAMEWORK/hf_engine); drive it, don't vendor. |
| nexu-io/html-video | Browser video studio UI | Apache-2.0 | INGESTION_LOG 2026-07-02 REFERENCE | Studio-UI blueprint already logged (dashboard backlog). |
| nexu-io/html-anything | Agentic HTML editor + templates | Apache-2.0 | INGESTION_LOG 2026-07-02 REFERENCE | Template/agent-detection patterns already mined. |
| nexu-io/open-design | HyperFrames craft (motion/palette) | Apache-2.0 | INGESTION_LOG 2026-06-27 INGESTED | Already in `2_KNOWLEDGE/hyperframes/craft/`. |
| juliangarnier/anime | JS animation lib | MIT | roster #8 / hyperframes craft | Motion capability owned via GSAP + craft library. |
| RayVentura/ShortGPT | Stock-footage-over-VO pipeline | MIT | INGESTION_LOG 2026-07-06 REFERENCE | We surpass on render/captions/ASR/TTS. |
| harry0703/MoneyPrinterTurbo | Topic→short pipeline | MIT | roster #6/#7; Rejected-list (pipeline) | Voice=OmniVoice better, asset-sourcer have; don't rebuild pipeline. |
| huytranvan2010/AI-auto-generate-video | HTML→video (VN) | MIT | INGESTION_LOG 2026-06-29 ADOPTED | Craft already adopted (audio-master sync). |
| hoquanghai/Auto-Create-Video | HTML→video (VN) | MIT | INGESTION_LOG 2026-06-29 analyzed | Scene-level sync idea already noted. |
| ATH-MaaS/Pixelle-Video | Full auto-video engine | Apache-2.0 | INGESTION_LOG 2026-06-30 REFERENCE | Pixelle-Video already assessed; AI-illustration conflicts brand. |
| Huanshere/VideoLingo | Subtitle/translate/dub | Apache-2.0 | INGESTION_LOG 2026-06-30 (C-tier) | Revisit only if multilingual/dubbing expansion. |
| calesthio/OpenMontage | Declarative video pipeline | AGPL-3.0 | INGESTION_LOG 2026-06-30 (deep) | Deeply analyzed; hook/arc patterns already adopted; AGPL copyleft. |
| Hommy-master/capcut-mate | CapCut draft automation | Apache-2.0 | INGESTION_LOG 2026-06-30 (CapCut dig) | CapCut = handoff-only (capcut_export.py); no free headless render. |
| vanloctech/youwee | yt-dlp GUI + ASR + Telegram | MIT | INGESTION_LOG 2026-07-02 SKIP-DUP | Download+ASR+telegram already covered. |
| multica-ai/andrej-karpathy-skills | LLM-coding principles | MIT | INGESTION_LOG 2026-06-30 ADOPTED | → LLM_CODING_DISCIPLINE.md. |
| mvanhorn/last30days-skill | Recency topic discovery | MIT | INGESTION_LOG 2026-06-30 HARVEST/BUILT | Wired into discovery/researcher. |
| dexhunter/seedance2-skill | Seedance prompt craft | unverified | INGESTION_LOG 2026-07-15 (Seedance pack EXTRACT) | Prompt grammar already folded into Engine #6. |
| nextlevelbuilder/ui-ux-pro-max-skill | Design/brand skills | MIT | INGESTION_LOG 2026-06-29 ADOPTED | 4 design skills already in domain_skills. |
| bradautomates/claude-video | Video comprehension skill | MIT | INGESTION_LOG 2026-07-11 REFERENCE | Perception (opposite of production). |
| digitalsamba/claude-code-video-toolkit | Remotion/moviepy toolkit | MIT | INGESTION_LOG 2026-07-11 HARVEST | Caption-align/pacing nuggets already taken. |
| feicaiclub/video-spec-builder | Interactive spec skill | MIT | INGESTION_LOG 2026-06-30 REFERENCE | Scene-tag vocab already mined into VIDEO_CRAFT_RULES. |
| github/spec-kit | Spec-driven-dev method | MIT | INGESTION_LOG 2026-06-30 REFERENCE | Discipline covered by SIL + LLM_CODING_DISCIPLINE. |
| msitarzewski/agency-agents | 232 agent personas | MIT | INGESTION_LOG 2026-07-01 REFERENCE | Already in watchlist. |
| garrytan/gstack | Agent workflow patterns | MIT | INGESTION_LOG 2026-06-30 REFERENCE | Sprint/review patterns dup with our discipline. |
| nidhinjs/prompt-master | Prompt grounding | MIT | INGESTION_LOG 2026-06-30 ADOPTED | Grounded `_gemini_script` already. |
| NVIDIA/SkillSpector | Skill/repo security scanner | Apache-2.0 | INGESTION_LOG 2026-06-30 ADOPTED | → scripts/security_scan.py. |
| HKUDS/AutoAgent | NL→agent framework | MIT | INGESTION_LOG 2026-07-06 REFERENCE | Every capability lighter+purpose-built already. |
| anthropics/skills | Official skills (docx/pptx/pdf) | mixed permissive | roster canonical skill format | Skill format learned; office-doc skills off video-core. |
| openai/skills | Skill examples | unverified | roster canonical skill format | Skill format already covered by SKILL_TEMPLATE_ANALYSIS. |
| remotion-dev/skills | Remotion motion skills | unverified | roster #8/#14; Remotion doctrine | Engine mismatch (HyperFrames); archetype coverage via #8. |
| daymade/claude-code-skills | Skill catalog | unverified | prior catalog-scan class | Catalog REFERENCE (cf batch8/9 scans). |
| alirezarezvani/claude-skills | Skill catalog | unverified | prior catalog-scan class | Catalog REFERENCE. |
| chubbyguan/chubbyskills | Skill catalog | unverified | prior catalog-scan class | Catalog REFERENCE. |
| numman-ali/openskills | Skill framework | unverified | prior catalog-scan class | Framework REFERENCE (we run on Claude Code). |
| obra/superpowers | Agent dev methodology | MIT | INGESTION_LOG discipline class | Dup with SIL + LLM_CODING_DISCIPLINE. |
| gsd-build/get-shit-done | Agent workflow | unverified | discipline class | Dup with our discipline. |
| Yeachan-Heo/oh-my-codex | Codex agent config | unverified | agent-runtime class | We don't adopt another runtime. |
| affaan-m/ECC | Agent-harness optimizer | MIT | discipline class | skills/memory/security dup with SIL/security_scan. |
| walkinglabs/learn-harness-engineering | Agent-harness course | MIT | discipline class | Knowledge dup with our harness discipline. |
| JuliusBrussee/caveman | Agent-output token compression | MIT | INGESTION_LOG (headroom/OmniRoute N/A) | Token-compression already decided N/A (small free-local prompts). |
| promptslab/Awesome-Prompt-Engineering | Prompt awesome-list | Apache-2.0 | INGESTION_LOG (prompts.chat class) | Generic prompt collection; we have tuned per-stage prompts. |
| bytedance/deer-flow | Deep-research framework | MIT | researcher.py + deep-research skill | Research capability covered. |
| mem0ai/mem0 | Agent memory | Apache-2.0 | knowledge_graph second-brain | Memory covered by our KG. |
| supermemoryai/supermemory | Agent memory | unverified | knowledge_graph second-brain | Memory covered. |
| MemPalace/mempalace | Agent memory | unverified | knowledge_graph second-brain | Memory covered. |
| HKUDS/RAG-Anything | Multimodal RAG | unverified | INGESTION_LOG 2026-06-30 (RAG-infra REFERENCE) | markitdown+gitingest cover ingestion. |
| Egonex-AI/Understand-Anything | Multimodal understanding | unverified | RAG/ingestion class | Ingestion/understanding covered. |
| google-labs-code/design.md | Design-system doc skill | unverified | DESIGN.md brand contract | We already have DESIGN.md + craft. |
| shadcn-ui/ui | React component lib | MIT | ant-design lesson (mine craft, not React) | Design craft applicable by hand; don't vendor React. |
| imskyleen/animate-ui | Animated React components | unverified | roster #8 / motion craft | Motion recipes covered; React runtime N/A. |
| mui/material-ui | React component lib | MIT | ant-design lesson | Design craft by hand; don't vendor React. |
| DietrichGebert/ponytail | Lazy/reuse-ladder philosophy | MIT | INGESTION_LOG 2026-06-30 REFERENCE | Already folded into LLM_CODING_DISCIPLINE. |
| microsoft/playwright-mcp | Browser MCP | Apache-2.0 | INGESTION_LOG batch9 MAP-skip | Not needed (we drive Playwright directly). |

---

## C · SKIP (doctrine) (33) — say which reason
| Repo | Capability | License | Reason |
|------|-----------|---------|--------|
| remotion-dev/remotion (+ template-tiktok, template-prompt-to-motion-graphics-saas, html-in-canvas, anime-example, transitions-video) | React video framework | MIT-ish | **Different render engine** — doctrine = HyperFrames, not Remotion. |
| OpenTalker/video-retalking | Audio-driven lip-sync | Apache code / tainted weights | **Lipsync/avatar line REMOVED 2026-07-14** + license-tainted (prior verdict). |
| OpenMOSS/MOVA | Audio-visual diffusion avatar | Apache-2.0 | Lipsync/avatar line removed (INGESTION_LOG 2026-07-03 REFERENCE). |
| jianchang512/pyvideotrans | Video translate/dub GUI | GPL-3.0 | GPL copyleft; algorithm already extracted clean-room → dub_align.py. |
| Comfy-Org/ComfyUI | Node diffusion GUI | GPL-3.0 | GPL + local heavy gen removed for speed (prior REFERENCE). |
| comfy-org/comfyui | (same, dup casing) | GPL-3.0 | Duplicate of above. |
| wyrde/wyrde-comfyui-workflows | ComfyUI workflow packs | unverified | Local heavy gen (LTX) removed doctrine. |
| WEIFENG2333/VideoCaptioner | Caption/subtitle app | GPL-3.0 | GPL copyleft (prior Rejected list). |
| OpenCut-app/OpenCut | Full web video editor | MIT | Whole editor app (prior Rejected: "opencut whole editor"). |
| Augani/openreel-video | Web video editor | unverified | Whole editor app (prior Rejected: "openreel"). |
| HITsz-TMG/VideoClaw | Paid cloud gen-video | MIT | Paid-cloud gen breaks free-local rule (INGESTION_LOG 2026-07-02 SKIP). |
| sherlockchou86/VideoPipe | C++ CV analysis pipeline | Apache-2.0 | Off-domain (object/face/behavior detection), C++ wrong stack. |
| OpenMOSS/MOSS-TTS | TTS (no Vietnamese) | unverified | No Vietnamese (cf MOSS-TTSD rejection). |
| debpalash/OmniVoice-Studio | Offline dictation/clone/dub desktop | AGPL-3.0 | AGPL copyleft; dub ~ covered by OmniVoice+dub_align (name collision, not our core). |
| FujiwaraChoki/MoneyPrinterV2 | Income automation (twitter/affiliate) | AGPL-3.0 | AGPL + off-core (not a video renderer). |
| timoncool/videosos | Browser AI video editor | MIT | Paid gen (fal/Runware) + lip-sync — doctrine mismatch. |
| Agent-Field/reels-af | Article→reel multi-agent | Apache-2.0 | Paid-cloud-only (OpenRouter/Gemini/Veo); full pipeline we have native. |
| SamurAIGPT/Generative-Media-Skills | Media-gen agent skills | MIT | Paid muapi.ai gen (Midjourney/Flux/Kling/Suno). |
| browser-use/browser-use | Browser automation framework | MIT | Heavy browser framework (prior Rejected); native fetch right-size. |
| unclecode/crawl4ai | AI web crawler | Apache-2.0 | Heavy crawl framework (prior Rejected class); native RSS preferred. |
| NanmiCoder/MediaCrawler | Social-media scraper | unverified | Scraping framework; ToS/ethics risk; native fetch preferred. |
| HKUDS/CLI-Anything | NL→CLI helper | unverified | Off-domain (not video). |
| TencentCloud/TencentDB-Agent-Memory | Cloud-DB agent memory | unverified | Cloud-DB-bound; memory covered by our KG. |
| aagarwal1012/Animated-Text-Kit | Flutter text animations | MIT | Wrong stack (Flutter/Dart); text-effects covered by effect_library. |
| CameronFoxly/Ascii-Motion | ASCII/ANSI art animator | MIT core / proprietary premium | Off-brand niche for clean tech-editorial; dual-license. |
| harness/harness | CI/CD DevOps platform | PolyForm/mixed | Off-domain (software delivery, not video). |
| deepflowio/deepflow | eBPF observability | Apache-2.0 | Off-domain (network/app observability). |
| GargantuaX/gemini-watermark-remover | Watermark removal via Gemini | unverified | Paid Gemini + ethical/off-scope. |
| Diolinux/PhotoGIMP | GIMP-as-Photoshop config | unverified | Out of scope (image-editor config) — inbox-flagged. |
| YouMind-OpenLab/awesome-gpt-image-2 | GPT image-gen prompt list | unverified | Paid image-gen, out of scope. |
| liquidslr/system-design-notes | System-design learning notes | unverified | Out of scope (learning ref). |
| ByteByteGoHq/system-design-101 | System-design learning | unverified | Out of scope (learning ref). |
| asgeirtj/system_prompts_leaks | Leaked system prompts | unverified | Out of scope (not video). |

---

## D · DEEP-RAP SHORTLIST (5), RANKED — survives to Step 2 (clone + real-CLI scan)

These are the only genuinely-NEW, roster-relevant, plausibly-usable survivors. RAP dedup discipline
kept this small on purpose: SEOSONA has already ingested most of this space, so the honest yield is a
short, high-signal queue rather than a padded 15–30. **Extract craft, never vendor; keep keyless/local
+ LIGHT brand.**

### 1. HKUDS/ViMax → roster **#1 Director agent** (⚓ anchor) + #4 Scene-planner
- **Why new/valuable:** the roster's Director is grounded in ViMax at README level only — it has never
  been cloned+scanned to actually extract the crew structure. ViMax is the canonical MIT source for the
  "director is glue, crew emits a TYPED plan" pattern that the whole V2 MVP hangs on.
- **Extract (never vendor):** the multi-agent crew decomposition + the typed `ProductionPlan` schema
  shape (shotlist/timing/style/voiceSpec/assetQueries/renderCmd) → inform our native Director glue over
  SEOSONA engines. NOT its model/API stack.
- **License read:** MIT (per roster license notes) — patterns adoptable; confirm LICENSE file in deep-RAP.

### 2. Leonxlnx/taste-skill → roster **#5 Subtitle-stylist / #8 Archetype / #11 QA-aesthetics**
- **Why new/valuable:** keyless, local SKILL.md set (63.8k★, MIT) encoding *aesthetic taste* rules —
  layout, typography pairing/scale, motion, spacing — to push AI-generated on-screen design past
  "generic." Directly serves on-screen text/card quality, a real polish gap, and doctrine-clean (no
  paid API, pure instruction files).
- **Extract:** the typography/spacing/hierarchy heuristics → parametrize ASS caption styles (#5) and
  archetype `TemplateSpec` polish (#8); reuse as a QA-aesthetics rubric (#11). Rewrite prose fresh
  (branding standard); keep SEOSONA LIGHT palette.
- **License read:** MIT (core skills) — confirm in deep-RAP; premium/image-gen bits ignored.

### 3. zhouxiaoka/autoclip → roster **#13 Repurpose skill**
- **Why new/valuable:** MIT, 6k★, actively-maintained long→short **highlight extraction with LLM
  scoring** (YouTube/Bilibili DL → intelligent highlight selection → compilation). V2 has autocut
  (dead-air removal) but no *virality/highlight scoring* to pick the best clip windows.
- **Extract:** the highlight-scoring heuristics + segment-ranking logic → build keyless #13 (swap their
  paid DashScope LLM for our resilient llm_engine cascade; download via our yt-dlp path). NOT vendored.
- **License read:** MIT (WebFetched) — clean; LLM dependency is swappable, so keyless-adaptable.

### 4. SamurAIGPT/AI-Youtube-Shorts-Generator → roster **#13 Repurpose skill** (dedup vs #3)
- **Why new/valuable:** the roster's named source for #13 (EXTRACT: virality scoring + speaker crop).
  Adds **auto face-crop / reframe** to the highlight-scoring capability.
- **Extract:** virality-scoring signal + the 9:16 speaker-crop/reframe logic.
- **License read:** unverified — roster flags it "unclear license → verify before copying." **Confirm in
  deep-RAP.** DEDUP NOTE: #3 (autoclip) and #4 serve the SAME role #13; Step 2 should scan both and keep
  ONE — autoclip is likely the cleaner base (confirmed MIT, higher stars), this one contributes the crop
  logic if its license clears.

### 5. charlie947/social-media-skills → roster **#15 Publisher / #16 Reporter** (NEW roles, thin sources)
- **Why new/valuable:** MIT (1.8k★) markdown workflows for per-platform posting (LinkedIn/IG/YouTube)
  + analytics interpretation — the roster's two NEWEST roles (#15 publish, #16 report) have the thinnest
  source coverage, and this is per-platform craft knowledge.
- **Extract:** the platform-specific posting/cadence/analytics *knowledge* only → seed #15/#16 playbooks.
  Their tooling (Apify + Gemini) is PAID → skip the tools, keep keyless where we build.
- **License read:** MIT (WebFetched) for the markdown; paid-API tool deps are out.

---

## Honest notes
- **Couldn't fully classify (license unverified, flagged):** the many "unverified" rows above are
  metadata-honest — most are B/C on capability/dedup grounds regardless of license, so license didn't
  gate the bucket. The one place it matters is **#4 AI-Youtube-Shorts-Generator** (D) — its license must
  be confirmed in deep-RAP before any extraction.
- **Marginal calls worth revisiting only if scope shifts:** imskyleen/animate-ui + shadcn/mui (motion/
  design craft — kept B, mine by hand only if a new archetype needs it); CameronFoxly/Ascii-Motion (C,
  off-brand — reconsider only for a novelty terminal/data-reveal element); Huanshere/VideoLingo (B,
  revisit only for a multilingual/dubbing expansion).
- **No fabricated licenses, no cloning.** WebFetch used cheaply on: autoclip, videosos, reels-af,
  Generative-Media-Skills, taste-skill, social-media-skills, OmniVoice-Studio, VideoPipe, MoneyPrinterV2,
  caveman, ECC, learn-harness-engineering, superpowers, Ascii-Motion.
