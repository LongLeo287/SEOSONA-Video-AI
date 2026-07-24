# V2 Repo Adoption Plan — mined from the SEOSONA Repo Inventory

> Source: Google Sheet `1nlVUS_opf2n7hpCNtph864lY_56AX7jOI5Px2ZaXoYg` ("Repo Inventory - Classified Tiered"),
> exported 2026-07-15 (1,539 classified rows: **151 S-Core**, 148 A-High, 458 B, 725 C, 6 D, 51 Q).
> Cross-referenced against: the sheet's own `Repo_Verdicts` tab (41 decided verdicts), `V2_Core_Engine` tab,
> `2_KNOWLEDGE/INGESTION_LOG.md` (~140 ingestion entries), Phase-0 ADRs (`docs/v2_phase0/ADR.md`), and the
> 2026-07-14 user decisions (OmniVoice-only TTS; lipsync/avatar line deleted; local LTX lane removed).
>
> Method note: "handled" = repo appears in INGESTION_LOG, Repo_Verdicts, or an ADR/user decision.
> ~13 targeted GitHub API lookups were done for ambiguous S-Core entries (license/desc/activity);
> everything else is judged from the sheet's own notes. Where the note is too thin, the action is **VERIFY**, not a guess.

## Known sheet-vs-ADR drift (fix in the sheet, do not re-litigate here)

The sheet's `V2_Core_Engine` tab still says whisper.cpp=ADOPT, WhisperX=ADOPT, VieNeu-TTS=CONDITIONAL.
**ADR-004 rejected whisper.cpp and WhisperX** (faster-whisper/CTranslate2 + PhoWhisper-large is the ASR
decision) and **ADR-003 made OmniVoice the only TTS** (VieNeu is the license-clean fallback only if the
NC stance changes). This plan follows the ADRs. Also: sheet S-Core is now 151 (was 149) — two rows were added since the memory snapshot.

---

## (a) Summary — S/A coverage

| Bucket | S-Core (151) | A-High (148) |
|---|---|---|
| LongLeo287 own repos (not adoption targets) | 23 | ~2 |
| Already handled (ingested / verdict / ADR / rejected) | ~76 | ~55 |
| **Unharvested (gap list below)** | **~52** | **~25 notable** (rest = off-product noise) |

Coverage by category (S-Core handled / total): Content-Video **41/50** (the core boundary is nearly exhausted — good),
RAG/Knowledge 11/14, Agent Skills 12/23, Agent Harness 7/31 (mostly deliberate — see cautions),
Frontend 3/9 (rest own repos), SEO 1/4 (rest own), LLM Infra 0/3, Scraping 2/4.

Headline: **the video-product categories are ~85% harvested already.** The remaining real product value is
concentrated in ~12 repos (top-10 below); the other ~40 unharvested S rows are dev-tooling for the agent
that builds V2, or miscategorized/own/noise.

---

## (b) THE GAP LIST — unharvested S-Core (and notable A-High), by V2 boundary

Actions: **ADOPT** (engine/adapter) · **EXTRACT** (pattern, clean-room) · **REFERENCE** (read, watchlist) · **SKIP** (with why) · **VERIFY** (sheet note too thin to judge).
Priority: P1 = high value now, P2 = later phase, P3 = nice-to-have.

### 1. Research / content evidence

| Repo | Tier | What it is | Action | V2 phase | Prio |
|---|---|---|---|---|---|
| bytedance/deer-flow | S | MIT long-horizon research SuperAgent (sandboxes, memories, subagents, message gateway) | EXTRACT — research fan-out + evidence-bundle shape for ResearchBundle; do NOT adopt the harness | P2 | P1 |
| browser-use/browser-use | S | Browser automation framework for AI agents | REFERENCE — Crawlee (conditional) + Playwright already cover V2 research fetch; revisit only if agentic browsing becomes a research need | P2 | P3 |
| alibaba/page-agent | S | In-page JS GUI agent, natural-language DOM control | REFERENCE — same reason; no headless-browser need it solves for us | P2 | P3 |
| firecrawl/firecrawl (A) | A | Crawl/scrape API (already used via API key in legacy researcher.py) | ALREADY-IN-USE — keep as hosted evidence provider behind the Research Worker adapter; self-host is overkill | P2 | P2 |
| autoscraper / Scrapling / scrapy (A) | A | Generic scraping frameworks | SKIP — Crawlee is the decided conditional crawler; three more crawlers add nothing | — | — |
| HKUDS/LightRAG (A) | A | Graph-based RAG | REFERENCE — V2 knowledge boundary is file-based (no vector DB decision); watchlist | P6 | P3 |

