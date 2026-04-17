from pathlib import Path
import os

from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-dev-secret-key")
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = [host for host in os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",") if host]

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "channels",
    "rest_framework",
    "rest_framework_simplejwt",
    "users",
    "bids",
    "chat",
    "leads",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.getenv("REDIS_URL", "redis://redis:6379/0")],
        },
    },
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "sales_crm"),
        "USER": os.getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "HOST": os.getenv("POSTGRES_HOST", "db"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE_ALIASES = {
    "Asia/Calcutta": "Asia/Kolkata",
}
TIME_ZONE = TIME_ZONE_ALIASES.get(os.getenv("DJANGO_TIME_ZONE", "UTC"), os.getenv("DJANGO_TIME_ZONE", "UTC"))
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "users.User"
LOGIN_URL = "/admin/login/"
LOGIN_REDIRECT_URL = "/admin/"
LOGOUT_REDIRECT_URL = "/admin/login/"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTES", "60"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", "1"))),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

CORS_ALLOWED_ORIGINS = [
    origin for origin in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173").split(",") if origin
]

JAZZMIN_SETTINGS = {
    "site_title": "Sales CRM Admin",
    "site_header": "Sales CRM Control Center",
    "site_brand": "Sales CRM",
    "site_logo": "branding/sales-crm.png",
    "site_icon": "branding/favicon.png",
    "login_logo": "branding/sales-crm.png",
    "site_logo_classes": "img-fluid",
    "custom_css": "branding/admin.css",
    "welcome_sign": "Welcome to the Sales CRM admin console",
    "copyright": "Sales CRM",
    "search_model": "users.User",
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "order_with_respect_to": ["users", "bids", "leads", "chat", "auth"],
    "icons": {
        "users": "fas fa-users-cog",
        "users.user": "fas fa-user",
        "bids": "fas fa-briefcase",
        "bids.bid": "fas fa-file-signature",
        "bids.bidplatform": "fas fa-store",
        "bids.bidprofile": "fas fa-id-badge",
        "leads": "fas fa-chart-line",
        "leads.leadstatus": "fas fa-list-check",
        "chat": "fas fa-comments",
        "chat.chatroom": "fas fa-layer-group",
        "chat.chatparticipant": "fas fa-user-friends",
        "chat.message": "fas fa-comment-dots",
        "chat.mention": "fas fa-at",
        "auth.group": "fas fa-users",
    },
    "topmenu_links": [
        {"name": "API Root", "url": "/", "new_window": True},
        {"name": "Frontend", "url": "http://localhost:5173", "new_window": True},
    ],
}
