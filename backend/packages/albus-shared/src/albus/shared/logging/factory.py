
"""Logger factory for Albus."""

from __future__ import annotations

import structlog


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    Return a structured logger.

    Args:
        name:
            Logger name, normally __name__.

    Returns:
        A structured logger compatible with Python logging.
    """

    return structlog.get_logger(name)
