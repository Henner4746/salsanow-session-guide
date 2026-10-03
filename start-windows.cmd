@echo off
setlocal
where py >nul 2>nul
if not errorlevel 1 (
  py -3 "%~dp0remote_ai.py" %*
  goto finished
)
where python >nul 2>nul
if not errorlevel 1 (
  python "%~dp0remote_ai.py" %*
  goto finished
)
echo Python 3.10 or newer is required. Install it from https://www.python.org/downloads/
exit /b 1
:finished
set "RESULT=%ERRORLEVEL%"
if not "%RESULT%"=="0" pause
exit /b %RESULT%
