# Setup environment for VieNeu-TTS
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$venvDir = Join-Path $scriptDir ".venv-vieneu"

Write-Host "Setting up environment for VieNeu-TTS..." -ForegroundColor Cyan

if (-not (Get-Command "uv" -ErrorAction SilentlyContinue)) {
    Write-Host "uv not found. Installing uv..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri "https://astral.sh/uv/install.ps1" -OutFile "install_uv.ps1"
    powershell -ExecutionPolicy ByPass -File "install_uv.ps1"
    Remove-Item "install_uv.ps1"
    $env:Path += ";$env:USERPROFILE\.cargo\bin"
}

Write-Host "Creating virtual environment at $venvDir" -ForegroundColor Green
uv venv $venvDir

Write-Host "Installing vieneu SDK..." -ForegroundColor Green
uv pip install vieneu --python "$venvDir"

Write-Host "Done! You can run VieNeu-TTS via $venvDir\Scripts\python.exe" -ForegroundColor Green