### 2. Script / creative craft

| Repo | Tier | What it is | Action | V2 phase | Prio |
|---|---|---|---|---|---|
| emilkowalski/skills | S | MIT 12.7k★ design-engineering skills: strict animation review, improve-animations planning, animation vocabulary | EXTRACT — fold the animation-review rubric into the creative lint + eval-judge rubric | P3–P4 | P1 |
| lottiefiles/motion-design-skill | S | MIT universal motion-design principles for agents (timing/easing/choreography, Disney principles) | EXTRACT — checklist rules into creative-layer lint (complements gsap-skills already extracted) | P3 | P1 |
| tuanminhhole/openclaw-skill-infographic (A) | A | OpenClaw infographic-generation skill | VERIFY — could feed the carousel/infographic lane; sheet note too thin | P6 | P3 |
| Cuongyd196/remotion-cuongit-template (A) | A | Remotion templates for technical-education shorts | REFERENCE — Remotion already verdict REFERENCE; template ideas only | P6 | P3 |
| msitarzewski/agency-agents (A) | A | Expert-agent library w/ personalities/processes/deliverables | REFERENCE — prompt-pattern ideas for the 5-role pipeline; low urgency | P2 | P3 |

### 3. Timeline / render / motion

| Repo | Tier | What it is | Action | V2 phase | Prio |
|---|---|---|---|---|---|
| diffusionstudio/lottie | S | MIT 4.8k★ "generate production-ready Lottie animations with Claude Code/Codex" | **ADOPT-as-adapter candidate** — the `V2_Core_Engine` tab already names "GSAP + Lottie adapters (EXTRACT)" as the motion runtime; this is the missing Lottie half | P3 | P1 |
| mermaid | S | Text→diagram JS library | ALREADY-IN-USE — SYSTEM_MAP + HyperFrames render Mermaid natively; nothing to adopt | — | — |
| hetpatel-11/Adobe_Premiere_Pro_MCP | S | MCP bridge to drive Premiere Pro | REFERENCE — V2 is a headless factory; only relevant if a human-NLE handoff lane opens (OTIO already covers interchange) | P6 | P3 |
| CapCut cluster (capcut-cli, pyJianYingDraft, VectCutAPI, capcut-mate, capcut-ai-editor) | S | CapCut/JianYing draft automation | DECIDED — verdicts exist (REFERENCE, P6); CapCut private format is not truth. No new work | P6 | — |
| mira-wm/mira | S | 5B real-time world model generating game video | SKIP — research toy; no GPU budget, no product fit | — | — |

### 4. Audio (TTS / ASR / dubbing)

| Repo | Tier | What it is | Action | V2 phase | Prio |
|---|---|---|---|---|---|
| OpenMOSS/MOSS-TTS | S | Apache-2.0 TTS family (long-form, multi-speaker, voice design, streaming) | REFERENCE — ADR-003 = OmniVoice only; this is the strongest re-evaluation candidate **if** the OmniVoice NC risk stance changes (check weight license then — code Apache, weights unverified) | P6 | P2 |
| codertapsu/multilingual-dubbed-video | S | MIT end-to-end local dub pipeline (transcribe→translate→TTS→align→mix→render) | EXTRACT — cross-check its align/mix stage order against dub_align + the VideoLingo extraction when building the V2 Localize lane | P3 | P2 |
| krillinai/KrillinAI (A) | A | GPL-3.0 10.5k★ full video translate/dub pipeline | REFERENCE clean-room only (GPL, same rule as pyvideotrans) — its subtitle-fit heuristics are the only part worth studying | P3 | P3 |
| rany2/edge-tts (A) | A | Microsoft Edge free TTS endpoint | SKIP — ADR-003 (OmniVoice only) + ToS/reliability risk of an unofficial endpoint in a commercial factory | — | — |
| abus-aikorea/voice-pro | S | Whisper+TTS+clone+YouTube-download WebUI | SKIP — every capability duplicated by decided engines; bundles yt-download ToS risk; nothing unique | — | — |
| jamiepine/voicebox | S | Local voice I/O (TTS/STT/clone) w/ REST+MCP | SKIP — duplicate of decided stack (OmniVoice + PhoWhisper) | — | — |
| altic-dev/FluidVoice | S | Local dictation utility | SKIP — off-product (input tool, not pipeline) | — | — |
| welcomyou/sherpa-vietnamese-asr | S | Offline VN ASR + diarization | DECIDED-REJECTED — sherpa VN engine benchmarked and quarantined 2026-07-14; do not revisit | — | — |

