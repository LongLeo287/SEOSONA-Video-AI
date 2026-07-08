# Repo Inventory — Master (classified + tiered)

> **Source of truth** for ingested/curated repos. Master binary: `2_KNOWLEDGE/raw_data/repo_inventory.xlsx`
> (gitignored). This markdown is the tracked summary. Regenerate after updating the xlsx.

- Total unique items: **1445**  · Top-priority: **194**  · Risk-flagged: **74**
- Synced: 2026-06-27 from `repo_inventory_classified_tiered_updated(26).xlsx`

## Tier dictionary

| Tier | Meaning | Rule of thumb | Default action |
|---|---|---|---|
| S - Core | Core/strategic asset, your own repo, or heavily viewed | Own repo, very high Visits, or a direct match to the AI/SEO/video/agent stack | Bring into the main workspace, read the README, plan integration |
| A - High | High value, evaluate early | Visits >= 10 or high score by category + interest | Shortlist and test quickly |
| B - Useful | Useful reference | Visits 4-9 or a related category | Keep the tag; clone when needed |
| C - Backlog | Explore later | Low Visits, need still unclear | Not a priority |
| D - Dead/Low | Broken/unclear URL / low value | Page not found or context too thin | Verify, then archive |
| Q - Quarantine | Legal/safety/policy risk | Clearly bypass/crack/cheat/credential/leak/offensive | Do not run; only legal/safety review or delete |
| Category | What it contains | Examples of keywords | Use |
| AI Agent / Agent Harness | Group of repos/models by primary use case | agent, agents, openclaw, claw, claude code, codex, opencode, antigravity | Used for quick filtering in the Repos_Classified sheet |
| Agent Skills / Prompt Ops | Group of repos/models by primary use case | skill, skills, prompt, system prompt, claude-plugins, templates, bmad, method | Used for quick filtering in the Repos_Classified sheet |
| LLM Infra / Inference / Routing | Group of repos/models by primary use case | llm, model, inference, vllm, ollama, mlx, nexa, router | Used for quick filtering in the Repos_Classified sheet |
| RAG / Knowledge / Memory / Search | Group of repos/models by primary use case | rag, memory, mem, notebooklm, knowledge, index, document, graph | Used for quick filtering in the Repos_Classified sheet |
| Security / Pentest / OSINT / RE | Group of repos/models by primary use case | security, pentest, osint, cve, exploit, vulnerability, vuln, hash | Used for quick filtering in the Repos_Classified sheet |
| Web Scraping / Browser Automation | Group of repos/models by primary use case | scrap, crawl, browser, crawler, spider, shodan, download, yt-dlp | Used for quick filtering in the Repos_Classified sheet |
| SEO / Marketing / Affiliate / Growth | Group of repos/models by primary use case | seo, affiliate, marketing, ads, keyword, rank, content, growth | Used for quick filtering in the Repos_Classified sheet |
| Content / Video / Audio / Image AI | Group of repos/models by primary use case | video, subtitle, caption, tts, voice, audio, whisper, sovits | Used for quick filtering in the Repos_Classified sheet |
| Frontend / UI / Design / Components | Group of repos/models by primary use case | react, vue, next, nuxt, ui, design, component, portfolio | Used for quick filtering in the Repos_Classified sheet |
| DevOps / Cloud / Database / Backup | Group of repos/models by primary use case | devops, deploy, kubernetes, docker, cloud, backup, database, postgres | Used for quick filtering in the Repos_Classified sheet |
| Game / Anime / Arknights / Entertainment | Group of repos/models by primary use case | arknights, endfield, anime, gacha, game, launcher, mihoyo, netflix | Used for quick filtering in the Repos_Classified sheet |
| Finance / Trading / Crypto | Group of repos/models by primary use case | trading, finance, financial, crypto, quant, usdc, solana, payment | Used for quick filtering in the Repos_Classified sheet |
| Education / Awesome / Reference | Group of repos/models by primary use case | awesome, course, learn, books, guide, tutorial, handbook, compendium | Used for quick filtering in the Repos_Classified sheet |
| Mobile / Desktop / OS Utility | Group of repos/models by primary use case | windows, macos, ios, android, desktop, extension, vscode, chrome | Used for quick filtering in the Repos_Classified sheet |
| Geospatial / Maps | Group of repos/models by primary use case | map, geo, basemap, geospatial, geojson, gis, cartographic | Used for quick filtering in the Repos_Classified sheet |
| Data / Analytics / Visualization | Group of repos/models by primary use case | data, analytics, dashboard, chart, visualization, table, sql, etl | Used for quick filtering in the Repos_Classified sheet |

