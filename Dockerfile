# ═════════════════════════════════════════════════════════════════
#  Dockerfile — FastAPI Backend
# ═════════════════════════════════════════════════════════════════

# ─── Stage: builder ─────────────────────────────────────
FROM python:3.13-slim AS builder

# ระบบ: curl + ca-certificates สำหรับโหลด uv
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ติดตั้ง uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# Layer caching: copy lockfile ก่อน
COPY pyproject.toml uv.lock ./

# ติดตั้ง runtime deps เท่านั้น
RUN uv sync --frozen --no-dev

# Copy source
COPY . .


# ─── Stage: runtime ─────────────────────────────────────
FROM python:3.13-slim

# Runtime libs ที่ psycopg / asyncpg ต้องใช้
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy virtualenv + source จาก builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app

# ใช้ .venv ก่อน system python
ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]