### 5. QA / eval

| Repo | Tier | What it is | Action | V2 phase | Prio |
|---|---|---|---|---|---|
| hexo-ai/sia | S | Framework for autonomously improving AI systems against benchmark tasks | EXTRACT — benchmark-loop shape for the eval flywheel / learning loop; VERIFY license first (unchecked) | P4–P5 | P2 |
| zhouxiaoka/autoclip (A) | A | MIT 6k★ AI highlight extraction + clipping from long video | EXTRACT — transcript-driven highlight scoring for a long→shorts repurpose lane; pairs with talking_head_autocut (which cuts silence/fillers but does not *rank* highlights) | P3–P4 | P1 |
| JayWebtech/autoshorts (A) | A | Local-first long→vertical-shorts desktop app | REFERENCE only — **no license** (all-rights-reserved), analysis allowed, vendor forbidden; autoclip covers the same ground with MIT | P4 | P3 |

### 6. Publish / analytics

| Repo | Tier | What it is | Action | V2 phase | Prio |
|---|---|---|---|---|---|
| metabase/metabase (A) | A | Open-source BI/dashboards | REFERENCE — P5 observability could embed it, but the Flask dashboard + factory_metrics already cover a solo operation; adopt only at multi-channel scale | P5 | P3 |
| yuliskov/SmartTube, Rophim-No-Ads, AdguardFilters, artlist-downloader (A) | A | Ad-blocking / media-download tools | SKIP — ToS/rights risk, off-product | — | — |

### 7. Control-plane / orchestration

| Repo | Tier | What it is | Action | V2 phase | Prio |
|---|---|---|---|---|---|
| vercel/ai | S | Vercel AI SDK — typed TS LLM/agent/streaming layer | VERIFY→likely ADOPT-as-lib — V2 control-plane is TypeScript and needs a typed multi-provider LLM layer; SEOSONA keeps its own cascade *policy* on top (parse-or-continue tiering). Check it doesn't drag Next.js assumptions into services/ | P1–P2 | P1 |
| voltagent/voltagent | S | TS AI-agent framework | REFERENCE — framework lock-in rejected; skim its typed tool/agent contracts for packages/contracts ideas only | P1 | P3 |
| langchain-ai/deepagents | S | MIT 26k★ "batteries-included agent harness" (planning, FS backend, subagents) | REFERENCE — same anti-lock-in rule; its planning/subagent decomposition is the only pattern worth a read | P2 | P3 |
| diegosouzapw/OmniRoute | S | OpenAI-compatible multi-provider LLM router w/ fallback + token compression | REFERENCE — duplicates the proven llm_engine cascade ("không hạ deterministic"); read only if the cascade is re-implemented in TS and a gateway shape is wanted | P1 | P3 |
| LMCache/LMCache | S | KV-cache layer for LLM inference | SKIP — serving-infra for self-hosted LLM fleets; V2 calls hosted/local APIs, no vLLM fleet | — | — |
| EpicStaff/EpicStaff, CanvasMind, QwenPaw | S | Visual multi-agent platforms | SKIP — third visual-workflow platform wave (dify/sim already vetted → pipeline_dag was the extraction; nothing new left) | — | — |

### 8. Knowledge / memory

| Repo | Tier | What it is | Action | V2 phase | Prio |
|---|---|---|---|---|---|
| vercel-labs/knowledge-agent-template | S | MIT file-system knowledge agent, **no vector DB**, stays current with the KB | EXTRACT — freshness/staleness re-index pattern; direct validation of the knowledge_graph (no-embeddings) approach for the V2 knowledge boundary | P2 | P1 |
| knowns-dev/knowns | S | MIT memory layer for AI-native dev (tasks/docs/specs/decisions across sessions) | EXTRACT — schema for persistent project decisions; serves the V2 *build process* (dev harness), not the video product | P0–P1 (dev) | P2 |
| allenai/olmocr | S | PDF→markdown OCR toolkit (GPU-heavy) | REFERENCE — same verdict as the MinerU/chunkr group: conditional backlog, only if infographics-from-PDF becomes a lane | P6 | P3 |
| nemocake/claude-obsidian-assistant (A) | A | Structured Obsidian vault for Claude context | REFERENCE — knowledge-graph scan (2026-07-01) already mined this family | — | — |
| braedonsaunders/codeflow (A) | A | Repo→interactive architecture graph | REFERENCE — knowledge_graph + SYSTEM_MAP already do this natively | — | — |
| upstash/context7 (A) | A | Live library-docs MCP for coding agents | REFERENCE — dev-tooling QoL; harmless to enable in the dev harness, zero product impact | dev | P3 |

