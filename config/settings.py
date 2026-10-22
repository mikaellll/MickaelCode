"""
Django settings for MickaelCode platform.
Full-stack Python/Django architecture refactored from mickaelcode.com.
"""

from pathlib import Path
from decouple import config, Csv
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-mickaelcode-dev-environment-secure-local-key-2026"
)

DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1,mickaelcode.com,*.railway.app",
    cast=Csv()
)

CSRF_TRUSTED_ORIGINS = [
    "https://mickaelcode.com",
    "https://*.mickaelcode.com",
    "https://*.railway.app",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

# Custom User Model
AUTH_USER_MODEL = "accounts.User"

# Application definition
INSTALLED_APPS = [
    # Modern Admin UI (Unfold must precede django.contrib.admin)
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",

    # Business applications
    "core.apps.CoreConfig",
    "accounts.apps.AccountsConfig",
    "blog.apps.BlogConfig",
    "courses.apps.CoursesConfig",
    "billing.apps.BillingConfig",
    "dashboard.apps.DashboardConfig",
    "marketing.apps.MarketingConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.global_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database configuration
# Uses SQLite for zero-friction local development, PostgreSQL via DATABASE_URL in production
DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Authentication backends (allows email or username login)
AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailOrUsernameModelBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files (User uploads, course covers, blog covers)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage" if not DEBUG else "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Auth Redirects
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:overview"
LOGOUT_REDIRECT_URL = "core:home"

# Stripe configuration
STRIPE_PUBLIC_KEY = config("STRIPE_PUBLIC_KEY", default="")
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET", default="")

# Marketing & Newsletter (Brevo / MailerLite)
NEWSLETTER_PROVIDER = config("NEWSLETTER_PROVIDER", default="brevo")
BREVO_API_KEY = config("BREVO_API_KEY", default="")
BREVO_LIST_ID = config("BREVO_LIST_ID", default=1, cast=int)

# Video Streaming / Bunny Stream / Mux
VIDEO_PROVIDER = config("VIDEO_PROVIDER", default="bunny")
BUNNY_STREAM_LIBRARY_ID = config("BUNNY_STREAM_LIBRARY_ID", default="")
BUNNY_STREAM_API_KEY = config("BUNNY_STREAM_API_KEY", default="")
BUNNY_STREAM_TOKEN_KEY = config("BUNNY_STREAM_TOKEN_KEY", default="")

# Email Settings
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="MickaelCode <contact@mickaelcode.com>")
SITE_URL = config("SITE_URL", default="http://127.0.0.1:8000")

# Security in Production
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Django Unfold Theme Customization
UNFOLD = {
    "SITE_TITLE": "MickaelCode Admin",
    "SITE_HEADER": "MickaelCode Dashboard",
    "SITE_URL": "/",
    "DASHBOARD_CALLBACK": "core.admin.dashboard_callback",
    "COLORS": {
        "primary": {
            "50": "240 253 250",
            "100": "204 251 241",
            "200": "153 246 228",
            "300": "94 234 212",
            "400": "45 212 191",
            "500": "0 255 255", # Cyan signature
            "600": "13 148 136",
            "700": "15 118 110",
            "800": "17 94 89",
            "900": "19 78 74",
            "950": "4 47 46",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Gestion du Contenu",
                "separator": True,
                "items": [
                    {
                        "title": "Articles de Blog",
                        "icon": "article",
                        "link": "/admin/blog/post/",
                    },
                    {
                        "title": "Catégories Blog",
                        "icon": "category",
                        "link": "/admin/blog/category/",
                    },
                    {
                        "title": "Réalisations Portfolio",
                        "icon": "work",
                        "link": "/admin/core/portfolioproject/",
                    },
                    {
                        "title": "Compétences",
                        "icon": "psychology",
                        "link": "/admin/core/skill/",
                    },
                ],
            },
            {
                "title": "E-Learning & Formations",
                "separator": True,
                "items": [
                    {
                        "title": "Formations Vidéo",
                        "icon": "school",
                        "link": "/admin/courses/course/",
                    },
                    {
                        "title": "Modules",
                        "icon": "view_module",
                        "link": "/admin/courses/module/",
                    },
                    {
                        "title": "Leçons",
                        "icon": "play_lesson",
                        "link": "/admin/courses/lesson/",
                    },
                    {
                        "title": "Inscriptions & Accès",
                        "icon": "badge",
                        "link": "/admin/courses/enrollment/",
                    },
                ],
            },
            {
                "title": "Ventes & Facturation",
                "separator": True,
                "items": [
                    {
                        "title": "Commandes Stripe",
                        "icon": "shopping_cart",
                        "link": "/admin/billing/order/",
                    },
                    {
                        "title": "Événements Webhook",
                        "icon": "webhook",
                        "link": "/admin/billing/paymentwebhookevent/",
                    },
                ],
            },
            {
                "title": "Marketing & Utilisateurs",
                "separator": True,
                "items": [
                    {
                        "title": "Utilisateurs",
                        "icon": "person",
                        "link": "/admin/accounts/user/",
                    },
                    {
                        "title": "Abonnés Newsletter",
                        "icon": "mail",
                        "link": "/admin/marketing/newslettersubscriber/",
                    },
                    {
                        "title": "Messages de Contact",
                        "icon": "chat",
                        "link": "/admin/core/contactmessage/",
                    },
                ],
            },
        ],
    },
}
