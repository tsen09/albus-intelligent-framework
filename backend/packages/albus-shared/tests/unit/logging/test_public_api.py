
"""Tests for the Albus logging public API."""

from importlib import import_module

import pytest

import albus.shared.logging as albus_logging


pytestmark = [
    pytest.mark.unit,
    pytest.mark.logging,
]


PUBLIC_API = [
    "LoggingConfig",
    "setup_logging",
    "get_logger",
    "create_logger",
    "bind_contextvars",
    "unbind_contextvars",
    "clear_contextvars",
    "get_contextvars",
]


class TestPublicAPI:
    """Verify the public logging interface."""

    @pytest.mark.parametrize("name", PUBLIC_API)
    def test_public_export_exists(
        self,
        name: str,
    ) -> None:
        """Expose each documented public API member."""
        assert hasattr(albus_logging, name)

    @pytest.mark.parametrize("name", PUBLIC_API)
    def test_public_export_callable(
        self,
        name: str,
    ) -> None:
        """Expose callable public API members."""
        assert callable(getattr(albus_logging, name))

    def test_config_import_identity(self) -> None:
        """Export the original configuration class."""
        module = import_module(
            "albus.shared.logging.config",
        )

        assert (
            albus_logging.LoggingConfig
            is module.LoggingConfig
        )

    def test_factory_import_identity(self) -> None:
        """Export the original logger factory functions."""
        module = import_module(
            "albus.shared.logging.factory",
        )

        assert albus_logging.get_logger is module.get_logger

        assert (
            albus_logging.create_logger
            is module.create_logger
        )

    def test_setup_import_identity(self) -> None:
        """Export the original setup function."""
        module = import_module(
            "albus.shared.logging.setup",
        )

        assert (
            albus_logging.setup_logging
            is module.setup_logging
        )


class TestCompatibilityAPI:
    """Verify backward-compatible logging imports."""

    @pytest.mark.parametrize(
        "name",
        [
            "setup_logging",
            "get_logger",
            "create_logger",
        ],
    )
    def test_compatibility_exports(
        self,
        name: str,
    ) -> None:
        """Preserve compatibility with legacy imports."""
        compatibility_module = import_module(
            "albus.shared.logging.logging",
        )

        assert getattr(
            compatibility_module,
            name,
        ) is getattr(
            albus_logging,
            name,
        )