### 9. Agent-harness / dev-tooling infra (see caution note — most of this category is NOT the product)

| Repo | Tier | What it is | Action | V2 phase | Prio |
|---|---|---|---|---|---|
| undertheseanlp/underthesea | S | **Apache-2.0 Vietnamese NLP toolkit** (word segmentation, POS, NER) — miscategorized as agent-harness (it added an agent layer) | **ADOPT-as-lib** — real VN word segmentation kills the highest-recurrence bug class (VN ASCII-substring collisions in keyword matching) and upgrades caption keywording + SEO tag extraction; heavier than pyvi, so wrap behind one boundary util and benchmark import cost | P2–P3 | P1 |
| nexu-io/harness-engineering-guide | S | Agent-runtime engineering guide (tools/memory/context/eval/guardrails) | EXTRACT — read once against the V2 dev-harness design; same family as x-harness/looper already absorbed | P0–P1 (dev) | P2 |
| addyosmani/agent-skills | S | Production-grade coding-agent skill library (spec/plan/build/test/review/ship) | REFERENCE — dev-discipline largely covered by LLM_CODING_DISCIPLINE + SIL; cherry-pick a review skill if a gap shows | dev | P3 |
| obra/superpowers, mattpocock/skills, NVIDIA/skills, sharpdeveye/maestro, langchain-ai/openwiki, revfactory/harness, codeaholicguy/ai-devkit | S | Coding-agent skill/method packs | REFERENCE — same verdict as spec-kit/ccbp (discipline already covered); openwiki's CI-refreshed AGENTS.md is the one idea worth noting for the V2 monorepo | dev | P3 |
| cline, opencode, herdr (AGPL), gajae-code, oh-my-openagent, claudeclaw, local-coding-agent, tmax, Qwen-AgentWorld, odysseus, Class-AI-Agent | S | Agent runtimes / terminal harnesses / RL environments | SKIP for the product — these are alternatives to Claude Code itself, not video capabilities. herdr additionally AGPL | — | — |
| samuraigpt/generative-media-skills, pilioai/skills, OfficeCLI | S | Paid-API media skill packs / office automation | SKIP — paid-API lock-in (MUAPI/Pilio) conflicts with keyless-first; OfficeCLI off-product (VERIFY only if PPTX deliverables ever become a lane) | — | — |
| YennNing/Awesome-Code-as-Agent-Harness-Papers | S | Papers list | REFERENCE — bookmark | — | P3 |

### 10. Other / own

