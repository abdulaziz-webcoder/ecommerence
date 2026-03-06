import os

redis_url = os.getenv("REDIS_CACHE_URL")

if redis_url:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": redis_url,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
            "KEY_PREFIX": "core",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    }

# Cache Middleware Timeout (ensure it's an integer)
CACHE_MIDDLEWARE_SECONDS = int(os.getenv("CACHE_TIMEOUT", 300))

# Celery Configuration
_broker = os.getenv("CELERY_BROKER", "").strip()

if _broker:
    CELERY_BROKER_URL = _broker
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", _broker)
else:
    # Fallback for PythonAnywhere free tier: run Celery tasks synchronously in the main web thread
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_STORE_EAGER_RESULT = True

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
