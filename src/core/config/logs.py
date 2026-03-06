import os.path
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent.parent.parent

LOG_DIR = DIR / "assets/logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler" if os.name == "nt" else "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "django.log"),
            # Only apply rotation kwargs if not on Windows
            **({} if os.name == "nt" else {"when": "midnight", "backupCount": 30}),
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],  # Log to both console and file
            "level": "INFO",
            "propagate": True,
        },
    },
}
