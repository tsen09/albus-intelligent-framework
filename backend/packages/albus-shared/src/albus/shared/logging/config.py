
"""Centralized configuration for Albus logging."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


ConsoleFormat = Literal["auto", "console", "json"]


def _get_bool(name: str, default: bool) -> bool:
    """Read a boolean environment variable."""
    value = os.getenv(name)

    if value is None:
        return default

    normalized = value.strip().lower()

    if normalized in {"true", "1", "yes", "on"}:
        return True

    if normalized in {"false", "0", "no", "off"}:
        return False

    raise ValueError(f"Invalid boolean value for {name}: {value}")


@dataclass(frozen=True, slots=True)
class LoggingConfig:
    """Configuration for the Albus logging subsystem."""

    log_level: str = "INFO"

    console_enabled: bool = True
    console_format: ConsoleFormat = "auto"

    file_enabled: bool = True
    log_dir: Path = Path("logs")

    rotation_when: str = "midnight"
    rotation_interval: int = 1
    retention_days: int = 14
    compression: bool = True

    module_namespace: str = "albus"

    redact_sensitive: bool = True

    def __post_init__(self) -> None:
        """Validate configuration values."""

        normalized_level = self.log_level.upper()

        if normalized_level not in {
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        }:
            raise ValueError(
                f"Unsupported logging level: {self.log_level}"
            )

        if self.console_format not in {
            "auto",
            "console",
            "json",
        }:
            raise ValueError(
                f"Unsupported console format: {self.console_format}"
            )

        if self.rotation_interval < 1:
            raise ValueError("rotation_interval must be at least 1")

        if self.retention_days < 0:
            raise ValueError("retention_days cannot be negative")

        if not self.module_namespace.strip():
            raise ValueError("module_namespace cannot be empty")

        object.__setattr__(self, "log_level", normalized_level)
        object.__setattr__(self, "log_dir", Path(self.log_dir))

    @classmethod
    def from_env(cls) -> LoggingConfig:
        """Build logging configuration from environment variables."""

        return cls(
            log_level=os.getenv(
                "ALBUS_LOG_LEVEL",
                "INFO",
            ),
            console_enabled=_get_bool(
                "ALBUS_LOG_TO_CONSOLE",
                True,
            ),
            console_format=os.getenv(
                "ALBUS_LOG_FORMAT",
                "auto",
            ).lower(),
            file_enabled=_get_bool(
                "ALBUS_LOG_TO_FILE",
                True,
            ),
            log_dir=Path(
                os.getenv("ALBUS_LOG_DIR", "logs")
            ),
            rotation_when=os.getenv(
                "ALBUS_LOG_ROTATION",
                "midnight",
            ),
            rotation_interval=int(
                os.getenv("ALBUS_LOG_ROTATION_INTERVAL", "1")
            ),
            retention_days=int(
                os.getenv("ALBUS_LOG_RETENTION_DAYS", "14")
            ),
            compression=_get_bool(
                "ALBUS_LOG_COMPRESSION",
                True,
            ),
            module_namespace=os.getenv(
                "ALBUS_LOG_NAMESPACE",
                "albus",
            ),
            redact_sensitive=_get_bool(
                "ALBUS_LOG_REDACT_SENSITIVE",
                True,
            ),
        )