## Category summary

| Category | Repo Count | S - Core | A - High | Risk/Q |
|---|---|---|---|---|
| AI Agent / Agent Harness | 451 | 10 | 42 | 12 |
| Misc / Unclear | 174 | 5 | 8 | 7 |
| LLM Infra / Inference / Routing | 141 | 2 | 9 | 3 |
| Frontend / UI / Design / Components | 119 | 7 | 3 | 2 |
| RAG / Knowledge / Memory / Search | 104 | 7 | 6 | 6 |
| Agent Skills / Prompt Ops | 75 | 7 | 15 | 4 |
| Content / Video / Audio / Image AI | 70 | 13 | 12 | 7 |
| DevOps / Cloud / Database / Backup | 63 | 0 | 6 | 0 |
| Web Scraping / Browser Automation | 49 | 2 | 7 | 3 |
| Mobile / Desktop / OS Utility | 43 | 1 | 4 | 1 |
| Security / Pentest / OSINT / RE | 43 | 1 | 1 | 20 |
| SEO / Marketing / Affiliate / Growth | 33 | 4 | 6 | 2 |
| Game / Anime / Arknights / Entertainment | 32 | 2 | 3 | 7 |
| Education / Awesome / Reference | 26 | 1 | 4 | 0 |
| Data / Analytics / Visualization | 11 | 1 | 2 | 0 |
| Geospatial / Maps | 6 | 1 | 2 | 0 |
| Finance / Trading / Crypto | 5 | 0 | 0 | 0 |

## Top priority (showing 40 of 194)

