import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(Path(__file__).parent / ".env")

# ลองอ่านแบบแยกตัวแปรก่อน
user = os.getenv("POSTGRES_USER") or os.getenv("DB_USER")
password = os.getenv("POSTGRES_PASSWORD") or os.getenv("DB_PASSWORD")
host = os.getenv("POSTGRES_HOST") or os.getenv("DB_HOST") or "localhost"
port = os.getenv("POSTGRES_PORT") or os.getenv("DB_PORT") or "5432"
db = os.getenv("POSTGRES_DB") or os.getenv("DB_NAME")

# ถ้าโปรเจกต์มี DATABASE_URL อยู่แล้วก็ใช้เลย
url = os.getenv("DATABASE_URL") or os.getenv("SQLALCHEMY_DATABASE_URI")

if not url:
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"

print("URL:", url)

engine = create_engine(url)
with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
print("Dropped alembic_version.")
