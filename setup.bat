@echo off
:: SEOSONA Video — setup entry point. The real, maintained setup lives in 0_SETUP\.
:: This just hands off to the PowerShell bootstrap (creates venvs, installs everything).
echo ==================================================
echo        SEOSONA VIDEO - ENVIRONMENT SETUP
echo   (single source of truth: 0_SETUP\)
echo ==================================================
echo.
echo Running 0_SETUP\bootstrap.ps1 ...
powershell -ExecutionPolicy Bypass -File "%~dp00_SETUP\bootstrap.ps1"
echo.
echo To see environment status any time:  npm run env:check
echo Docs:  0_SETUP\ENVIRONMENT.md  +  0_SETUP\MODELS.md
pause
