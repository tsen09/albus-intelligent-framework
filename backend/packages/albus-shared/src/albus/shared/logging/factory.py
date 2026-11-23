"""Logger retrieval and dependency-injected logger factory."""
from __future__ import annotations
import structlog
from .config import LoggingConfig


def create_logger(name: str, config: LoggingConfig):
    """Return a Structlog logger; setup_logging(config) must run first."""
    if not isinstance(config, LoggingConfig):
        raise TypeError("config must be a LoggingConfig instance")
    if not name.strip():
        raise ValueError("logger name cannot be empty")
    return structlog.get_logger(name)


def get_logger(name: str | None = None):
    """Retrieve a Structlog logger after application startup configuration."""
    return structlog.get_logger(name)
