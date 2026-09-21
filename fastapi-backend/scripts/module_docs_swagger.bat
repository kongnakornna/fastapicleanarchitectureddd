@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0module_docs_swagger.ps1" %*
if errorlevel 1 (
  echo.
  echo [ERROR] module_docs_swagger.ps1 failed
)
pause