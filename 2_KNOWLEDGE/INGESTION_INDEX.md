# SEOSONA Video — Repo Ingestion Index
# MASTER inventory (1445 repos, tiered + risk-flagged): see `2_KNOWLEDGE/REPO_INVENTORY.md`
#   (summary) + `2_KNOWLEDGE/raw_data/repo_inventory.xlsx` (full, gitignored). This file
#   tracks the video-relevant ingestion/integration status below.
# This is the SINGLE SOURCE OF TRUTH for what has/hasn't been ingested.
# RULE: Check this file BEFORE creating any new knowledge file.
# Last updated: 2026-06-24 (11-repo triage: OmniVoice wired, OpenMontage patterns ingested)
#
# NOTE (2026-06-24): 2_KNOWLEDGE/repos/ was decluttered — 63 video/TTS/audio/render
# notes kept; 731 non-video research notes removed
# (gitignored, local-only). If a link below points to a repos/*.md that's no longer
# there, the raw note is in the archive; the *integration* (code/skills) is unaffected.

---

## Batch triage — repo_inventory (1,434 repos, 2026-06-24)
From the classified inventory: 162 video-relevant → 89 already in this system (dup) →
73 new → strict filter (drop noise: photo-repair, netflix-kodi, firmware, UI widgets;
drop TTS alternatives since VieNeu is chosen) → **2 ADOPT**:
- **vinai/PhoWhisper-large** — Vietnamese ASR (BSD-3, local), drop-in upgrade over generic
  faster-whisper in the SRT step (lower WER on Vietnamese). **shortlist: ADOPT**
- **Huanshere/VideoLingo** — Apache-2.0 translate→dub + WhisperX subtitle-cut → adds the
  translation/dubbing capability the repurposer lacks, rewired to PhoWhisper + VieNeu. **shortlist: ADOPT**
- Reference only: KrillinAI (GPL-3.0 dub pipeline), VieNeu-v2-Turbo-GGUF (CPU quant — but v2),
  dantech0xff/daily-news-broadcast (text aggregator, topic-feeder only).
- Skip/duplicate: fish-speech, VibeVoice, F5/CosyVoice/OmniVoice (TTS — VieNeu already chosen),
  ebook2audiobook.

## Status Legend
- `pending` — Queued, not yet started
- `ingested` — Knowledge extracted to 2_KNOWLEDGE/repos/, integration applied
- `cleared` — Raw repo deleted, ingestion complete
- `skipped` — Tier C, logged to 5_RESEARCH/ only
- `partial` — Partially done, needs continuation

---

## Priority Group 1 — Video / TTS / Audio Pipeline

