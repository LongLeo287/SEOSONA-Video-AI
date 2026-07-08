# 0_SETUP — Root files map (what every loose file at the project root is + why it lives there)

The 18 files at the repo root are NOT clutter — almost all are **convention-locked**: the tool that
reads them (npm, git, dotenv, puppeteer, pip, the AI agents, the SEOSONA OS binding) discovers them at
the project root BY CONVENTION. Moving them into subfolders breaks that discovery → the user's
"don't break / don't lose connections" rule wins, so they STAY at root. This file is the management
map so the root is *understood*, not *messy*.

## A. HARD-LOCKED at root — moving BREAKS a tool / the OS audit
| File | Owner / why root-locked |
|------|--------------------------|
| `package.json`, `package-lock.json` | **npm** — must be at root; defines deps + all `npm run` scripts |
| `.gitignore`, `.gitattributes` | **git** — only read at repo root |
| `.puppeteerrc.cjs` | **puppeteer** — auto-discovered at root (Chromium config for HyperFrames render) |
| `.clauderules`, `.cursorrules` | **Claude Code / Cursor** — read at root |
| `requirements.txt` | **pip** + in the OS audit's `requiredFiles` (also mirrored at `0_SETUP/requirements/main.txt`) |
| `seosona.project.json` | **SEOSONA OS binding** + OS audit `requiredFiles` — parent OS resolves the project via this |
| `system_config.yaml` | OS audit `requiredFiles` + 3 code loaders read `ROOT/system_config.yaml` |
| `AGENTS.md` | OS audit `requiredFiles` + AI-agent instructions read at root (12 refs) |
| `GEMINI.md` | OS audit `requiredFiles` + Gemini-agent instructions |
| `ARCHITECTURE.md` | **OS audit `requiredFiles`** — `npm run seosona:audit` fails if missing from root |

## B. Movable in theory — but a strong convention keeps each at root (net negative to move)
| File | Could move? | Why keep at root |
|------|-------------|------------------|
| `.env` | risky | 4 `load_dotenv()` calls — `llm_engine.py` uses bare `load_dotenv()` (cwd default); holds **secrets**; root is the universal standard |
| `.env.example` | yes | nothing reads it (template) — but it PAIRS with `.env`; separating them loses the point |
| `README.md` | yes | **GitHub auto-renders the root README** as the repo home page — move it and the repo shows no front page |
| `setup.bat` | yes (path tweak) | entry point users expect at root; it redirects to `0_SETUP/bootstrap.ps1` |

## C. Truly free to move — 1 file
| File | Note |
|------|------|
| `STRUCTURE.md` | project structure doc, 1 ref, NOT in the OS audit. Safe to move to `2_KNOWLEDGE/` on request. |

→ Default: keep all at root (each has a tool or convention reason). Only `STRUCTURE.md` is a no-downside move.

## Why NOT a `1_CONFIG/` folder
Every "config-looking" root file is owned by a tool that needs it at root: `.env`/`.env.example`
(dotenv), `.puppeteerrc.cjs` (puppeteer), `requirements.txt` (pip), `seosona.project.json` +
`system_config.yaml` (the OS audit's required-files check). Relocating them = broken tooling + a failed
`npm run seosona:audit`. So a `1_CONFIG/` folder would either be empty or break things. The management
layer is this map + `0_SETUP/` (env/models/setup), not a physical config move.

To see live env status: `npm run env:check`.
