@echo off
setlocal
cd /d "%~dp0"
title Build ULTRON.exe

where python >nul 2>&1
if errorlevel 1 (
  echo [ULTRON] Python was not found in PATH.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" python -m venv .venv
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip >nul
pip install -r requirements.txt

set ICON_ARG=
if exist "ultron.ico" set ICON_ARG=--icon ultron.ico

pyinstaller --noconfirm --clean --onefile --windowed ^
  --name ULTRON ^
  %ICON_ARG% ^
  --hidden-import speech_recognition ^
  --hidden-import sounddevice ^
  --hidden-import PIL.ImageGrab ^
  --hidden-import customtkinter ^
  ultron_entry.py

if errorlevel 1 (
  echo.
  echo [ULTRON] Build failed.
  pause
  exit /b 1
)

echo.
echo [ULTRON] Build complete: dist\ULTRON.exe
if exist "ultron.ico" (
  echo [ULTRON] Custom icon embedded.
) else (
  echo [ULTRON] No ultron.ico found. Build used the default executable icon.
  echo Put your chosen icon at ultron.ico and run this file again.
)
pause
endlocal
