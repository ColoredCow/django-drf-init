from .base import *  # noqa: F403, F401
from .env import env

DEBUG = True
ALLOWED_HOSTS = env("ALLOWED_HOSTS", cast=lambda v: [s.strip() for s in v.split(",")])
CORS_ALLOW_CREDENTIALS = True

EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",  # default as console, change ENV variable to use SMTP or other methods
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", default="coloredcow"),
        "USER": env("DB_USER", default="colredcow"),
        "PASSWORD": env("DB_PASSWORD", default="coloredcow"),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="5432"),
    }
}

STATIC_URL = "static/"
