
"""Unit tests for Albus sensitive-data redaction."""

import json
from typing import Any

import pytest

from albus.shared.logging.filters import (
    redact_sensitive_data,
)


pytestmark = [
    pytest.mark.unit,
    pytest.mark.logging,
]


def redact(
    event: dict[str, Any],
) -> dict[str, Any]:
    """Execute the redaction processor."""
    return redact_sensitive_data(
        None,
        "info",
        event,
    )


class TestSensitiveDataRedaction:
    """Verify sensitive-field redaction."""

    def test_password_redaction(self) -> None:
        """Remove plaintext password values."""
        result = redact({
            "event": "login",
            "password": "fake-password-123",
        })

        assert "fake-password-123" not in json.dumps(result)

    def test_api_key_redaction(self) -> None:
        """Remove plaintext API keys."""
        result = redact({
            "event": "api_request",
            "api_key": "fake-api-key-123",
        })

        assert "fake-api-key-123" not in json.dumps(result)

    def test_access_token_redaction(self) -> None:
        """Remove plaintext access tokens."""
        result = redact({
            "event": "authentication",
            "access_token": "fake-access-token-123",
        })

        assert "fake-access-token-123" not in json.dumps(result)

    def test_authorization_redaction(self) -> None:
        """Remove authorization credentials."""
        result = redact({
            "authorization": "Bearer fake-token-123",
        })

        assert "fake-token-123" not in json.dumps(result)

    def test_safe_fields_preserved(self) -> None:
        """Preserve non-sensitive event metadata."""
        event = {
            "event": "request_completed",
            "request_id": "request-001",
            "status_code": 200,
            "duration_ms": 125,
            "success": True,
        }

        assert redact(event.copy()) == event

    def test_nested_password_redaction(self) -> None:
        """Remove sensitive values in nested dictionaries."""
        result = redact({
            "event": "authentication",
            "credentials": {
                "username": "test-user",
                "password": "fake-nested-password",
            },
        })

        assert "fake-nested-password" not in json.dumps(result)

    def test_nested_list_redaction(self) -> None:
        """Remove sensitive values inside nested lists."""
        result = redact({
            "users": [
                {
                    "password": "fake-list-password",
                },
            ],
        })

        assert "fake-list-password" not in json.dumps(result)

    def test_bearer_token_in_message(self) -> None:
        """Remove bearer tokens from free-text messages."""
        result = redact({
            "event": "Authorization: Bearer fake-token-123",
        })

        assert "fake-token-123" not in json.dumps(result)

    def test_empty_event(self) -> None:
        """Safely process an empty event."""
        assert redact({}) == {}

    def test_redaction_is_idempotent(self) -> None:
        """Avoid changing already-redacted values."""
        first = redact({
            "password": "fake-password-123",
        })

        second = redact(first.copy())

        assert first == second

    def test_multiple_sensitive_fields(self) -> None:
        """Redact multiple credentials in one event."""
        secrets = [
            "fake-password-001",
            "fake-token-002",
            "fake-api-key-003",
        ]

        result = redact({
            "password": secrets[0],
            "access_token": secrets[1],
            "api_key": secrets[2],
        })

        serialized = json.dumps(result)

        for secret in secrets:
            assert secret not in serialized
