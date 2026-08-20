@echo off
setlocal
cd /d "%~dp0"
title Install ULTRON to Desktop

if not exist "dist\ULTRON.exe" (
  echo [ULTRON] dist\ULTRON.exe does not exist yet.
  echo Run build_ultron_exe.bat first.
  pause
  exit /b 1
)

set "DESKTOP=%USERPROFILE%\Desktop"
if not exist "%DESKTOP%" (
  for /f "usebackq delims=" %%D in (`powershell -NoProfile -Command "[Environment]::GetFolderPath('Desktop')"`) do set "DESKTOP=%%D"
)

copy /Y "dist\ULTRON.exe" "%DESKTOP%\ULTRON.exe" >nul
if errorlevel 1 (
  echo [ULTRON] Could not copy ULTRON.exe to the Desktop.
  pause
  exit /b 1
)

echo [ULTRON] Installed to: %DESKTOP%\ULTRON.exe
echo Double-click ULTRON.exe to launch the core.
pause
endlocal
