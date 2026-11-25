
"""Context management for Albus logging."""

from __future__ import annotations

from typing import Any

import structlog


def bind_contextvars(**values: Any) -> None:
    """
    Bind contextual information to the current execution context.

    Examples:
        bind_contextvars(
            request_id="req-123",
            workflow_id="workflow-456",
        )
    """

    structlog.contextvars.bind_contextvars(**values)


def clear_contextvars() -> None:
    """Clear all contextual information in the current context."""

    structlog.contextvars.clear_contextvars()


def unbind_contextvars(*keys: str) -> None:
    """Remove selected contextual values."""

    if keys:
        structlog.contextvars.unbind_contextvars(*keys)


def get_contextvars() -> dict[str, Any]:
    """Return a copy of the current logging context."""

    return structlog.contextvars.get_contextvars()
