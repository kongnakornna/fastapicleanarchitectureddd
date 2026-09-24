# ═══ Step 1: Preview ═══
python run_all_modules.py --dry-run

# ═══ Step 2: Git commit ═══
git add -A && git commit -m "before module generation"

# ═══ Step 3: Run ═══
python run_all_modules.py

# ═══ Step 4: ตรวจผล ═══
git status
git diff --stat

# ═══ Step 5: เปิด server ═══
uvicorn app.app:app --reload

# ═══ Step 6: เปิด Swagger ═══
# http://localhost:8000/docs