| Repo | Tier | Domain | Status | Integrated Into |
|------|------|--------|--------|----------------|
| **hyperframes** | **CORE** | **render-engine** | **ingested** | **2_KNOWLEDGE/hyperframes/ (guides+reference+catalog, 20 files) · .agents/skills/ (18 skills) · 5_FRAMEWORK/hf_engine/ (source) · 4_BRAIN/native_composer.py (render). See 2_KNOWLEDGE/hyperframes/README.md** |
| gsap-skills (greensock) | A | animation | **ingested + WIRED (deep)** | MIT. Deep-analysed → 2_KNOWLEDGE/hyperframes/gsap-skills.md (techniques + seek-render gotchas) + hyperframes-animation skill. **9 free plugins vendored (gsap 3.13.0): SplitText/MorphSVG/DrawSVG/MotionPath/ScrambleText/CustomEase/EasePack/CustomBounce/CustomWiggle** auto-loaded+registered in every render; ScrollTrigger dropped (seek render). Brand ease `"seosona"` (CustomEase) pre-registered + applied to hero titles. Verified by render. |
| openclaw-skill-infographic (tuanminhhole) | B | design-vi | **ingested** | MIT. 9_PROMPTS/design_assets/infographic_vn_presets.md (VN-safe fonts + 3 design strategies + aspect presets) → referenced by carousel_master_prompt. 9router creds added to 1_CONFIG for the optional Recraft/Flux/Ideogram image-gen backend. |
| **PhoWhisper-large (VinAI)** | A | asr-vi | **ingested + WIRED** | BSD-3, local. Vietnamese ASR. Wired as the PRIMARY engine in `2_SKILLS/srt_maker/asr_router.py` (switchable `SEOSONA_ASR`, falls back to faster-whisper → openai-whisper). Set `SEOSONA_PHOWHISPER_MODEL` to a CT2 PhoWhisper repo to activate; until then the router auto-uses faster-whisper. Lower WER on Vietnamese for subtitles + repurposer hooks. |
| **VideoLingo (Huanshere)** | A | subtitle/dub | **ingested + WIRED (full)** | Apache-2.0. (1) WhisperX single-line subtitle cutting = `group_words_to_segments`. (2) **Full translate→dub localizer built**: `1_AGENTS/repurposer_agent/localizer.py` `localize_video()` = ASR router (PhoWhisper) → translate router (LLM primary, Google backup, keeps EN tech terms) → VieNeu brand-voice dub (time-fit via ffmpeg atempo) → translated .srt + aligned dubbed .wav. New switchable `2_SKILLS/translator/`. |
| F5-TTS | A | voice-clone | partial | 2_SKILLS/voice_cloner/ [needs full distillation] |
| VieNeu-TTS | A | tts-vi | partial | 2_SKILLS/voice_cloner/voice_router.py (via 4_BRAIN/native_composer.py) [needs SOP update] |
| VideoCaptioner | A | subtitle | partial | 2_SKILLS/srt_maker/ [needs full distillation] |
| MoneyPrinterTurbo | A | full-pipeline | quarantined | removed (not wired; reference note only) |
| MoneyPrinterV2 | A | full-pipeline | cleared | 2_KNOWLEDGE/repos/MoneyPrinterV2.md |
| OmniVoice (k2-fsa) | A | tts-vi-clone | superseded | 2_KNOWLEDGE/repos/OmniVoice.md (knowledge kept; engine NOT wired — VieNeu is the single TTS source of truth via voice_router.py. The old omnivoice/fish branches were removed.) |
| omnivoice-vi (dataset) | A | tts-vi-voices | ingested | 2_KNOWLEDGE/repos/omnivoice-vi-dataset.md (6 female VN voice .pt profiles + dubbing) |
| OpenMontage | B | agentic-video-OS | ingested | 2_KNOWLEDGE/repos/OpenMontage.md (AGPLv3 — patterns/ideas only: provider scoring, governance, pipeline taxonomy) |
| WeClone | A | voice-clone | cleared | 2_KNOWLEDGE/repos/WeClone.md |
| story2audio | A | tts+subtitle | quarantined | removed (not wired; reference note only) |
| autoclip | A | video-clip | cleared | 2_KNOWLEDGE/repos/autoclip.md |
| skill-autoshorts | A | shorts-workflow | cleared | 2_KNOWLEDGE/repos/skill-autoshorts.md |
| pipecat | A | audio-pipeline | cleared | 2_KNOWLEDGE/repos/pipecat.md |
| TTS-Audio-Suite | A | audio | pending | — |
| BetterBox-TTS | A | tts | pending | — |
| html-video | A | html-to-video | pending | — |

---

## Priority Group 2 — Scraping / Research / SEO

| Repo | Tier | Domain | Status | Integrated Into |
|------|------|--------|--------|----------------|
| Scrapling | A | scraper | cleared | 2_KNOWLEDGE/repos/Scrapling.md |
| claude-seo | A | seo | partial | 1_AGENTS/seo_writer_agent/ [needs full distillation] |
| firecrawl | A | scraper | cleared | 2_KNOWLEDGE/repos/firecrawl.md |
| browser-use | A | browser-auto | cleared | 2_KNOWLEDGE/repos/browser-use.md |
| EasySpider | B | visual-scraper | cleared | 2_KNOWLEDGE/repos/EasySpider.md |
| deer-flow | A | research-agent | cleared | 2_KNOWLEDGE/repos/deer-flow.md |
| langfuse | A | llmops | cleared | 2_KNOWLEDGE/repos/langfuse.md |
| LightRAG | A | rag | cleared | 2_KNOWLEDGE/repos/LightRAG.md |
| seo-tool | B | seo | pending | — |
| seo-geo-claude-skills | B | seo | pending | — |
| social-media-scraping-apis | B | scraper | pending | — |
| ultimate-web-scraper | B | scraper | pending | — |

---

## Priority Group 3 — Agent / Workflow Frameworks

