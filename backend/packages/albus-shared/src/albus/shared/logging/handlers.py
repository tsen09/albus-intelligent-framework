
"""Logging handlers for Albus."""

from __future__ import annotations

import gzip
import logging
import logging.handlers
import re
import shutil
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .config import LoggingConfig


class GzipTimedRotatingFileHandler(
    logging.handlers.TimedRotatingFileHandler
):
    """Timed rotating file handler with optional gzip compression."""

    def __init__(
        self,
        filename: str,
        *,
        compression: bool = True,
        **kwargs: Any,
    ) -> None:
        self.compression = compression
        self.retention_days = int(kwargs.pop("retention_days", 14))

        if compression:
            self.namer = self._namer
            self.rotator = self._rotator

        super().__init__(filename, **kwargs)

    @staticmethod
    def _namer(default_name: str) -> str:
        return f"{default_name}.gz"

    @staticmethod
    def _rotator(source: str, destination: str) -> None:
        """Compress a rotated log file."""

        with open(source, "rb") as source_file:
            with gzip.open(destination, "wb") as destination_file:
                shutil.copyfileobj(source_file, destination_file)

        Path(source).unlink(missing_ok=True)

    def getFilesToDelete(self) -> list[str]:
        """Delete rotated files older than the configured calendar-day window."""
        if self.retention_days == 0:
            return []  # Explicitly retain indefinitely.
        base = Path(self.baseFilename)
        prefix = base.name + "."
        expired: list[str] = []
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
        for path in base.parent.iterdir():
            if not path.is_file() or not path.name.startswith(prefix):
                continue
            suffix = path.name[len(prefix):]
            if suffix.endswith(".gz"):
                suffix = suffix[:-3]
            # Only consider names created by the configured timed rotator.
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:_\d{2}-\d{2}-\d{2})?", suffix):
                continue
            try:
                timestamp = datetime.strptime(suffix, "%Y-%m-%d_%H-%M-%S" if "_" in suffix else "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                continue
            if timestamp < cutoff:
                expired.append(str(path))
        return expired


class ModuleFileRouter(logging.Handler):
    """Route records into separate files based on logger names."""

    def __init__(
        self,
        config: LoggingConfig,
        formatter: logging.Formatter,
    ) -> None:
        super().__init__()

        self.config = config
        self.formatter = formatter

        self._handlers: dict[
            str,
            GzipTimedRotatingFileHandler,
        ] = {}

        self._router_lock = threading.RLock()

        self.config.log_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _resolve_module_name(self, logger_name: str) -> str:
        """Convert logger names into safe file names."""

        namespace = self.config.module_namespace

        if logger_name == namespace:
            name = "core"

        elif logger_name.startswith(f"{namespace}."):
            name = logger_name[len(namespace) + 1:]

        else:
            name = "external"

        name = re.sub(
            r"[^a-zA-Z0-9_-]+",
            "_",
            name,
        ).strip("_")

        return name or "unknown"

    def _get_handler(
        self,
        logger_name: str,
    ) -> GzipTimedRotatingFileHandler:

        module_name = self._resolve_module_name(logger_name)

        with self._router_lock:
            if module_name not in self._handlers:

                filename = (
                    self.config.log_dir
                    / f"{module_name}.log"
                )

                handler = GzipTimedRotatingFileHandler(
                    str(filename),
                    when=self.config.rotation_when,
                    interval=self.config.rotation_interval,
                    backupCount=1 if self.config.retention_days else 0,
                    retention_days=self.config.retention_days,
                    encoding="utf-8",
                    delay=True,
                    utc=True,
                    compression=self.config.compression,
                )

                handler.setLevel(logging.NOTSET)
                handler.setFormatter(self.formatter)

                self._handlers[module_name] = handler

            return self._handlers[module_name]

    def emit(self, record: logging.LogRecord) -> None:
        """Write a log record to its module-specific handler."""

        try:
            handler = self._get_handler(record.name)
            handler.emit(record)

        except Exception:
            self.handleError(record)

    def close(self) -> None:
        """Close all managed file handlers."""

        with self._router_lock:
            for handler in self._handlers.values():
                handler.close()

            self._handlers.clear()

        super().close()
