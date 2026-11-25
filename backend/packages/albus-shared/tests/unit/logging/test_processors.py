
"""Tests for the Albus structured logging processors."""

import json
from pathlib import Path
from typing import Any

import pytest

from albus.shared.logging import (
    LoggingConfig,
    bind_contextvars,
    get_logger,
    setup_logging,
)


pytestmark = [
    pytest.mark.unit,
    pytest.mark.logging,
]


def read_last_record(
    log_directory: Path,
) -> dict[str, Any]:
    """Read the last JSON record from the processor log."""
    log_file = log_directory / "processor.log"

    records = log_file.read_text(
        encoding="utf-8",
    ).splitlines()

    return json.loads(records[-1])


class TestLoggingProcessors:
    """Verify structured event processing."""

    def test_event_message(
        self,
        logging_config: LoggingConfig,
        log_directory: Path,
    ) -> None:
        """Preserve the original event message."""
        setup_logging(logging_config)

        get_logger("albus.processor").info(
            "processor_event"
        )

        record = read_last_record(log_directory)

        assert record["event"] == "processor_event"

    def test_logger_name(
        self,
        logging_config: LoggingConfig,
        log_directory: Path,
    ) -> None:
        """Include the originating logger name."""
        setup_logging(logging_config)

        get_logger("albus.processor").info("test")

        record = read_last_record(log_directory)

        assert record["logger"] == "albus.processor"

    @pytest.mark.parametrize(
        "level",
        ["debug", "info", "warning", "error", "critical"],
    )
    def test_log_level(
        self,
        logging_config: LoggingConfig,
        log_directory: Path,
        level: str,
    ) -> None:
        """Include the correct logging level."""
        setup_logging(logging_config)

        logger = get_logger("albus.processor")

        getattr(logger, level)("test")

        record = read_last_record(log_directory)

        assert record["level"] == level

    def test_timestamp_present(
        self,
        logging_config: LoggingConfig,
        log_directory: Path,
    ) -> None:
        """Include an event timestamp."""
        setup_logging(logging_config)

        get_logger("albus.processor").info("test")

        record = read_last_record(log_directory)

        assert isinstance(record["timestamp"], str)
        assert record["timestamp"]

    def test_structured_metadata(
        self,
        logging_config: LoggingConfig,
        log_directory: Path,
    ) -> None:
        """Preserve structured metadata and value types."""
        setup_logging(logging_config)

        get_logger("albus.processor").info(
            "test",
            duration_ms=125,
            success=True,
            component="processor",
        )

        record = read_last_record(log_directory)

        assert record["duration_ms"] == 125
        assert record["success"] is True
        assert record["component"] == "processor"

    def test_context_injection(
        self,
        logging_config: LoggingConfig,
        log_directory: Path,
    ) -> None:
        """Merge bound context into the event."""
        setup_logging(logging_config)

        bind_contextvars(
            request_id="request-001",
            environment="testing",
        )

        get_logger("albus.processor").info("test")

        record = read_last_record(log_directory)

        assert record["request_id"] == "request-001"
        assert record["environment"] == "testing"

    def test_bound_logger_metadata(
        self,
        logging_config: LoggingConfig,
        log_directory: Path,
    ) -> None:
        """Preserve metadata bound directly to a logger."""
        setup_logging(logging_config)

        logger = get_logger("albus.processor").bind(
            component="worker",
        )

        logger.info("test")

        record = read_last_record(log_directory)

        assert record["component"] == "worker"

    def test_exception_processing(
        self,
        logging_config: LoggingConfig,
        log_directory: Path,
    ) -> None:
        """Render exception information into structured logs."""
        setup_logging(logging_config)

        logger = get_logger("albus.processor")

        try:
            raise RuntimeError("Synthetic test exception")

        except RuntimeError:
            logger.exception("exception_event")

        record = read_last_record(log_directory)

        assert record["event"] == "exception_event"
        assert record.get("exception")

        assert "Synthetic test exception" in json.dumps(
            record["exception"],
        )

    def test_sensitive_data_processing(
        self,
        logging_config: LoggingConfig,
        log_directory: Path,
    ) -> None:
        """Apply sensitive-data redaction to processed events."""
        setup_logging(logging_config)

        get_logger("albus.processor").info(
            "authentication",
            password="fake-processor-password",
        )

        record = read_last_record(log_directory)

        assert "fake-processor-password" not in json.dumps(
            record,
        )
