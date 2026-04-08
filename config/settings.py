import environ
import os
from pathlib import Path

# Initialize environ
env = environ.Env(DEBUG=(bool, False))

BASE_DIR = Path(__file__).resolve().parent.parent

# Read .env file
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# =============================================================================
# CORE SETTINGS
# =============================================================================

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# =============================================================================
# APPLICATION DEFINITION
# =============================================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "a_users",
    "b_customers",
    "c_devices",
    "d_repairs",
    "e_quotations",
    "f_payments",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "a_users.middleware.LoginRequiredMiddleware",
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
                "a_users.context_processors.current_url_name",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# =============================================================================
# DATABASE
# =============================================================================

DATABASES = {
    "default": env.db(),
}

# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Manila"
USE_I18N = True
USE_TZ = True

# =============================================================================
# STATIC FILES
# =============================================================================

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# =============================================================================
# DEFAULT PRIMARY KEY
# =============================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =============================================================================
# AUTHENTICATION
# =============================================================================

AUTH_USER_MODEL = "a_users.User"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

# =============================================================================
# PDF GENERATION (Signed URLs)
# =============================================================================

# How long PDF URLs remain valid (in seconds)
# 60 seconds is enough for Playwright to fetch the page
PDF_URL_EXPIRY_SECONDS = env.int("PDF_URL_EXPIRY_SECONDS", default=60)

# =============================================================================
# EMAIL CONFIGURATION
# =============================================================================

EMAIL_BACKEND = env(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env(
    "DEFAULT_FROM_EMAIL", default="Elektro Master Repairs <noreply@elektromaster.com>"
)

# =============================================================================
# PRODUCTION SECURITY SETTINGS (FIX #5)
# =============================================================================

# These settings are OFF by default (safe for development)
# Enable them in production by setting environment variables

# Redirect all HTTP requests to HTTPS
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)

# Only send session cookie over HTTPS
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=False)

# Only send CSRF cookie over HTTPS
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=False)

# Tell browsers to only use HTTPS for this site (in seconds)
# 31536000 = 1 year (recommended for production)
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=0)

# Include subdomains in HSTS policy
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=False
)

# Add site to browser's HSTS preload list
SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=False)

# Prevent browsers from MIME-sniffing the content type
SECURE_CONTENT_TYPE_NOSNIFF = env.bool("SECURE_CONTENT_TYPE_NOSNIFF", default=True)
