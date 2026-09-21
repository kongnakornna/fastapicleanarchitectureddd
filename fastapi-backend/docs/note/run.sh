#!/usr/bin/env bash
# ============================================================
#  ERP + CRM + IoT Module Generator - Unix Launcher
#  ตัวเรียกใช้ตัวสร้างโมดูลสำหรับ Linux/macOS
# ============================================================

set -e
set -o pipefail

# --- Fix Thai/Unicode encoding ---
export LANG="${LANG:-en_US.UTF-8}"
export LC_ALL="${LC_ALL:-en_US.UTF-8}"
export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "============================================================"
echo "  ERP + CRM + IoT  -  Module Generator"
echo "  ตัวสร้างโมดูล ERP + CRM + IoT"
echo "============================================================"
echo ""

# --- ตรวจสอบ Python ---
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo -e "${RED}[ERROR]${NC} Python not found"
        exit 1
    fi
    PYTHON=python
else
    PYTHON=python3
fi

PYVER=$($PYTHON --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}[OK]${NC} Python version: $PYVER"

# --- ตรวจสอบ generator ---
if [ ! -f "generate.py" ]; then
    echo -e "${RED}[ERROR]${NC} generate.py not found"
    exit 1
fi
echo -e "${GREEN}[OK]${NC} generate.py found"

# --- สร้าง venv ---
if [ ! -d ".venv" ]; then
    echo ""
    echo -e "${BLUE}[STEP]${NC} Creating virtual environment..."
    $PYTHON -m venv .venv
    echo -e "${GREEN}[OK]${NC} venv created"
fi

# shellcheck disable=SC1091
source .venv/bin/activate
echo -e "${GREEN}[OK]${NC} venv activated"

# --- ติดตั้ง dependencies ---
echo ""
echo -e "${BLUE}[STEP]${NC} Installing dependencies..."
pip install --upgrade pip -q

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q || {
        echo -e "${YELLOW}[WARN]${NC} Some dependencies failed"
    }
else
    pip install fastapi "uvicorn[standard]" pydantic sqlalchemy asyncpg redis -q || true
fi

# --- รัน generator ---
echo ""
echo "============================================================"
echo "  Running generator..."
echo "============================================================"
echo ""

if $PYTHON generate.py "$@"; then
    echo ""
    echo "============================================================"
    echo -e "  ${GREEN}[SUCCESS]${NC} Generation complete"
    echo -e "  ${GREEN}[สำเร็จ]${NC} การสร้างเสร็จสมบูรณ์"
    echo "============================================================"
    echo ""
    echo "Next steps / ขั้นตอนต่อไป:"
    echo "  1. Review generated files"
    echo "  2. Run tests: pytest tests/ -v"
    echo "  3. Start server: uvicorn app.main:app --reload"
    echo ""
else
    echo -e "${RED}[ERROR]${NC} Generation failed"
    exit 1
fi