"""Fixtures for the Albus logging unit tests."""

from collections.abc import Iterator
import logging
import os
from pathlib import Path

import pytest
import structlog

from albus.shared.logging import (
    LoggingConfig,
    clear_contextvars,
)


@pytest.fixture(autouse=True)
def isolate_logging_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Remove external logging environment variables."""
    for name in tuple(os.environ):
        if name.upper().startswith("ALBUS_LOG_"):
            monkeypatch.delenv(name, raising=False)


@pytest.fixture(autouse=True)
def isolate_logging_state() -> Iterator[None]:
    """Isolate global logging state between tests."""
    root_logger = logging.getLogger()

    original_handlers = root_logger.handlers.copy()
    original_level = root_logger.level
    original_config = structlog.get_config().copy()
    was_configured = structlog.is_configured()

    third_party_loggers = (
        "httpx",
        "httpcore",
        "PIL",
        "urllib3",
    )

    original_levels = {
        name: logging.getLogger(name).level
        for name in third_party_loggers
    }

    clear_contextvars()

    yield

    clear_contextvars()

    for handler in root_logger.handlers.copy():
        if handler not in original_handlers:
            root_logger.removeHandler(handler)
            handler.close()

    for handler in original_handlers:
        if handler not in root_logger.handlers:
            root_logger.addHandler(handler)

    root_logger.setLevel(original_level)

    for name, level in original_levels.items():
        logging.getLogger(name).setLevel(level)

    structlog.reset_defaults()

    if was_configured:
        structlog.configure(**original_config)


@pytest.fixture
def log_directory(tmp_path: Path) -> Path:
    """Provide an isolated directory for generated log files."""
    directory = tmp_path / "logs"
    directory.mkdir()

    return directory


@pytest.fixture
def logging_config(log_directory: Path) -> LoggingConfig:
    """Provide a deterministic logging configuration."""
    return LoggingConfig(
        log_level="DEBUG",
        console_enabled=True,
        console_format="json",
        file_enabled=True,
        log_dir=log_directory,
        module_namespace="albus",
        rotation_when="midnight",
        rotation_interval=1,
        retention_days=14,
        compression=True,
        redact_sensitive=True,
    )