| Name | Kind | Tier | URL |
|---|---|---|---|
| LongLeo287/OmniClaw | repo | S - Core | https://github.com/LongLeo287/OmniClaw |
| LongLeo287/aios-local | repo | S - Core | https://github.com/LongLeo287/aios-local |
| LongLeo287/seo-tool | repo | S - Core | https://github.com/LongLeo287/seo-tool |
| LongLeo287/SEOSONA | repo | S - Core | https://github.com/LongLeo287/SEOSONA |
| LongLeo287/SEOSONA-OS | repo | S - Core | https://github.com/LongLeo287/SEOSONA-OS |
| chroma-core/chroma | repo | S - Core | https://github.com/chroma-core/chroma |
| vercel/ai | repo | S - Core | https://github.com/vercel/ai |
| microsoft/playwright-mcp | repo | S - Core | https://github.com/microsoft/playwright-mcp |
| AIDC-AI/Pixelle-Video | repo | S - Core | https://github.com/AIDC-AI/Pixelle-Video |
| ArcReel/ArcReel | repo | S - Core | https://github.com/ArcReel/ArcReel |
| calesthio/OpenMontage | repo | S - Core | https://github.com/calesthio/OpenMontage |
| voltagent/voltagent | repo | S - Core | https://github.com/voltagent/voltagent |
| browser-use/browser-use | repo | S - Core | https://github.com/browser-use/browser-use |
| LMCache/LMCache | repo | S - Core | https://github.com/LMCache/LMCache |
| nexu-io/open-design | repo | S - Core | https://github.com/nexu-io/open-design |
| nousresearch/hermes-agent | repo | S - Core | https://github.com/nousresearch/hermes-agent |
| renezander030/capcut-cli | repo | S - Core | https://github.com/renezander030/capcut-cli |
| DeusData/codebase-memory-mcp | repo | S - Core | https://github.com/DeusData/codebase-memory-mcp |
| EverMind-AI/EverOS | repo | S - Core | https://github.com/EverMind-AI/EverOS |
| nexu-io/harness-engineering-guide | repo | S - Core | https://github.com/nexu-io/harness-engineering-guide |
| NVIDIA/skills | repo | S - Core | https://github.com/NVIDIA/skills |
| NVIDIA/SkillSpector | repo | S - Core | https://github.com/NVIDIA/SkillSpector |
| OpenCut-app/OpenCut | repo | S - Core | https://github.com/OpenCut-app/OpenCut |
| palmier-io/palmier-pro | repo | S - Core | https://github.com/palmier-io/palmier-pro |
| QwenLM/Qwen-AgentWorld | repo | S - Core | https://github.com/QwenLM/Qwen-AgentWorld |
| StarTrail-org/PixelRAG | repo | S - Core | https://github.com/StarTrail-org/PixelRAG |
| SWivid/F5-TTS | repo | S - Core | https://github.com/SWivid/F5-TTS |
| NVIDIA-AI-Blueprints/video-search-and-summarization | repo | S - Core | https://github.com/NVIDIA-AI-Blueprints/video-search-and-summarization |
| cytostack/openwolf | repo | S - Core | https://github.com/cytostack/openwolf |
| EpicStaff/EpicStaff | repo | S - Core | https://github.com/EpicStaff/EpicStaff |
| headroomlabs-ai/headroom | repo | S - Core | https://github.com/headroomlabs-ai/headroom |
| jamiepine/voicebox | repo | S - Core | https://github.com/jamiepine/voicebox |
| ksimback/looper | repo | S - Core | https://github.com/ksimback/looper |
| LongLeo287/Portfolio_LongLeo | repo | S - Core | https://github.com/LongLeo287/Portfolio_LongLeo |
| LongLeo287/Tiem_Nuoc_Nho | repo | S - Core | https://github.com/LongLeo287/Tiem_Nuoc_Nho |
| LongLeo287/Tiem_Nuoc_Nho_v5 | repo | S - Core | https://github.com/LongLeo287/Tiem_Nuoc_Nho_v5 |
| mattpocock/skills | repo | S - Core | https://github.com/mattpocock/skills |
| NVIDIA/NemoClaw | repo | S - Core | https://github.com/NVIDIA/NemoClaw |
| NVIDIA/OpenShell | repo | S - Core | https://github.com/NVIDIA/OpenShell |
| yifanfeng97/Hyper-Extract | repo | S - Core | https://github.com/yifanfeng97/Hyper-Extract |

## Risk flags (74)

