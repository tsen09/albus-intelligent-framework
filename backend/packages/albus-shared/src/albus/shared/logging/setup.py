
"""Centralized logging initialization for Albus."""

from __future__ import annotations

import logging
import os
import sys

import structlog

from .config import LoggingConfig
from .handlers import ModuleFileRouter
from .processors import (
    get_foreign_pre_chain,
    get_formatter_processors,
    get_structlog_processors,
)


def _resolve_console_format(config: LoggingConfig) -> str:
    """Resolve the console output format."""

    if config.console_format != "auto":
        return config.console_format

    environment = os.getenv(
        "ALBUS_ENV",
        os.getenv("ENV", "development"),
    ).strip().lower()

    if environment in {"production", "prod"}:
        return "json"

    if not sys.stderr.isatty():
        return "json"

    return "console"


def _build_formatter(
    config: LoggingConfig,
    *,
    json_output: bool,
) -> structlog.stdlib.ProcessorFormatter:
    """Build a formatter for logging handlers."""

    renderer = (
        structlog.processors.JSONRenderer()
        if json_output
        else structlog.dev.ConsoleRenderer(colors=True)
    )

    return structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=get_foreign_pre_chain(),
        processors=[
            *get_formatter_processors(
                redact_sensitive=config.redact_sensitive,
            ),
            renderer,
        ],
    )


def _configure_structlog() -> None:
    """Configure structlog's standard-library integration."""

    structlog.configure(
        processors=get_structlog_processors(),
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def _configure_third_party_loggers() -> None:
    """Reduce excessive logging from third-party dependencies."""

    noisy_loggers = {
        "httpx": logging.WARNING,
        "httpcore": logging.WARNING,
        "PIL": logging.WARNING,
        "urllib3": logging.WARNING,
    }

    for name, level in noisy_loggers.items():
        logging.getLogger(name).setLevel(level)


def setup_logging(
    config: LoggingConfig | None = None,
) -> None:
    """
    Initialize Albus logging infrastructure.

    Call once during application startup.

    Args:
        config:
            Optional LoggingConfig instance.
            Environment configuration is used by default.
    """

    config = config or LoggingConfig.from_env()

    root_logger = logging.getLogger()

    # Remove previously configured root handlers.
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        handler.close()

    root_logger.setLevel(config.log_level)

    # Configure structlog.
    _configure_structlog()

    # Configure console logging.
    console_format = _resolve_console_format(config)

    if config.console_enabled:
        console_formatter = _build_formatter(
            config,
            json_output=(console_format == "json"),
        )

        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.NOTSET)
        console_handler.setFormatter(console_formatter)

        root_logger.addHandler(console_handler)

    # Configure module-specific file logging.
    if config.file_enabled:
        file_formatter = _build_formatter(
            config,
            json_output=True,
        )

        file_handler = ModuleFileRouter(
            config=config,
            formatter=file_formatter,
        )

        file_handler.setLevel(logging.NOTSET)
        root_logger.addHandler(file_handler)

    # Configure third-party logger levels.
    _configure_third_party_loggers()
