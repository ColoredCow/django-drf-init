from email.utils import formataddr

from .env import env

EMAIL_CONFIG = {
    "DEFAULT_FROM_NAME": env("DEFAULT_FROM_NAME", default="COLOREDCOW"),
    "DEFAULT_FROM_EMAIL_ADDRESS": env("DEFAULT_FROM_EMAIL"),
    "EMAIL_BACKEND": env(
        "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
    ),
    "EMAIL_HOST": env("EMAIL_HOST"),
    "EMAIL_PORT": env("EMAIL_PORT", default=587),
    "EMAIL_USE_TLS": env.bool("EMAIL_USE_TLS", default=True),
    "EMAIL_HOST_USER": env("EMAIL_HOST_USER"),
    "EMAIL_HOST_PASSWORD": env("EMAIL_HOST_PASSWORD"),
}

EMAIL_CONFIG["DEFAULT_FROM_EMAIL"] = formataddr(
    (EMAIL_CONFIG["DEFAULT_FROM_NAME"], EMAIL_CONFIG["DEFAULT_FROM_EMAIL_ADDRESS"])
)
