@echo off
setlocal enabledelayedexpansion

echo ==================================================
echo        SEOSONA VIDEO - ENVIRONMENT SETUP
echo ==================================================

:: 1. Create Virtual Environment if missing
if not exist ".venv" (
    echo [INFO] Virtual environment '.venv' not found. Creating it...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [FAIL] Could not create .venv. Is Python 3.10+ installed and in PATH?
        pause
        exit /b 1
    )
    echo [PASS] Virtual environment created.
)

:: 2. Check Node.js
npm -v >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] Node.js is not installed or not in PATH!
    echo Please install Node.js 22+ and try again.
    pause
    exit /b 1
)

:: 3. Run the Python Bootstrapper (Doctor)
echo [INFO] Handing over to SEOSONA Doctor...
call .venv\Scripts\python.exe scripts\seosona_doctor.py

echo.
pause
