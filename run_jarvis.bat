@echo off
title JARVIS+ Launcher
cd /d "%~dp0"
echo %~dp0| findstr /I /L /C:"\Temp\Rar$" >nul
if not errorlevel 1 (
  echo [JARVIS+] Do not run JARVIS from inside WinRAR.
  echo [JARVIS+] Click Extract To, open the extracted folder, then run this launcher again.
  pause
  exit /b 1
)
if exist ".venv\Scripts\python.exe" (
  .venv\Scripts\python.exe -m pip --version >nul 2>&1
  if errorlevel 1 (
    echo [JARVIS+] Repairing a damaged private environment...
    rmdir /s /q ".venv"
  )
)
if not exist ".venv\Scripts\python.exe" (
  echo [JARVIS+] First launch: creating the private environment...
  py -m venv .venv
  .venv\Scripts\python.exe -m ensurepip --upgrade
)
if not exist ".venv\.jarvis-v4.0-ready" (
  echo [JARVIS+] Installing version 4.0 adaptive conversation update...
  .venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
  .venv\Scripts\python.exe -m pip install -r requirements.txt
  if errorlevel 1 (
    echo.
    echo [JARVIS+] Installation failed. Take a screenshot of this window.
    pause
    exit /b 1
  )
  echo ready>".venv\.jarvis-v4.0-ready"
)
.venv\Scripts\python.exe main.py
if errorlevel 1 (
  echo.
  echo [JARVIS+] The app stopped with an error. Take a screenshot of this window.
  pause
)