| Name | Tier | Risk | Recommended action |
|---|---|---|---|
| k2-fsa/OmniVoice | A - High | Voice cloning consent/license review | Add to the shortlist; evaluate applicability within 1-2 work sessions. |
| amruth-sn/kong | B - Useful | Exploit/CVE/offensive | Keep as a reference; tag the use case clearly, clone only when needed. |
| mrexodia/ida-pro-mcp | B - Useful | Exploit/CVE/offensive | Keep as a reference; tag the use case clearly, clone only when needed. |
| AngeloD2022/jsxer | B - Useful | Exploit/CVE/offensive | Keep as a reference; tag the use case clearly, clone only when needed. |
| advisories/GHSA-p9ff-h696-f583 | B - Useful | Exploit/CVE/offensive | Keep as a reference; tag the use case clearly, clone only when needed. |
| 0xBlackash/CVE-2026-21643 | B - Useful | Exploit/CVE/offensive | Keep as a reference; tag the use case clearly, clone only when needed. |
| Adaptix-Framework/AdaptixC2 | B - Useful | Exploit/CVE/offensive | Keep as a reference; tag the use case clearly, clone only when needed. |
| HackUnderway/cerberus | B - Useful | Exploit/CVE/offensive | Keep as a reference; tag the use case clearly, clone only when needed. |
| skylot/jadx | B - Useful | Exploit/CVE/offensive | Keep as a reference; tag the use case clearly, clone only when needed. |
| WangYihang/GitHacker | B - Useful | Exploit/CVE/offensive | Keep as a reference; tag the use case clearly, clone only when needed. |
| jamiepine/voicebox | S - Core | Voice cloning consent/license review | Prioritize reading the README, star/fork/clone if needed, attach to the main workspace. |
| elementalsouls/Claude-BugHunter | C - Backlog | Exploit/CVE/offensive | Leave in the backlog; return only when a matching project comes up. |
| gadievron/raptor | C - Backlog | Exploit/CVE/offensive | Leave in the backlog; return only when a matching project comes up. |
| P4nda0s/reverse-skills | C - Backlog | Exploit/CVE/offensive | Leave in the backlog; return only when a matching project comes up. |
| staticpayload/oh-my-codex | C - Backlog | Exploit/CVE/offensive | Leave in the backlog; return only when a matching project comes up. |
| zhaoxuya520/reverse-skill | Q - Quarantine | Reverse engineering/offensive security review | Do not auto-clone/run. Keep only for auditing; run a legal/safety review before use. |
| JesseCHale/HaleHound-CYD | C - Backlog | Exploit/CVE/offensive | Leave in the backlog; return only when a matching project comes up. |
| OpenAttackDefenseTools/tulip | C - Backlog | Exploit/CVE/offensive | Leave in the backlog; return only when a matching project comes up. |
| Vuemony/vue-after-free | C - Backlog | Exploit/CVE/offensive | Leave in the backlog; return only when a matching project comes up. |
| LongLeo287/JerrySFX | D - Dead/Low | Broken/Page not found | Re-verify the URL; if it cannot be recovered, archive it from the main list. |
| JuliusBrussee/caveman-claude | D - Dead/Low | Broken/Page not found | Re-verify the URL; if it cannot be recovered, archive it from the main list. |
| claudekit/claudekit-marketing | D - Dead/Low | Broken/Page not found | Re-verify the URL; if it cannot be recovered, archive it from the main list. |
| carsalgut/reverse-skills | D - Dead/Low | Broken/Page not found | Re-verify the URL; if it cannot be recovered, archive it from the main list. |
| dotanminh/nextjs-supabase-wms | D - Dead/Low | Broken/Page not found | Re-verify the URL; if it cannot be recovered, archive it from the main list. |
| COMMUNITY-SCRIPTS/PROXMOZVE | D - Dead/Low | Broken/Page not found | Re-verify the URL; if it cannot be recovered, archive it from the main list. |
| LongLeo287/bypass-rophim-vip | Q - Quarantine | Piracy/Bypass | Do not clone/run. Keep only for auditing; delete or run a legal/safety review. |
| LongLeo287/rophim-vip-2025 | Q - Quarantine | Piracy/Bypass | Do not clone/run. Keep only for auditing; delete or run a legal/safety review. |
| LongLeo287/RR_Crack-Extension | Q - Quarantine | Piracy/Bypass | Do not clone/run. Keep only for auditing; delete or run a legal/safety review. |
| AykutSarac/jsoncrack.com | Q - Quarantine | Piracy/Bypass | Do not clone/run. Keep only for auditing; delete or run a legal/safety review. |
| nghyane/ampcode-connector | Q - Quarantine | Credential/secret risk | Do not clone/run. Keep only for auditing; delete or run a legal/safety review. |

_(+44 more in the xlsx)_

## Resource links

| Name | Kind | Tier | URL |
|---|---|---|---|
| omnivoice-vi | dataset | Resource | https://huggingface.co/datasets/STBack23/omnivoice-vi |
| skills.sh | directory | A - High | https://www.skills.sh/ |
| GSAP docs v3 | documentation | A - High | https://gsap.com/docs/v3/ |
| CyberTools4U GitHub Tools | directory | B - Useful | https://cybertools4u.com/github-tools |
