@echo off
setlocal
cd /d "%~dp0"
title Install ULTRON to Desktop

if not exist "dist\ULTRON.exe" (
  echo [ULTRON] ULTRON.exe not found. Building it now...
  call build_ultron_exe.bat
)

if not exist "dist\ULTRON.exe" (
  echo [ULTRON] Build did not produce dist\ULTRON.exe.
  pause
  exit /b 1
)

for /f "usebackq delims=" %%D in (`powershell -NoProfile -Command "[Environment]::GetFolderPath('Desktop')"`) do set "DESKTOP=%%D"
if not defined DESKTOP set "DESKTOP=%USERPROFILE%\Desktop"

copy /Y "dist\ULTRON.exe" "%DESKTOP%\ULTRON.exe" >nul
if errorlevel 1 (
  echo [ULTRON] Could not copy ULTRON.exe to the Desktop.
  pause
  exit /b 1
)

echo.
echo [ULTRON] Installed successfully.
echo [ULTRON] Desktop app: %DESKTOP%\ULTRON.exe
echo [ULTRON] The custom ULTRON icon is embedded in the executable.
echo.
echo Double-click ULTRON.exe to launch the core.
pause
endlocal
