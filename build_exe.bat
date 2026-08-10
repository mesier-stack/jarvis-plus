@echo off
title Build JARVIS+ EXE
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call run_jarvis.bat
call .venv\Scripts\activate.bat
pyinstaller --noconfirm --clean --windowed --name "JARVIS+" --collect-all customtkinter --collect-all speech_recognition --collect-all google main.py
echo.
echo Finished. Your app is in dist\JARVIS+\
pause
