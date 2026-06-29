@echo off
REM SEOSONA Video - daily production launcher (for Windows Task Scheduler).
REM Free/local by default. To also publish, set SEOSONA_PUBLISH before scheduling,
REM e.g.  setx SEOSONA_PUBLISH telegram   (telegram is the free instant target).
cd /d "%~dp0.."
call npm run daily >> "logs\daily\schtasks.out" 2>&1
