# settings/__init__.py

from .env import env

django_env = env("DJANGO_ENV", default="local")

if django_env == "production":
    from .production import *  # noqa: F403, F401

    print("Using production settings")
elif django_env == "staging":
    from .staging import *  # noqa: F403, F401

    print("Using staging settings")
else:
    from .local import *  # noqa: F403, F401

    print("Using local settings")
