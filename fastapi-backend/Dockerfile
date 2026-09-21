# ---- Stage: builder ----
FROM python:3.14-slim AS builder

# ติดตั้ง curl + ca-certificates เพื่อโหลด uv
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ติดตั้ง uv ผ่าน official installer (จาก astral.sh — ไม่ใช่ ghcr.io)
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

# เพิ่ม uv เข้า PATH
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# คัดลอก lockfile ก่อน (layer caching)
COPY pyproject.toml uv.lock ./

# ติดตั้งเฉพาะ runtime deps
RUN uv sync --frozen --no-dev

# คัดลอก source
COPY . .

# ---- Stage: runtime ----
FROM python:3.14-slim

WORKDIR /app

# ย้าย .venv + source จาก builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app
COPY --from=builder /root/.local/share/uv/python /root/.local/share/uv/python

# ให้ .venv มาก่อน system
ENV PATH="/app/.venv/bin:$PATH"

# ไม่ต้องใช้ uv ใน runtime อีก — uvicorn อยู่ใน .venv แล้ว
EXPOSE 8000

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]