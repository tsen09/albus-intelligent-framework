
"""Structlog processors for Albus logging."""

from __future__ import annotations

from typing import Any

import structlog
from structlog.processors import CallsiteParameter

from .filters import redact_sensitive_data


CALLSITE_PARAMETERS = {
    CallsiteParameter.FILENAME,
    CallsiteParameter.FUNC_NAME,
    CallsiteParameter.LINENO,
    CallsiteParameter.MODULE,
    CallsiteParameter.PATHNAME,
    CallsiteParameter.PROCESS,
    CallsiteParameter.PROCESS_NAME,
    CallsiteParameter.THREAD,
    CallsiteParameter.THREAD_NAME,
}


def get_structlog_processors() -> list:
    """Return processors for structured log events."""

    return [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.CallsiteParameterAdder(
            parameters=CALLSITE_PARAMETERS,
        ),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]


def get_foreign_pre_chain() -> list:
    """Process standard-library log records."""

    return [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.ExtraAdder(),
        structlog.processors.CallsiteParameterAdder(
            parameters=CALLSITE_PARAMETERS,
        ),
    ]


def get_formatter_processors(
    redact_sensitive: bool = True,
) -> list:
    """Return final formatting processors."""

    processors = [
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        structlog.processors.TimeStamper(
            fmt="iso",
            utc=True,
        ),
    ]

    if redact_sensitive:
        processors.append(redact_sensitive_data)

    processors.append(
        structlog.processors.dict_tracebacks
    )

    return processors
