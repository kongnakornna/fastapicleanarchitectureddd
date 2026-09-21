# 1) แก้ .env
#    APPLICATION_TABLE_PREFIX=erp_

# 2) reset DB
alembic downgrade base
del alembic\versions\*.py            # Windows
alembic revision --autogenerate -m "init erp tables"
alembic upgrade head

# 3) ตรวจสอบ
psql -d ioterp -c "\dt"

uv python pin 3.13
Remove-Item -Recurse -Force .venv
uv sync
make migrate
make dev