| Repo | Tier | Domain | Status | Integrated Into |
|------|------|--------|--------|----------------|
| yutu | A | youtube-cli | partial | 1_AGENTS/publisher_agent/ [needs full distillation] |
| AgentFlow | A | agent-orchestr | cleared | 2_KNOWLEDGE/repos/AgentFlow.md |
| Qwen-Agent | A | agent-framework | cleared | 2_KNOWLEDGE/repos/Qwen-Agent.md |
| agentscope | A | multi-agent | cleared | 2_KNOWLEDGE/repos/agentscope.md |
| dify | A | llm-workflow | cleared | 2_KNOWLEDGE/repos/dify.md |
| ChatDev | B | multi-agent | cleared | 2_KNOWLEDGE/repos/ChatDev.md |
| pipecat | A | voice-agent | cleared | 2_KNOWLEDGE/repos/pipecat.md |
| deepagents | B | agent | cleared | 2_KNOWLEDGE/repos/deepagents.md |
| agency-agents | B | agent | cleared | 2_KNOWLEDGE/repos/agency-agents.md |
| open-multi-agent | B | multi-agent | cleared | 2_KNOWLEDGE/repos/open-multi-agent.md |
| agentlytics | B | agent-analytics | cleared | 2_KNOWLEDGE/repos/agentlytics.md |
| BMAD-METHOD | C | agent-workflow | cleared | 2_KNOWLEDGE/repos/BMAD-METHOD.md |

---

## Priority Group 4 — UI / Frontend / Design

| Repo | Tier | Domain | Status | Integrated Into |
|------|------|--------|--------|----------------|
| magicui | B | ui | cleared | 2_KNOWLEDGE/repos/magicui.md |
| prebuiltui | B | ui | cleared | 2_KNOWLEDGE/repos/prebuiltui.md |
| tailwind-animations | B | ui | skipped | empty repo |
| open-design | B | design | cleared | 2_KNOWLEDGE/repos/open-design.md |
| typeui | B | ui | cleared | 2_KNOWLEDGE/repos/typeui.md |

---

## Priority Group 5 — Knowledge / Skills Collections

| Repo | Tier | Domain | Status | Integrated Into |
|------|------|--------|--------|----------------|
| agent-skills | B | skills-collection | cleared | 2_KNOWLEDGE/repos/agent-skills.md |
| awesome-agent-skills | B | skills-collection | cleared | 2_KNOWLEDGE/repos/awesome-agent-skills.md |
| awesome-claude-skills | B | skills-collection | cleared | 2_KNOWLEDGE/repos/awesome-claude-skills.md |
| ai-marketing-skills | B | marketing | cleared | 2_KNOWLEDGE/repos/ai-marketing-skills.md |
| marketingskills | B | marketing | cleared | 2_KNOWLEDGE/repos/marketingskills.md |
| 500-AI-Agents-Projects | B | reference | cleared | 2_KNOWLEDGE/repos/500-ai-agents-projects.md |
| awesome-llm-apps | B | reference | cleared | 2_KNOWLEDGE/repos/awesome-llm-apps.md |
| LLM-engineer-handbook | B | reference | cleared | 2_KNOWLEDGE/repos/llm-engineer-handbook.md |
| Awesome-Prompt-Engineering | C | reference | skipped | 5_RESEARCH/ |

---

## Priority Group 6 — General AI / Routing / Tools

| Repo | Tier | Domain | Status | Integrated Into |
|------|------|--------|--------|----------------|

