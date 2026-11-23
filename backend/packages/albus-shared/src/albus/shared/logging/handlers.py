
"""Logging handlers for Albus."""

from __future__ import annotations

import gzip
import logging
import logging.handlers
import re
import shutil
import threading
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
        """Identify expired rotated files."""

        if not self.compression:
            return super().getFilesToDelete()

        if self.backupCount <= 0:
            return []

        base_path = Path(self.baseFilename)
        prefix = f"{base_path.name}."

        pattern = re.compile(
            rf"^{re.escape(prefix)}"
            r"\d{4}-\d{2}-\d{2}"
            r"(?:_\d{2}-\d{2}-\d{2})?\.gz$"
        )

        candidates = sorted(
            str(path)
            for path in base_path.parent.iterdir()
            if path.is_file() and pattern.match(path.name)
        )

        return candidates[:-self.backupCount]


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

        self._lock = threading.RLock()

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

        with self._lock:
            if module_name not in self._handlers:

                filename = (
                    self.config.log_dir
                    / f"{module_name}.log"
                )

                handler = GzipTimedRotatingFileHandler(
                    str(filename),
                    when=self.config.rotation_when,
                    interval=self.config.rotation_interval,
                    backupCount=self.config.retention_days,
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

        with self._lock:
            for handler in self._handlers.values():
                handler.close()

            self._handlers.clear()

        super().close()
