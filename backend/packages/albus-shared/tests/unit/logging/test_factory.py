
"""Unit tests for the Albus logger factory."""

import logging
from typing import Any
from unittest.mock import patch

import pytest

from albus.shared.logging import (
    LoggingConfig,
    create_logger,
    get_logger,
)


pytestmark = [
    pytest.mark.unit,
    pytest.mark.logging,
]


class TestGetLogger:
    """Verify logger retrieval."""

    def test_get_named_logger(self) -> None:
        """Retrieve a named logger."""
        logger = get_logger("albus.api")

        assert logger is not None
        assert callable(logger.info)

    def test_get_default_logger(self) -> None:
        """Retrieve a logger without an explicit name."""
        assert get_logger() is not None

    @pytest.mark.parametrize(
        "method",
        [
            "debug",
            "info",
            "warning",
            "error",
            "critical",
            "exception",
            "bind",
        ],
    )
    def test_logger_interface(self, method: str) -> None:
        """Expose the expected structured logging interface."""
        logger = get_logger("albus.test")

        assert callable(getattr(logger, method))

    def test_logger_does_not_register_handlers(self) -> None:
        """Retrieve loggers without configuring root handlers."""
        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers.copy()

        get_logger("albus.test")

        assert root_logger.handlers == original_handlers


class TestCreateLogger:
    """Verify explicit logger creation."""

    def test_create_named_logger(
        self,
        logging_config: LoggingConfig,
    ) -> None:
        """Create a logger with a valid configuration."""
        logger = create_logger(
            "albus.worker",
            logging_config,
        )

        assert logger is not None

    @pytest.mark.parametrize("name", ["", " ", "   "])
    def test_invalid_logger_name(
        self,
        logging_config: LoggingConfig,
        name: str,
    ) -> None:
        """Reject blank logger names."""
        with pytest.raises(ValueError):
            create_logger(name, logging_config)

    @pytest.mark.parametrize(
        "config",
        [None, {}, "DEBUG", 123],
    )
    def test_invalid_configuration(
        self,
        config: Any,
    ) -> None:
        """Reject unsupported configuration objects."""
        with pytest.raises(TypeError):
            create_logger("albus.test", config)

    def test_create_logger_does_not_register_handlers(
        self,
        logging_config: LoggingConfig,
    ) -> None:
        """Avoid side effects when creating loggers."""
        root_logger = logging.getLogger()
        original_handlers = root_logger.handlers.copy()

        create_logger("albus.test", logging_config)

        assert root_logger.handlers == original_handlers

    def test_factory_delegates_to_structlog(
        self,
        logging_config: LoggingConfig,
    ) -> None:
        """Delegate logger creation to Structlog."""
        with patch("structlog.get_logger") as mocked:
            create_logger(
                "albus.worker",
                logging_config,
            )

            mocked.assert_called_once()
