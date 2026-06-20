<#
.SYNOPSIS
Setup script to isolate F5-TTS into its own virtual environment (.venv-f5)
following the LoHa Tech video pipeline architecture.
#>

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $ScriptDir ".venv-f5"

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host " F5-TTS LOCAL ENVIRONMENT SETUP (.venv-f5)" -ForegroundColor Cyan
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

# 3. Install PyTorch with CUDA 12.4
Write-Host "[2/4] Installing PyTorch with CUDA 12.4 (NVIDIA GPU Support)..." -ForegroundColor Yellow
uv pip install --python $VenvDir torch==2.4.0+cu124 torchaudio==2.4.0+cu124 --extra-index-url https://download.pytorch.org/whl/cu124

# 4. Install F5-TTS from Source
Write-Host "[3/4] Installing F5-TTS and its dependencies..." -ForegroundColor Yellow
uv pip install --python $VenvDir git+https://github.com/SWivid/F5-TTS.git

# 5. Setup reference audio directory
$WorkspaceDir = Join-Path (Split-Path (Split-Path $ScriptDir -Parent) -Parent) "7_ASSETS\refvoice"
if (-not (Test-Path $WorkspaceDir)) {
    Write-Host "[4/4] Creating reference voice directory at $WorkspaceDir..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $WorkspaceDir | Out-Null
    Write-Host "👉 IMPORTANT: Please put a clean 10-15s voice sample named 'clone_ref.wav' in $WorkspaceDir" -ForegroundColor Magenta
} else {
    Write-Host "[4/4] Reference voice directory verified." -ForegroundColor Green
}

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "✅ F5-TTS Setup Complete!" -ForegroundColor Green
Write-Host "The SEOSONA Video pipeline will automatically use this isolated environment." -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Cyan