| 9router | B | llm-routing | cleared | 2_KNOWLEDGE/repos/9router.md |
| AI-Animation-Skill | A | html-animation | cleared | 2_KNOWLEDGE/repos/AI-Animation-Skill.md |
| Antigravity-Deck | B | agent-ui | cleared | 2_KNOWLEDGE/repos/Antigravity-Deck.md |
| Antigravity-Manager | B | llm-proxy | cleared | 2_KNOWLEDGE/repos/Antigravity-Manager.md |
| Antigravity-Skills-Chronicle | B | agent-skills | cleared | 2_KNOWLEDGE/repos/Antigravity-Skills-Chronicle.md |
| AntigravityManager | B | llm-proxy | cleared | 2_KNOWLEDGE/repos/AntigravityManager.md |
| AstrBot | B | agent | cleared | 2_KNOWLEDGE/repos/AstrBot.md |
| Atomic-Chat | B | llm-local | cleared | 2_KNOWLEDGE/repos/Atomic-Chat.md |
| Auto-Claude | B | agent-coding | cleared | 2_KNOWLEDGE/repos/Auto-Claude.md |
| AutoCLI | B | scraper | cleared | 2_KNOWLEDGE/repos/AutoCLI.md |
| Awesome-Prompt-Engineering | B | reference | cleared | 2_KNOWLEDGE/repos/Awesome-Prompt-Engineering.md |
| BetterBox-TTS | A | tts-vi | cleared | 2_KNOWLEDGE/repos/BetterBox-TTS.md |
| Class-AI-Agent | B | agent-skills | cleared | 2_KNOWLEDGE/repos/Class-AI-Agent.md |
| Claude-Code-Game-Studios | B | agent-workflow | cleared | 2_KNOWLEDGE/repos/Claude-Code-Game-Studios.md |
| Claude-code-skill-manager | B | agent-skills | cleared | 2_KNOWLEDGE/repos/Claude-code-skill-manager.md |
| Claw-CLI | B | agent-cli | cleared | 2_KNOWLEDGE/repos/Claw-CLI.md |
| ClawRouter | B | llm-router | cleared | 2_KNOWLEDGE/repos/ClawRouter.md |
| ClawWork | B | agent-workflow | cleared | 2_KNOWLEDGE/repos/ClawWork.md |
| ContribAI | B | agent-coding | cleared | 2_KNOWLEDGE/repos/ContribAI.md |
| DataFlow | B | llm-data | cleared | 2_KNOWLEDGE/repos/DataFlow.md |
| Dayflow | B | productivity-tool | cleared | 2_KNOWLEDGE/repos/Dayflow.md |
| DeepTutor | B | agent | cleared | 2_KNOWLEDGE/repos/DeepTutor.md |
| Dich-Viet | B | translation | cleared | 2_KNOWLEDGE/repos/Dich-Viet.md |
| Druckenmiller | B | agent-skills | cleared | 2_KNOWLEDGE/repos/Druckenmiller.md |
| F5-TTS | A | tts | cleared | 2_KNOWLEDGE/repos/F5-TTS.md |
| HashIndex | B | rag-indexing | cleared | 2_KNOWLEDGE/repos/HashIndex.md |
| LLMs-from-scratch | B | reference | cleared | 2_KNOWLEDGE/repos/LLMs-from-scratch.md |
| LongLeo287 | A | user-profile | cleared | 2_KNOWLEDGE/repos/LongLeo287.md |
| MaxKB | B | agent-platform | cleared | 2_KNOWLEDGE/repos/MaxKB.md |
| Memento-Skills | B | agent-skills | cleared | 2_KNOWLEDGE/repos/Memento-Skills.md |
| Molten-Agent-Kit | B | agent-social | cleared | 2_KNOWLEDGE/repos/Molten-Agent-Kit.md |
| My-Brain-Is-Full-Crew | B | agent-workflow | cleared | 2_KNOWLEDGE/repos/My-Brain-Is-Full-Crew.md |
| NemoClaw | B | agent-security | cleared | 2_KNOWLEDGE/repos/NemoClaw.md |
| NexusRAG | B | rag | cleared | 2_KNOWLEDGE/repos/NexusRAG.md |
| OmniClaw | A | system-core | cleared | 2_KNOWLEDGE/repos/OmniClaw.md |
| Open-Higgsfield-AI | A | video-ai | cleared | 2_KNOWLEDGE/repos/Open-Higgsfield-AI.md |
| nightingale | A | video-monitoring | cleared | 2_KNOWLEDGE/repos/nightingale.md |
| loop-engineering | A | agent-workflow | cleared | 2_KNOWLEDGE/repos/loop-engineering.md |
| supergraph | A | llm-router | cleared | 2_KNOWLEDGE/repos/supergraph.md |
| OpenClaw-bot-review | B | agent-ui | cleared | 2_KNOWLEDGE/repos/OpenClaw-bot-review.md |
| OpenSpace | B | agent-optimization | cleared | 2_KNOWLEDGE/repos/OpenSpace.md |
---

## Tier C — Reference Only (Log URL, No Clone Needed)

