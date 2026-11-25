
"""Unit tests for Albus logging context management."""

import asyncio

import pytest

from albus.shared.logging import (
    bind_contextvars,
    clear_contextvars,
    get_contextvars,
    unbind_contextvars,
)


pytestmark = [
    pytest.mark.unit,
    pytest.mark.logging,
]


class TestLoggingContext:
    """Verify logging context operations."""

    def test_initial_context_is_empty(self) -> None:
        """Start with an empty logging context."""
        assert get_contextvars() == {}

    def test_bind_single_value(self) -> None:
        """Bind a single context value."""
        bind_contextvars(request_id="request-001")

        assert get_contextvars()["request_id"] == "request-001"

    def test_bind_multiple_values(self) -> None:
        """Bind multiple context values."""
        bind_contextvars(
            request_id="request-001",
            user_id="user-001",
            environment="testing",
        )

        assert get_contextvars() == {
            "request_id": "request-001",
            "user_id": "user-001",
            "environment": "testing",
        }

    def test_update_existing_value(self) -> None:
        """Replace an existing context value."""
        bind_contextvars(request_id="request-001")
        bind_contextvars(request_id="request-002")

        assert get_contextvars()["request_id"] == "request-002"

    def test_bind_preserves_existing_values(self) -> None:
        """Preserve previously bound context values."""
        bind_contextvars(request_id="request-001")
        bind_contextvars(user_id="user-001")

        assert get_contextvars() == {
            "request_id": "request-001",
            "user_id": "user-001",
        }

    def test_unbind_single_value(self) -> None:
        """Remove a selected context value."""
        bind_contextvars(
            request_id="request-001",
            user_id="user-001",
        )

        unbind_contextvars("user_id")

        assert get_contextvars() == {
            "request_id": "request-001",
        }

    def test_unbind_multiple_values(self) -> None:
        """Remove multiple selected context values."""
        bind_contextvars(
            request_id="request-001",
            user_id="user-001",
            environment="testing",
        )

        unbind_contextvars("user_id", "environment")

        assert get_contextvars() == {
            "request_id": "request-001",
        }

    def test_unbind_nonexistent_value(self) -> None:
        """Safely ignore missing context keys."""
        unbind_contextvars("nonexistent")

        assert get_contextvars() == {}

    def test_clear_context(self) -> None:
        """Remove all bound context values."""
        bind_contextvars(
            request_id="request-001",
            user_id="user-001",
        )

        clear_contextvars()

        assert get_contextvars() == {}

    def test_clear_empty_context(self) -> None:
        """Safely clear an already empty context."""
        clear_contextvars()
        clear_contextvars()

        assert get_contextvars() == {}

    def test_context_snapshot(self) -> None:
        """Prevent mutation through returned context dictionaries."""
        bind_contextvars(request_id="request-001")

        context = get_contextvars()
        context["request_id"] = "modified"

        assert get_contextvars()["request_id"] == "request-001"


class TestAsyncLoggingContext:
    """Verify context isolation between asynchronous tasks."""

    @pytest.mark.asyncio
    async def test_concurrent_task_isolation(self) -> None:
        """Prevent context leakage between concurrent tasks."""

        async def worker(request_id: str) -> str:
            bind_contextvars(request_id=request_id)

            await asyncio.sleep(0)

            return get_contextvars()["request_id"]

        results = await asyncio.gather(
            worker("request-001"),
            worker("request-002"),
            worker("request-003"),
        )

        assert results == [
            "request-001",
            "request-002",
            "request-003",
        ]

        assert get_contextvars() == {}

    @pytest.mark.asyncio
    async def test_child_task_inherits_context(self) -> None:
        """Propagate parent context into a child task."""
        bind_contextvars(request_id="parent-request")

        async def child() -> str:
            return get_contextvars()["request_id"]

        result = await asyncio.create_task(child())

        assert result == "parent-request"

    @pytest.mark.asyncio
    async def test_child_does_not_modify_parent(self) -> None:
        """Isolate child context modifications."""
        bind_contextvars(request_id="parent-request")

        async def child() -> None:
            bind_contextvars(request_id="child-request")

        await asyncio.create_task(child())

        assert get_contextvars()["request_id"] == "parent-request"
