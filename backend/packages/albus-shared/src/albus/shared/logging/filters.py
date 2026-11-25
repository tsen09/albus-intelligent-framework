
"""Sensitive-data filtering for Albus logging."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any


REDACTED = "[REDACTED]"

SENSITIVE_KEYS = {
    "password",
    "passwd",
    "secret",
    "token",
    "access_token",
    "refresh_token",
    "api_key",
    "apikey",
    "authorization",
    "credentials",
    "credential",
    "private_key",
    "client_secret",
    "database_url",
    "connection_string",
}

SENSITIVE_VALUE_PATTERN = re.compile(
    r"""(?ix)
    (?P<key>
        password|passwd|secret|api[_-]?key|
        access[_-]?token|refresh[_-]?token|
        client[_-]?secret|authorization
    )
    (\s*[:=]\s*)
    (?P<value>
        "[^"]*"|'[^']*'|[^\s,;]+
    )
    """
)

BEARER_PATTERN = re.compile(
    r"(?i)(bearer\s+)[a-z0-9._~+/=-]+"
)


def _normalize_key(key: Any) -> str:
    """Normalize field names for sensitive-key matching."""
    return str(key).lower().replace("-", "_")


def redact_value(value: Any) -> Any:
    """Recursively redact sensitive values."""

    if isinstance(value, Mapping):
        return {
            key: (
                REDACTED
                if _normalize_key(key) in SENSITIVE_KEYS
                else redact_value(item)
            )
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [redact_value(item) for item in value]

    if isinstance(value, tuple):
        return tuple(redact_value(item) for item in value)

    if isinstance(value, str):
        return redact_text(value)

    return value


def redact_text(value: str) -> str:
    """Redact recognizable credentials in free-text messages."""

    value = SENSITIVE_VALUE_PATTERN.sub(
        lambda match: (
            f"{match.group('key')}{match.group(2)}{REDACTED}"
        ),
        value,
    )

    value = BEARER_PATTERN.sub(
        rf"\g<1>{REDACTED}",
        value,
    )

    return value


def redact_sensitive_data(
    logger: Any,
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Structlog processor for sensitive-data redaction."""

    return redact_value(event_dict)
