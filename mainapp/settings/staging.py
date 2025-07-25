from .base import *  # noqa: F403, F401
from .env import env

ALLOWED_HOSTS = env("ALLOWED_HOSTS", cast=lambda v: [s.strip() for s in v.split(",")])
CORS_ALLOW_CREDENTIALS = env("CORS_ALLOW_CREDENTIALS", default=True, cast=bool)
DEBUG = env.bool("DEBUG", default=False)

CORS_ALLOWED_ORIGINS = env(
    "CORS_ALLOWED_ORIGINS", cast=lambda v: [s.strip() for s in v.split(",")]
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", default="coloredcow_staging"),
        "USER": env("DB_USER", default="coloredcow_staging"),
        "PASSWORD": env("DB_PASSWORD", default="coloredcow_staging"),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="5432"),
    }
}
