import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# ═══════════════════════════════════════════════
# 🔐 Security
# ═══════════════════════════════════════════════
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "insecure-dev-key-change-me-please")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")
CSRF_TRUSTED_ORIGINS = [
    x for x in os.getenv(
        "CSRF_TRUSTED_ORIGINS",
        "http://localhost:8001,http://127.0.0.1:8001",
    ).split(",") if x
]


# ═══════════════════════════════════════════════
# 📦 Apps
# ═══════════════════════════════════════════════
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django_icons",

"apps.shared",
    "apps.shared.presentation",
    "apps.layout",
    "apps.authentication",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.shared.infrastructure.middleware.FastAPISessionMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# ═══════════════════════════════════════════════
# 📁 Templates
# ═══════════════════════════════════════════════
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
"DIRS": [
        BASE_DIR / "templates",
        BASE_DIR / "apps" / "layout" / "templates",
        BASE_DIR / "apps" / "authentication" / "presentation" / "templates",
        BASE_DIR / "apps" / "user" / "presentation" / "templates",
        BASE_DIR / "apps" / "key" / "presentation" / "templates",
        BASE_DIR / "apps" / "knowledge" / "presentation" / "templates",
        BASE_DIR / "apps" / "notification" / "presentation" / "templates",
    ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.static",
                "django.template.context_processors.media",
                "django.template.context_processors.i18n",
                "apps.shared.presentation.context_processors.layout_context",
                "apps.shared.presentation.context_processors.user_context",
                "apps.shared.presentation.context_processors.menu_context",
                "apps.shared.presentation.context_processors.footer_context",
            ],
        },
    },
]


# ═══════════════════════════════════════════════
# 🗄️ Database
# ═══════════════════════════════════════════════
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ═══════════════════════════════════════════════
# 🌐 i18n
# ═══════════════════════════════════════════════
LANGUAGE_CODE = os.getenv("LANGUAGE_CODE", "th")
TIME_ZONE = "Asia/Bangkok"
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ("th", "ไทย"),
    ("en", "English"),
]

LOCALE_PATHS = [BASE_DIR / "locale"]


# ═══════════════════════════════════════════════
# 📁 Static / Media
# ═══════════════════════════════════════════════
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ═══════════════════════════════════════════════
# 🚀 FastAPI Backend
# ═══════════════════════════════════════════════
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")
FASTAPI_TIMEOUT = int(os.getenv("FASTAPI_TIMEOUT", "30"))


# ═══════════════════════════════════════════════
# 🍪 Session
# ═══════════════════════════════════════════════
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_ENGINE = "django.contrib.sessions.backends.db"

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"


# ═══════════════════════════════════════════════
# 🔀 Login redirect
# ═══════════════════════════════════════════════
LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/auth/login/"
