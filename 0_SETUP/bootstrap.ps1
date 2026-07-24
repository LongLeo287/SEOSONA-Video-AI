# SEOSONA Video — one-command environment setup for a fresh clone.
# Recreates the venvs, installs all requirements, runs npm install. Idempotent.
# Heavy models auto-download from HuggingFace on first run (see MODELS.md to pre-fetch).
#   PS> 0_SETUP\bootstrap.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
Write-Host "==== SEOSONA Video bootstrap ====" -ForegroundColor Cyan

function Need($name) { if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
    Write-Host "[FAIL] '$name' not found on PATH — install it first." -ForegroundColor Red; exit 1 } }
Need python; Need node; Need npm
$haveUv = [bool](Get-Command uv -ErrorAction SilentlyContinue)
if (-not $haveUv) { Write-Host "[warn] uv not found — the isolated voice venv needs it (https://astral.sh/uv)." -ForegroundColor Yellow }

# 1) Node + render engine + ffmpeg
Write-Host "`n[1/4] npm install (hyperframes + ffmpeg-static + deps)…" -ForegroundColor Cyan
npm install

# 2) main / inference venv (the hermes venv on PATH) — install project requirements into it
Write-Host "`n[2/4] pip install -r requirements/main.txt (into the active 'python')…" -ForegroundColor Cyan
python -m pip install -r "0_SETUP\requirements\main.txt"

# 3) OmniVoice venv (torch 2.8 + CUDA) — the brand voice engine
Write-Host "`n[3/4] OmniVoice venv (torch CUDA)…" -ForegroundColor Cyan
$ovDir = "7_ASSETS\voice\.venv-omnivoice"
$ovPy  = "$ovDir\Scripts\python.exe"
if ($haveUv) {
    $env:UV_LINK_MODE = "copy"
    if (-not (Test-Path $ovPy)) { uv venv $ovDir --python 3.11 }
    uv pip install --python $ovPy -r "0_SETUP\requirements\omnivoice.txt"
    Write-Host "    ensuring CUDA torch (RTX GPU)…"
    uv pip install --python $ovPy "torch==2.8.0" "torchaudio==2.8.0" --index-url https://download.pytorch.org/whl/cu128
} else {
    Write-Host "[skip] OmniVoice venv — install uv, then re-run." -ForegroundColor Yellow
}

# 4) verify
Write-Host "`n[4/4] verifying…" -ForegroundColor Cyan
python "0_SETUP\check_env.py"

Write-Host "`n==== done ====" -ForegroundColor Green
Write-Host "Models auto-download from HuggingFace on first render. To pre-fetch see 0_SETUP\MODELS.md."
Write-Host "If voice should use the GPU, confirm the OmniVoice row shows 'cuda True' above."
