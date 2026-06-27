# Repo Inventory — Master (classified + tiered)

> **Source of truth** for ingested/curated repos. Master binary: `2_KNOWLEDGE/raw_data/repo_inventory.xlsx`
> (gitignored). This markdown is the tracked summary. Regenerate after updating the xlsx.

- Total unique items: **1445**  · Top-priority: **194**  · Risk-flagged: **74**
- Synced: 2026-06-27 from `repo_inventory_classified_tiered_updated(26).xlsx`

## Tier dictionary

| Tier | Meaning | Rule of thumb | Default action |
|---|---|---|---|
| S - Core | Tài sản lõi/chiến lược hoặc repo của bạn/được xem nhiều | Own repo, Visits rất cao, hoặc khớp trực tiếp AI/SEO/video/agent stack | Đưa vào workspace chính, đọc README, lập kế hoạch tích hợp |
| A - High | Giá trị cao, nên đánh giá sớm | Visits >= 10 hoặc score cao theo category + interest | Shortlist và test nhanh |
| B - Useful | Reference hữu ích | Visits 4-9 hoặc category có liên quan | Giữ tag; clone khi cần |
| C - Backlog | Khám phá sau | Visits thấp, chưa rõ nhu cầu | Không ưu tiên |
| D - Dead/Low | URL lỗi/không rõ/ít giá trị | Page not found hoặc context quá mỏng | Xác minh, sau đó archive |
| Q - Quarantine | Rủi ro pháp lý/an toàn/chính sách | Bypass/crack/cheat/credential/leak/offensive rõ ràng | Không chạy; chỉ review pháp lý/an toàn hoặc xóa |
| Category | What it contains | Examples of keywords | Use |
| AI Agent / Agent Harness | Nhóm repo/model theo use case chính | agent, agents, openclaw, claw, claude code, codex, opencode, antigravity | Dùng để lọc nhanh trong sheet Repos_Classified |
| Agent Skills / Prompt Ops | Nhóm repo/model theo use case chính | skill, skills, prompt, system prompt, claude-plugins, templates, bmad, method | Dùng để lọc nhanh trong sheet Repos_Classified |
| LLM Infra / Inference / Routing | Nhóm repo/model theo use case chính | llm, model, inference, vllm, ollama, mlx, nexa, router | Dùng để lọc nhanh trong sheet Repos_Classified |
| RAG / Knowledge / Memory / Search | Nhóm repo/model theo use case chính | rag, memory, mem, notebooklm, knowledge, index, document, graph | Dùng để lọc nhanh trong sheet Repos_Classified |
| Security / Pentest / OSINT / RE | Nhóm repo/model theo use case chính | security, pentest, osint, cve, exploit, vulnerability, vuln, hash | Dùng để lọc nhanh trong sheet Repos_Classified |
| Web Scraping / Browser Automation | Nhóm repo/model theo use case chính | scrap, crawl, browser, crawler, spider, shodan, download, yt-dlp | Dùng để lọc nhanh trong sheet Repos_Classified |
| SEO / Marketing / Affiliate / Growth | Nhóm repo/model theo use case chính | seo, affiliate, marketing, ads, keyword, rank, content, growth | Dùng để lọc nhanh trong sheet Repos_Classified |
| Content / Video / Audio / Image AI | Nhóm repo/model theo use case chính | video, subtitle, caption, tts, voice, audio, whisper, sovits | Dùng để lọc nhanh trong sheet Repos_Classified |
| Frontend / UI / Design / Components | Nhóm repo/model theo use case chính | react, vue, next, nuxt, ui, design, component, portfolio | Dùng để lọc nhanh trong sheet Repos_Classified |
| DevOps / Cloud / Database / Backup | Nhóm repo/model theo use case chính | devops, deploy, kubernetes, docker, cloud, backup, database, postgres | Dùng để lọc nhanh trong sheet Repos_Classified |
| Game / Anime / Arknights / Entertainment | Nhóm repo/model theo use case chính | arknights, endfield, anime, gacha, game, launcher, mihoyo, netflix | Dùng để lọc nhanh trong sheet Repos_Classified |
| Finance / Trading / Crypto | Nhóm repo/model theo use case chính | trading, finance, financial, crypto, quant, usdc, solana, payment | Dùng để lọc nhanh trong sheet Repos_Classified |
| Education / Awesome / Reference | Nhóm repo/model theo use case chính | awesome, course, learn, books, guide, tutorial, handbook, compendium | Dùng để lọc nhanh trong sheet Repos_Classified |
| Mobile / Desktop / OS Utility | Nhóm repo/model theo use case chính | windows, macos, ios, android, desktop, extension, vscode, chrome | Dùng để lọc nhanh trong sheet Repos_Classified |
| Geospatial / Maps | Nhóm repo/model theo use case chính | map, geo, basemap, geospatial, geojson, gis, cartographic | Dùng để lọc nhanh trong sheet Repos_Classified |
| Data / Analytics / Visualization | Nhóm repo/model theo use case chính | data, analytics, dashboard, chart, visualization, table, sql, etl | Dùng để lọc nhanh trong sheet Repos_Classified |

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
| k2-fsa/OmniVoice | A - High | Voice cloning consent/license review | Đưa vào shortlist; đánh giá khả năng áp dụng trong 1-2 phiên làm việc. |
| amruth-sn/kong | B - Useful | Exploit/CVE/offensive | Giữ làm reference; tag rõ use case, chỉ clone khi cần. |
| mrexodia/ida-pro-mcp | B - Useful | Exploit/CVE/offensive | Giữ làm reference; tag rõ use case, chỉ clone khi cần. |
| AngeloD2022/jsxer | B - Useful | Exploit/CVE/offensive | Giữ làm reference; tag rõ use case, chỉ clone khi cần. |
| advisories/GHSA-p9ff-h696-f583 | B - Useful | Exploit/CVE/offensive | Giữ làm reference; tag rõ use case, chỉ clone khi cần. |
| 0xBlackash/CVE-2026-21643 | B - Useful | Exploit/CVE/offensive | Giữ làm reference; tag rõ use case, chỉ clone khi cần. |
| Adaptix-Framework/AdaptixC2 | B - Useful | Exploit/CVE/offensive | Giữ làm reference; tag rõ use case, chỉ clone khi cần. |
| HackUnderway/cerberus | B - Useful | Exploit/CVE/offensive | Giữ làm reference; tag rõ use case, chỉ clone khi cần. |
| skylot/jadx | B - Useful | Exploit/CVE/offensive | Giữ làm reference; tag rõ use case, chỉ clone khi cần. |
| WangYihang/GitHacker | B - Useful | Exploit/CVE/offensive | Giữ làm reference; tag rõ use case, chỉ clone khi cần. |
| jamiepine/voicebox | S - Core | Voice cloning consent/license review | Ưu tiên đọc README, star/fork/clone nếu cần, gắn vào workspace chính. |
| elementalsouls/Claude-BugHunter | C - Backlog | Exploit/CVE/offensive | Để backlog; chỉ quay lại khi có dự án khớp. |
| gadievron/raptor | C - Backlog | Exploit/CVE/offensive | Để backlog; chỉ quay lại khi có dự án khớp. |
| P4nda0s/reverse-skills | C - Backlog | Exploit/CVE/offensive | Để backlog; chỉ quay lại khi có dự án khớp. |
| staticpayload/oh-my-codex | C - Backlog | Exploit/CVE/offensive | Để backlog; chỉ quay lại khi có dự án khớp. |
| zhaoxuya520/reverse-skill | Q - Quarantine | Reverse engineering/offensive security review | Không clone/chạy tự động. Chỉ giữ để audit, review pháp lý/an toàn trước khi dùng. |
| JesseCHale/HaleHound-CYD | C - Backlog | Exploit/CVE/offensive | Để backlog; chỉ quay lại khi có dự án khớp. |
| OpenAttackDefenseTools/tulip | C - Backlog | Exploit/CVE/offensive | Để backlog; chỉ quay lại khi có dự án khớp. |
| Vuemony/vue-after-free | C - Backlog | Exploit/CVE/offensive | Để backlog; chỉ quay lại khi có dự án khớp. |
| LongLeo287/JerrySFX | D - Dead/Low | Broken/Page not found | Xác minh lại URL; nếu không phục hồi thì archive khỏi danh sách chính. |
| JuliusBrussee/caveman-claude | D - Dead/Low | Broken/Page not found | Xác minh lại URL; nếu không phục hồi thì archive khỏi danh sách chính. |
| claudekit/claudekit-marketing | D - Dead/Low | Broken/Page not found | Xác minh lại URL; nếu không phục hồi thì archive khỏi danh sách chính. |
| carsalgut/reverse-skills | D - Dead/Low | Broken/Page not found | Xác minh lại URL; nếu không phục hồi thì archive khỏi danh sách chính. |
| dotanminh/nextjs-supabase-wms | D - Dead/Low | Broken/Page not found | Xác minh lại URL; nếu không phục hồi thì archive khỏi danh sách chính. |
| COMMUNITY-SCRIPTS/PROXMOZVE | D - Dead/Low | Broken/Page not found | Xác minh lại URL; nếu không phục hồi thì archive khỏi danh sách chính. |
| LongLeo287/bypass-rophim-vip | Q - Quarantine | Piracy/Bypass | Không clone/chạy. Chỉ giữ để audit, xóa hoặc review pháp lý/an toàn. |
| LongLeo287/rophim-vip-2025 | Q - Quarantine | Piracy/Bypass | Không clone/chạy. Chỉ giữ để audit, xóa hoặc review pháp lý/an toàn. |
| LongLeo287/RR_Crack-Extension | Q - Quarantine | Piracy/Bypass | Không clone/chạy. Chỉ giữ để audit, xóa hoặc review pháp lý/an toàn. |
| AykutSarac/jsoncrack.com | Q - Quarantine | Piracy/Bypass | Không clone/chạy. Chỉ giữ để audit, xóa hoặc review pháp lý/an toàn. |
| nghyane/ampcode-connector | Q - Quarantine | Credential/secret risk | Không clone/chạy. Chỉ giữ để audit, xóa hoặc review pháp lý/an toàn. |

_(+44 more in the xlsx)_

## Resource links

| Name | Kind | Tier | URL |
|---|---|---|---|
| omnivoice-vi | dataset | Resource | https://huggingface.co/datasets/STBack23/omnivoice-vi |
| skills.sh | directory | A - High | https://www.skills.sh/ |
| GSAP docs v3 | documentation | A - High | https://gsap.com/docs/v3/ |
| CyberTools4U GitHub Tools | directory | B - Useful | https://cybertools4u.com/github-tools |
