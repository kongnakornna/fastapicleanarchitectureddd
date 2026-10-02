# Upgrade pip
python -m pip install --upgrade pip

# Install pg8000 ★
python -m pip install pg8000

# Verify
python -c "import pg8000; print('✅ pg8000', pg8000.__version__)"

# Save requirements
python -m pip freeze > requirements.txt

# Migrate
python -m alembic upgrade head

# Run
python -m uvicorn app.app:app --reload --port 8000
