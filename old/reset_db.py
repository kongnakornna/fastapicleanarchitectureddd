import psycopg2
from app.core.settings import settings

conn = psycopg2.connect(
    host=settings.POSTGRESQL_HOST,
    port=settings.POSTGRESQL_PORT,
    user=settings.POSTGRESQL_USERNAME,
    password=settings.POSTGRESQL_PASSWORD,
    dbname='postgres'
)
conn.autocommit = True
cur = conn.cursor()

cur.execute("""
    SELECT pg_terminate_backend(pid)
    FROM pg_stat_activity
    WHERE datname = %s AND pid <> pg_backend_pid()
""", (settings.POSTGRESQL_DATABASE,))

cur.execute(f"DROP DATABASE IF EXISTS {settings.POSTGRESQL_DATABASE}")
cur.execute(f"CREATE DATABASE {settings.POSTGRESQL_DATABASE}")
print("Database recreated successfully")

cur.close()
conn.close()
