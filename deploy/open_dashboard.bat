@echo off
REM SEOSONA Video — one-click dashboard. Double-click this file:
REM   - starts the Flask server (in its own window)
REM   - waits a moment, then opens the browser to the dashboard
cd /d "%~dp0.."
start "SEOSONA Dashboard" cmd /c "npm run start:dashboard"
timeout /t 3 /nobreak >nul
start "" http://localhost:5050