| Repo | Tier | What it is | Action |
|---|---|---|---|
| LongLeo287/* (23 S rows: SEOSONA, SEOSONA-OS, seo-tool, SEOSONA-Video-AI, OmniClaw, aios-local, Tiem_Nuoc_Nho family, portfolios, sources-TV, CZN, basemaps, rr-bot…) | S | Own repos | N/A — not adoption targets. Two worth a VERIFY pass for reusable assets before V2 migration: **Footage-Looper** (b-roll loop assets?) and **Premiere-Pro-FX-5.0** (effect presets that could seed effect-library recipes) |
| Security/OSINT S+A (SkillSpector, strix, dockerscan, GhidraGPT…) | S/A | Security tooling | SkillSpector already noted (skill supply-chain scanning of ingested skills — keep, dev-side). Everything else SKIP for this product |
| Game/anime, geospatial, mobile, finance, misc rows | S/A | Off-domain | SKIP — browsing-history artifacts, not stack candidates |

---

## (c) Top-10 highest-leverage unharvested items

1. **diffusionstudio/lottie** (MIT, 4.8k★, active) — P1, render boundary. The V2 engine sheet already commits to "GSAP + Lottie adapters"; this is the only S-Core repo that fills the Lottie half. Take: its Claude-Code generation workflow + Lottie-JSON validation + deterministic render path → `packages/engines/lottie` adapter emitting a RenderReceipt. Test: same animation JSON → identical frames twice.
2. **undertheseanlp/underthesea** (Apache-2.0) — P1, cross-cutting VN correctness. Take: `word_tokenize` as the single VN word-boundary primitive behind one util, replacing ad-hoc `\bkw\b` regexes in keyword/domain matching (the repo's most-recurring bug class), plus NER for caption keyword highlight and SEO tag extraction. Benchmark import weight vs pyvi before committing.
3. **vercel/ai** (Apache-2.0) — P1, control-plane. V2 is a TS monorepo that must re-implement the LLM cascade; use the SDK as the typed provider transport only, keep SEOSONA's parse-or-continue tier policy above it. Take: provider abstraction + structured-output (zod) generation — zod is already the V2 contracts library. VERIFY it stays framework-neutral in a plain Node service.
4. **zhouxiaoka/autoclip** (MIT, 6k★) — P1, QA/repurpose. Take: transcript-driven highlight *scoring* (LLM ranking of candidate segments) to add a "best-moments" pass on top of talking_head_autocut's silence/filler cuts → long-form → N ranked shorts, an entire output lane the factory lacks.
5. **emilkowalski/skills** (MIT, 12.7k★) — P1, creative QA. Take: the strict-animation-review checklist and animation vocabulary → creative lint rules + eval-judge rubric lines (motion critique today is entirely LLM-improvised).
6. **lottiefiles/motion-design-skill** (MIT) — P1, creative craft. Take: timing/easing/choreography checklists and Disney-principles mapping → merge into the HyperFrames craft library beside the gsap-skills extraction; becomes the review rubric the director stage lints against.
7. **bytedance/deer-flow** (MIT) — P2, research boundary. Take: the plan→search→verify research-flow decomposition and evidence-bundle structure to harden ResearchBundle (multi-source corroboration before a stat may enter ScriptSpec — extends the traceability gate). Do not adopt the harness.
8. **vercel-labs/knowledge-agent-template** (MIT) — P2, knowledge boundary. Take: the stay-current mechanism (file-watch → staleness marking → selective re-index) for knowledge_graph V2, which today regenerates wholesale; validates the no-vector-DB stance with a working reference.
9. **hexo-ai/sia** (license unVERIFIED) — P2, eval flywheel. Take: the benchmark-task + autonomous-improvement loop shape → formalize the eval flywheel into "fixed benchmark set, agent proposes change, judge scores, keep-if-better" for the P4/P5 learning loop. Check license before any deeper read.
10. **codertapsu/multilingual-dubbed-video** (MIT) — P2, audio/localize. Take: its transcribe→translate→synthesize→align→mix stage ordering and mixing choices as a second reference implementation to cross-check dub_align + the VideoLingo time-fit extraction when the V2 Localize lane is built.

---

## (d) Category caution notes

- **AI Agent / Agent Harness (452 repos — 29% of the whole inventory; 31 S, 41 A).** This category is browsing history from building *the agent that builds the product*. It serves the dev-tooling layer, not the video product. Only four things in it matter to V2: **underthesea** (miscategorized VN NLP — product-relevant, see Top-10), **deer-flow** (research patterns), **sia** (eval-loop shape), and the verification-discipline guides (harness-engineering-guide / x-harness / looper — mostly already absorbed into LLM_CODING_DISCIPLINE + SIL). Every OpenClaw/Codex/antigravity runtime variant: SKIP.
- **Security / Pentest / OSINT / RE (49 repos, 26 risk/Q-flagged).** SKIP for this product wholesale. The single keeper is **NVIDIA/SkillSpector** (already logged) as a dev-side supply-chain scanner for third-party SKILL.md ingestion. Never run strix/GhidraGPT-class tooling from a video factory context.
- **Content / Video / Audio / Image AI (114 repos, 50 S).** Effectively mined out — 41/50 S rows already carry an ingestion entry or verdict. The remaining value is exactly the audio/motion rows in the gap list. Note 36 rows are risk-flagged (voice-clone consent, CapCut ToS, synthetic media) — the flags match decisions already taken.
- **CapCut cluster** (5 S repos): verdicts already exist (REFERENCE, P6, private format ≠ truth). Do not reopen because the rows score 91–95.
- **RAG/PDF infra** (chroma, MinerU, chunkr, olmocr, opendataloader…): standing verdict holds — a faceless video factory has no vector/PDF ingestion need; conditional backlog behind an "infographics-from-PDF" lane that doesn't exist yet.
- **Own repos** (23 S rows): inflate the S-Core count; exclude from adoption math. VERIFY Footage-Looper and Premiere-Pro-FX-5.0 for migratable assets before V2 cutover.
- **Sheet hygiene:** sync `V2_Core_Engine` tab to ADR-003/ADR-004 (whisper.cpp/WhisperX rows say ADOPT but are rejected; VieNeu row says CONDITIONAL but OmniVoice-only is decided), and consider re-categorizing underthesea out of Agent Harness so it isn't lost.
