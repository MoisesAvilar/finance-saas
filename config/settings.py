import os
import sys
from pathlib import Path
from datetime import timedelta

import dj_database_url
from dotenv import load_dotenv
from corsheaders.defaults import default_headers

# ---------------------------------------------------------------------
# BASE
# ---------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, os.path.join(BASE_DIR, "apps"))
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-fallback-key")
DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "").split(",")
    if host
]

# ---------------------------------------------------------------------
# APPS
# ---------------------------------------------------------------------
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # Auth / Social
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "dj_rest_auth",
    "dj_rest_auth.registration",

    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework.authtoken",
    "corsheaders",
    "django_filters",
    "drf_spectacular",

    # Local apps
    "pwa",
    "core",
    "common",
    "accounts",
    "vehicles",
    "operations",
    "analytics",

    # Static
    "whitenoise.runserver_nostatic",
]

SITE_ID = 1

# ---------------------------------------------------------------------
# AUTH / ALLAUTH (Google ID Token validation)
# ---------------------------------------------------------------------
SOCIALACCOUNT_ADAPTER = "allauth.socialaccount.adapter.DefaultSocialAccountAdapter"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APPS": [
            {
                "client_id": os.getenv("GOOGLE_CLIENT_ID_WEB"),
                "secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "key": "",
            }
        ],
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "METHOD": "oauth2",
        "VERIFIED_EMAIL": True,
    }
}

SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_EMAIL_REQUIRED = False
SOCIALACCOUNT_QUERY_EMAIL = True

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

AUTH_USER_MODEL = "accounts.CustomUser"

# ---------------------------------------------------------------------
# MIDDLEWARE (ORDEM IMPORTA)
# ---------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",   # ⬅️ sempre antes
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "allauth.account.middleware.AccountMiddleware",
]

# ---------------------------------------------------------------------
# URL / TEMPLATES
# ---------------------------------------------------------------------
ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.common.context_processors.banners",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"

LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

# ---------------------------------------------------------------------
# DATABASE
# ---------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

database_url = os.getenv("DATABASE_URL")
if database_url:
    DATABASES["default"] = dj_database_url.parse(
        database_url, conn_max_age=600
    )

# ---------------------------------------------------------------------
# PASSWORD VALIDATION
# ---------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------
# I18N / TIMEZONE
# ---------------------------------------------------------------------
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ---------------------------------------------------------------------
# STATIC / MEDIA
# ---------------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# ---------------------------------------------------------------------
# REST / JWT
# ---------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

REST_USE_JWT = True

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

# ---------------------------------------------------------------------
# CORS (CONFIGURAÇÃO CORRETA PARA NEXT + EXPO)
# ---------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://corre-certo.vercel.app",
]

CORS_ALLOW_HEADERS = list(default_headers) + [
    "authorization",
]

CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "https://corre-certo.vercel.app",
    "https://driverfinance.pythonanywhere.com",
]

# ---------------------------------------------------------------------
# PWA
# ---------------------------------------------------------------------
PWA_APP_NAME = "DriverFinance"
PWA_APP_DESCRIPTION = "Controle financeiro inteligente para motoristas."
PWA_APP_THEME_COLOR = "#2563eb"
PWA_APP_BACKGROUND_COLOR = "#ffffff"
PWA_APP_DISPLAY = "standalone"
PWA_APP_SCOPE = "/"
PWA_APP_START_URL = "/"

PWA_APP_ICONS = [
    {"src": "/static/images/android-chrome-192x192.png", "sizes": "192x192"},
    {"src": "/static/images/android-chrome-512x512.png", "sizes": "512x512"},
]

PWA_APP_ICONS_APPLE = [
    {"src": "/static/images/apple-touch-icon.png", "sizes": "180x180"},
]

PWA_SERVICE_WORKER_PATH = os.path.join(
    BASE_DIR, "static/js/serviceworker.js"
)

# ---------------------------------------------------------------------
# DRF SPECTACULAR
# ---------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "Driver Finance API",
    "DESCRIPTION": "API para o aplicativo Driver Finance",
    "VERSION": "1.0.0",
}
