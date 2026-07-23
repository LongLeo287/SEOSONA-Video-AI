# 0_SETUP — Environment management (single source of truth)

Everything this project needs to run, in ONE place. To see live status: `python 0_SETUP/check_env.py`.
To set up a fresh machine: `0_SETUP/bootstrap.ps1`. Heavy artifacts (venvs, models, node_modules) live
OUTSIDE git — this folder is the MAP + the installers, not the binaries.

## 1. Python environments (3 venvs, all Python 3.11)
Why 3: the render/inference stack is pinned to torch 2.5 and must not be bumped; voice GPU + training
need torch 2.8 — kept isolated so they can't break inference.

| Env | Location | torch | Purpose | Requirements |
|-----|----------|-------|---------|--------------|
| **main / inference** | `…/hermes/hermes-agent/venv` (the `python` on PATH) | 2.5.1+cu121 | render (native_composer), PhoWhisper ASR, all `4_BRAIN`/`scripts` | `requirements/main.txt` |
| **OmniVoice** | `7_ASSETS/voice/.venv-omnivoice` | 2.8.0+cu128 (CUDA) | the BRAND VOICE engine (OmniVoice, GPU) — run via subprocess | `requirements/omnivoice.txt` |
| **training** | `7_ASSETS/voice/training/.venv-train` | 2.8.0+cu128 | ⚠️ OBSOLETE — was the LoRA voice training; LoRA removed 2026-06-30. Deletable. | — |

The main venv is the user's hermes agent venv (shared, not project-local) — do NOT recreate/move it;
just install `requirements/main.txt` into it. Project-local venvs are created by `bootstrap.ps1`.

## 2. Models
In-project (small, may be git-ignored):
- `7_ASSETS/voice/profiles/cqa_omnivoice_ref.wav` (+ `.txt`) — the CQA brand-voice clone reference.

HuggingFace cache (`~/.cache/huggingface/hub`, auto-downloaded on first use — NOT in the repo):
- `k2-fsa/OmniVoice` (3.1 GB) — brand voice (the ONLY voice engine; weights CC-BY-NC, owner-accepted).
- `kiendt/PhoWhisper-large-ct2` (3.1 GB) — Vietnamese ASR primary (2026-07-14: replaced the defective
  in-project medium int8 CT2, which is quarantined — see `MODELS.md`).

See `MODELS.md` for exact fetch commands.

## 3. Node + system tools
- **node** ≥ 20 (tested v22) + `node_modules/` (`npm install`) — includes **hyperframes** (render engine)
  and **ffmpeg-static** (the ffmpeg binary the whole pipeline uses; resolved via `native_composer._ffmpeg_bin`).
- **uv** — fast Python installer (used for the isolated venvs). **git**. **ffmpeg** is bundled (ffmpeg-static).

## 4. Clone to a NEW machine — setup order
```powershell
# 0. prerequisites: Python 3.11, Node ≥20, git, uv, an NVIDIA GPU + recent driver (for voice GPU)
git clone <repo> ; cd "SEOSONA Video"
0_SETUP\bootstrap.ps1        # creates venvs, installs all requirements, npm install, prints next steps
python 0_SETUP\check_env.py  # verify every row is [ OK ]
# Models auto-download from HuggingFace on first run; or pre-fetch via MODELS.md.
```

## 5. Files in this folder
- `check_env.py` — live status dashboard (what's installed / missing). Read-only.
- `bootstrap.ps1` — one-command setup for a fresh clone.
- `MODELS.md` — model registry + fetch/cleanup commands.
- `requirements/{main,omnivoice}.txt` — frozen package lists per venv.

## 6. Voice system (current)
OmniVoice (brand voice = CQA clone, GPU, `.venv-omnivoice`) is the ONLY voice engine — no backup;
a failed synth returns None honestly (user decision 2026-07-14, Phase-0 benchmark). All other
engines removed (VieNeu/F5/edge/LoRA). See `voice_router.py` + `MODELS.md`.
