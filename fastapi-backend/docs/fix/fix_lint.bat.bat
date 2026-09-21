@echo off
REM ============================================================
REM  fix_lint.bat - Auto-fix Ruff lint errors
REM  Project: fastapi-clean-architecture-ddd-erp-iot
REM ============================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   Ruff Lint Auto-Fix Script
echo ============================================================
echo.

REM --- ตรวจสอบว่าอยู่ในโฟลเดอร์ที่ถูกต้อง ---
if not exist "pyproject.toml" (
    echo [ERROR] pyproject.toml not found.
    echo         Please run this script from the project root:
    echo         C:\github\fastapi-clean-architecture-ddd-erp-iot\fastapi-backend
    exit /b 1
)

REM --- Step 1: Auto-fix (safe) ---
echo [1/6] Running safe auto-fixes...
uv run ruff check . --fix
if errorlevel 1 (
    echo [WARN] Some errors could not be auto-fixed. Continuing...
)

REM --- Step 2: Auto-fix (unsafe) ---
echo.
echo [2/6] Running unsafe auto-fixes...
uv run ruff check . --fix --unsafe-fixes
if errorlevel 1 (
    echo [WARN] Some errors could not be auto-fixed. Continuing...
)

REM --- Step 3: แก้ TRY401: logger.exception("...: %s", e) ---
echo.
echo [3/6] Fixing TRY401 (redundant exception in logger.exception)...

REM ใช้ PowerShell สำหรับ regex replacement (ปลอดภัยกว่า sed)
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$files = Get-ChildItem -Path 'app' -Recurse -Include '*.py';" ^
  "$count = 0;" ^
  "foreach ($f in $files) {" ^
  "  $content = Get-Content -Raw -LiteralPath $f.FullName;" ^
  "  $orig = $content;" ^
  "  $content = $content -replace 'logger\.exception\(\s*\"([^\"]+): %s\",\s*e\s*\)', 'logger.exception(\"`$1\")';" ^
  "  $content = $content -replace 'except Exception as e:(\r?\n\s+)logger\.exception', 'except Exception:`$1logger.exception';" ^
  "  if ($content -ne $orig) {" ^
  "    Set-Content -NoNewline -LiteralPath $f.FullName -Value $content;" ^
  "    $count++;" ^
  "  }" ^
  "}" ^
  "Write-Host \"  Fixed $count file(s) for TRY401\""

REM --- Step 4: แก้ DTZ003: datetime.utcnow() ---
echo.
echo [4/6] Fixing DTZ003 (datetime.utcnow -> datetime.now(UTC))...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$files = Get-ChildItem -Path 'app' -Recurse -Include '*.py';" ^
  "$count = 0;" ^
  "foreach ($f in $files) {" ^
  "  $content = Get-Content -Raw -LiteralPath $f.FullName;" ^
  "  $orig = $content;" ^
  "  $content = $content -replace 'from datetime import datetime, timezone', 'from datetime import UTC, datetime';" ^
  "  $content = $content -replace 'from datetime import datetime\r?\n', 'from datetime import UTC, datetime`n';" ^
  "  $content = $content -replace 'datetime\.utcnow\(\)', 'datetime.now(UTC)';" ^
  "  if ($content -ne $orig) {" ^
  "    Set-Content -NoNewline -LiteralPath $f.FullName -Value $content;" ^
  "    $count++;" ^
  "  }" ^
  "}" ^
  "Write-Host \"  Fixed $count file(s) for DTZ003\""

REM --- Step 5: แก้ RUF012: __table_args__ ---
echo.
echo [5/6] Fixing RUF012 (mutable default in class attribute)...
echo        NOTE: Manual fix may still be required.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$files = Get-ChildItem -Path 'app' -Recurse -Include 'models.py';" ^
  "foreach ($f in $files) {" ^
  "  $content = Get-Content -Raw -LiteralPath $f.FullName;" ^
  "  if ($content -match '__table_args__ = \{') {" ^
  "    if ($content -notmatch 'from typing import.*ClassVar') {" ^
  "      $content = 'from typing import ClassVar`n' + $content;" ^
  "    }" ^
  "    $content = $content -replace '__table_args__ = \{', '__table_args__: ClassVar[dict] = {';" ^
  "    Set-Content -NoNewline -LiteralPath $f.FullName -Value $content;" ^
  "    Write-Host \"  Fixed $($f.Name)\"" ^
  "  }" ^
  "}"

REM --- Step 6: Format ---
echo.
echo [6/6] Running ruff format...
uv run ruff format .

echo.
echo ============================================================
echo   Re-checking lint status...
echo ============================================================
echo.
uv run ruff check .
if errorlevel 1 (
    echo.
    echo [WARN] Some errors remain. Please fix them manually.
    echo        See the list above.
    exit /b 1
)

echo.
echo ============================================================
echo   [SUCCESS] All lint errors fixed!
echo ============================================================
echo.

endlocal
exit /b 0