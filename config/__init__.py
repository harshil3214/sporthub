"""
Project package initializer.

Celery is optional in this project. If it's not installed (e.g. fresh setup),
we still want Django management commands (migrate/runserver) to work.
"""

try:
    from .celery import app as celery_app
    __all__ = ("celery_app",)
except ModuleNotFoundError:
    __all__ = ()