<#
.SYNOPSIS
Setup script to isolate OmniVoice into its own virtual environment (.venv-omnivoice)
following the SEOSONA AI video pipeline architecture.
#>

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $ScriptDir ".venv-omnivoice"

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host " OmniVoice LOCAL ENVIRONMENT SETUP (.venv-omnivoice)" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# 1. Create Virtual Environment
if (-not (Test-Path $VenvDir)) {
    Write-Host "[1/4] Creating virtual environment at $VenvDir using uv..." -ForegroundColor Yellow
    uv venv --python 3.11 $VenvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment using uv." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[1/4] Virtual environment already exists at $VenvDir." -ForegroundColor Green
}

# 2. Install PyTorch with CUDA
Write-Host "[2/4] Installing PyTorch with CUDA (NVIDIA GPU Support)..." -ForegroundColor Yellow
uv pip install --python $VenvDir torch==2.4.0+cu124 torchaudio==2.4.0+cu124 --extra-index-url https://download.pytorch.org/whl/cu124

# 3. Install OmniVoice from Source
Write-Host "[3/4] Installing OmniVoice and its dependencies..." -ForegroundColor Yellow
uv pip install --python $VenvDir git+https://github.com/k2-fsa/OmniVoice.git

# 4. Setup reference audio directory
$WorkspaceDir = Join-Path (Split-Path (Split-Path $ScriptDir -Parent) -Parent) "7_ASSETS\refvoice"
if (-not (Test-Path $WorkspaceDir)) {
    Write-Host "[4/4] Creating reference voice directory at $WorkspaceDir..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $WorkspaceDir | Out-Null
    Write-Host "👉 IMPORTANT: Please put a clean 10-15s voice sample named 'clone_ref.wav' in $WorkspaceDir" -ForegroundColor Magenta
} else {
    Write-Host "[4/4] Reference voice directory verified." -ForegroundColor Green
}

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "✅ OmniVoice Setup Complete!" -ForegroundColor Green
Write-Host "The SEOSONA Video pipeline will automatically use this isolated environment." -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Cyan