| Repo | Reason | Logged To |
|------|--------|-----------|
| AdguardFilters | Ad blocking, not relevant | 5_RESEARCH/ |
| FBI_Watchdog | Security tool | 5_RESEARCH/ |
| DuckPentest-Project | Pentest, not relevant | 5_RESEARCH/ |
| VMkatz | Security tool | 5_RESEARCH/ |
| Netflix_ATV_L3_DRM_Uncertified_Mod | DRM bypass | 5_RESEARCH/ |
| RSTGameTranslation | Game translation | 5_RESEARCH/ |
| FinRL | Trading RL | 5_RESEARCH/ |
| AI-Trader | Trading AI | 5_RESEARCH/ |
| TradingAgents | Trading | 5_RESEARCH/ |
| Network-labs | Network tools | 5_RESEARCH/ |
| hackingBuddyGPT | Security | 5_RESEARCH/ |
| identYwaf | WAF detection | 5_RESEARCH/ |
| katana | Web crawler/security | 5_RESEARCH/ |
| PentestOPS | Pentest | 5_RESEARCH/ |
| trivy | Security scanner | 5_RESEARCH/ |
| checkov | IaC security | 5_RESEARCH/ |
| uber-apk-signer | Android signing | 5_RESEARCH/ |
| MBR_xbebenkMod | System mod | 5_RESEARCH/ |
| zeroleaks | Security | 5_RESEARCH/ |
| git-secrets | Security | 5_RESEARCH/ |
| GitHacker | Security | 5_RESEARCH/ |

| AI-Agent-TFT | Game playing AI (TFT), not relevant | 5_RESEARCH/ |
| AI-Project-Gallery | List of data science / ML projects | 5_RESEARCH/ |
| AI-Trader | Trading bot/platform | 5_RESEARCH/ |
| API-mega-list | List of generic APIs | 5_RESEARCH/ |
| AdaptixC2 | Security / Pentesting C2 framework | 5_RESEARCH/ |
| AutoResearchClaw | Academic paper generation AI, not relevant. | 5_RESEARCH/ |
| Class_CI-CD | Course material for CI/CD. | 5_RESEARCH/ |
| Class_Docker_Systems | Course material for Docker. | 5_RESEARCH/ |
| Class_NodeJs_Systems | Course material for NodeJS. | 5_RESEARCH/ |
| ClawLibrary | 2D pixel game UI for agent, out of scope. | 5_RESEARCH/ |
| Dopamine | iOS jailbreak tool, not relevant. | 5_RESEARCH/ |
| DuckPentest-Project | AI penetration testing agent. | 5_RESEARCH/ |
| EF-Tools | No README found, skipping. | 5_RESEARCH/ |
| EmbeddingGemma.NET | .NET bindings for EmbeddingGemma. | 5_RESEARCH/ |
| FBI_Watchdog | Domain seizure detection tool. | 5_RESEARCH/ |
| FinRL | Financial Reinforcement Learning. | 5_RESEARCH/ |
| Font-Awesome | Icon library, standard tool. | 5_RESEARCH/ |
| Git-Secrets | Security tool for scanning secrets. | 5_RESEARCH/ |
| GitHacker | Security pentest tool for .git. | 5_RESEARCH/ |
| GitNexus | Unclear relevance, appears crypto related. | 5_RESEARCH/ |
| Kronos | Finance specific LLM. | 5_RESEARCH/ |
| MBR_xbebenkMod | Clash of Clans bot. | 5_RESEARCH/ |
| Machine-Learning-Projects | Reference learning projects. | 5_RESEARCH/ |
| MiroFish | Universal Swarm Intelligence Engine. | 5_RESEARCH/ |
| MovieRecapTool-Landing | Landing page website code. | 5_RESEARCH/ |
| MyBot | Clash of clans bot. | 5_RESEARCH/ |
| Netflix_ATV_L3_DRM_Uncertified_Mod | Android APK mod. | 5_RESEARCH/ |
| Network-labs | Networking labs. | 5_RESEARCH/ |
| NtWarden | Windows Analysis toolkit. | 5_RESEARCH/ |
| OpenSandbox | Sandbox orchestration. | 5_RESEARCH/ |
| OpenSpec | Spec framework. | 5_RESEARCH/ |
---

## Stats

- Total repos in raw/: 294 (remaining to process)
- Ingested (full): 74
- Partial (needs redo): 6
- Pending: 294
- Tier C / Skipped: 62
- Cleared: 106
