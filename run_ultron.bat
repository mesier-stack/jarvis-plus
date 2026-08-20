@echo off
setlocal
cd /d "%~dp0"
title ULTRON // Adaptive Intelligence Core

where python >nul 2>&1
if errorlevel 1 (
  echo [ULTRON] Python was not found in PATH.
  echo Install Python 3.11+ and try again.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [ULTRON] Creating isolated environment...
  python -m venv .venv
)

call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip >nul
pip install -r requirements.txt

if errorlevel 1 (
  echo [ULTRON] Dependency installation failed.
  pause
  exit /b 1
)

python ultron_main.py

if errorlevel 1 (
  echo.
  echo [ULTRON] Core terminated with an error.
  pause
)
endlocal
