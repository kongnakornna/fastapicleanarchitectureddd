# syntax=docker/dockerfile:1.7

# =====================================================================
# Stage 1 — Build frontend assets (Tailwind CSS + esbuild JS bundle)
# =====================================================================
FROM node:20-alpine AS frontend

WORKDIR /app

# Install npm deps first (better layer caching)
COPY package.json package-lock.json* ./
RUN npm ci --no-audit --no-fund || npm install --no-audit --no-fund

# PostCSS + Tailwind configs and sources
COPY tailwind.config.js postcss.config.js* ./
COPY assets ./assets

# Produce static/css/tailwind.output.css + static/js/app.min.js
RUN mkdir -p static/css static/js
RUN npm run build:css:prod && npm run build:js


# =====================================================================
# Stage 2 — Python runtime for Django
# =====================================================================
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DJANGO_SETTINGS_MODULE=config.settings

WORKDIR /app

# Python deps (gunicorn added here since it's not in requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Project source
COPY . .

# Bring in the assets built by the Node stage
COPY --from=frontend /app/static ./static

# Collect static files at build time (uses throwaway values for
# settings that require an env var).
RUN DJANGO_SECRET_KEY=build-only \
    DJANGO_DEBUG=0 \
    python manage.py collectstatic --noinput

# Run as non-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8001

CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8001", \
     "--workers", "3", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]