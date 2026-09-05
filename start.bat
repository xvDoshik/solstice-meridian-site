@echo off
cd /d "%~dp0"
set CMD=%1
if "%CMD%"=="" set CMD=preview
if /i "%CMD%"=="preview" powershell -NoProfile -ExecutionPolicy Bypass -File _tools\preview.ps1 & goto end
if /i "%CMD%"=="deploy" powershell -NoProfile -ExecutionPolicy Bypass -File _tools\deploy.ps1 & goto end
if /i "%CMD%"=="setup" powershell -NoProfile -ExecutionPolicy Bypass -File _tools\setup.ps1 & goto end
if /i "%CMD%"=="build" python build.py & goto end
echo usage: start.bat [preview^|deploy^|setup^|build]
:end
