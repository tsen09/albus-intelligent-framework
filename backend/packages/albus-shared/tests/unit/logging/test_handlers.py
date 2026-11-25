
"""Tests for Albus logging handlers."""

import gzip
import json
import logging
from pathlib import Path

import pytest

from albus.shared.logging import (
    LoggingConfig,
    get_logger,
    setup_logging,
)


pytestmark = [
    pytest.mark.unit,
    pytest.mark.logging,
]


class TestModuleFileRouting:
    """Verify module-based file routing."""

    def test_log_file_creation(
        self,
        logging_config: LoggingConfig,
        log_directory: Path,
    ) -> None:
        """Create a file for a named module."""
        setup_logging(logging_config)

        logger = get_logger("albus.api")
        logger.info("api_started")

        assert (log_directory / "api.log").is_file()

    def test_multiple_module_files(
        self,
        logging_config: LoggingConfig,
        log_directory: Path,
    ) -> None:
        """Route separate modules to separate files."""
        setup_logging(logging_config)

        get_logger("albus.api").info("api_event")
        get_logger("albus.worker").info("worker_event")

        assert (log_directory / "api.log").exists()
        assert (log_directory / "worker.log").exists()

    def test_module_event_isolation(
        self,
        logging_config: LoggingConfig,
        log_directory: Path,
    ) -> None:
        """Prevent events leaking into unrelated module files."""
        setup_logging(logging_config)

        get_logger("albus.api").info("api_event")
        get_logger("albus.worker").info("worker_event")

        api_content = (
            log_directory / "api.log"
        ).read_text(encoding="utf-8")

        worker_content = (
            log_directory / "worker.log"
        ).read_text(encoding="utf-8")

        assert "api_event" in api_content
        assert "worker_event" not in api_content

        assert "worker_event" in worker_content
        assert "api_event" not in worker_content

    def test_external_logger_routing(
        self,
        logging_config: LoggingConfig,
        log_directory: Path,
    ) -> None:
        """Route external logger events to external.log."""
        setup_logging(logging_config)

        logging.getLogger("third_party").info(
            "external_event"
        )

        assert (log_directory / "external.log").exists()

    def test_file_logging_disabled(
        self,
        log_directory: Path,
    ) -> None:
        """Avoid creating files when file logging is disabled."""
        config = LoggingConfig(
            console_enabled=True,
            file_enabled=False,
            log_dir=log_directory,
        )

        setup_logging(config)

        get_logger("albus.api").info("console_only")

        assert not list(log_directory.glob("*.log"))


class TestFileHandlerOutput:
    """Verify file handler output."""

    def test_json_log_output(
        self,
        logging_config: LoggingConfig,
        log_directory: Path,
    ) -> None:
        """Write valid JSON records to log files."""
        setup_logging(logging_config)

        get_logger("albus.api").info(
            "json_event",
            status_code=200,
        )

        content = (
            log_directory / "api.log"
        ).read_text(encoding="utf-8")

        record = json.loads(content.splitlines()[-1])

        assert record["event"] == "json_event"
        assert record["status_code"] == 200

    def test_multiple_events_appended(
        self,
        logging_config: LoggingConfig,
        log_directory: Path,
    ) -> None:
        """Append events without overwriting previous records."""
        setup_logging(logging_config)

        logger = get_logger("albus.api")

        logger.info("first_event")
        logger.info("second_event")
        logger.info("third_event")

        content = (
            log_directory / "api.log"
        ).read_text(encoding="utf-8")

        records = [
            json.loads(line)
            for line in content.splitlines()
            if line.strip()
        ]

        assert len(records) == 3

        assert [
            record["event"]
            for record in records
        ] == [
            "first_event",
            "second_event",
            "third_event",
        ]


class TestFileHandlerLifecycle:
    """Verify file handler lifecycle behaviour."""

    def test_reinitialization_preserves_logs(
        self,
        logging_config: LoggingConfig,
        log_directory: Path,
    ) -> None:
        """Preserve existing log records after reinitialization."""
        setup_logging(logging_config)

        get_logger("albus.api").info("before_setup")

        setup_logging(logging_config)

        get_logger("albus.api").info("after_setup")

        content = (
            log_directory / "api.log"
        ).read_text(encoding="utf-8")

        assert "before_setup" in content
        assert "after_setup" in content

    def test_active_log_is_not_compressed(
        self,
        logging_config: LoggingConfig,
        log_directory: Path,
    ) -> None:
        """Keep active logs uncompressed."""
        setup_logging(logging_config)

        get_logger("albus.api").info("active_event")

        assert (log_directory / "api.log").exists()
        assert not list(log_directory.glob("*.gz"))
