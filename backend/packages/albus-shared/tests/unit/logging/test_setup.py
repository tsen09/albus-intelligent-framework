
"""Unit and component tests for Albus logging setup."""

import json
import logging
from pathlib import Path

import pytest
import structlog

from albus.shared.logging import (
    LoggingConfig,
    get_logger,
    setup_logging,
)


pytestmark = [
    pytest.mark.unit,
    pytest.mark.logging,
]


def get_owned_handlers() -> list[logging.Handler]:
    """Retrieve handlers managed by Albus."""
    return [
        handler
        for handler in logging.getLogger().handlers
        if getattr(handler, "_albus_owned", False)
    ]


class TestLoggingSetup:
    """Verify logging initialization."""

    def test_setup_returns_none(
        self,
        logging_config: LoggingConfig,
    ) -> None:
        """Initialize logging without returning a value."""
        assert setup_logging(logging_config) is None

    def test_structlog_initialized(
        self,
        logging_config: LoggingConfig,
    ) -> None:
        """Configure the Structlog subsystem."""
        setup_logging(logging_config)

        assert structlog.is_configured()

    def test_root_logger_level(
        self,
        logging_config: LoggingConfig,
    ) -> None:
        """Configure the root logger level."""
        setup_logging(logging_config)

        assert logging.getLogger().level == logging.DEBUG

    def test_handlers_registered(
        self,
        logging_config: LoggingConfig,
    ) -> None:
        """Register Albus-owned logging handlers."""
        setup_logging(logging_config)

        assert get_owned_handlers()

    def test_console_only_handler(self) -> None:
        """Register only the console output handler."""
        config = LoggingConfig(
            console_enabled=True,
            file_enabled=False,
        )

        setup_logging(config)

        assert len(get_owned_handlers()) == 1

    def test_file_only_handler(
        self,
        log_directory: Path,
    ) -> None:
        """Register only the file output handler."""
        config = LoggingConfig(
            console_enabled=False,
            file_enabled=True,
            log_dir=log_directory,
        )

        setup_logging(config)

        assert len(get_owned_handlers()) == 1

    def test_both_output_handlers(
        self,
        logging_config: LoggingConfig,
    ) -> None:
        """Register console and file output handlers."""
        setup_logging(logging_config)

        assert len(get_owned_handlers()) == 2

    def test_setup_from_environment(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Initialize logging using environment settings."""
        monkeypatch.setenv("ALBUS_LOG_LEVEL", "WARNING")
        monkeypatch.setenv(
            "ALBUS_LOG_FILE_ENABLED",
            "false",
        )

        setup_logging()

        assert logging.getLogger().level == logging.WARNING


class TestLoggingReinitialization:
    """Verify safe logging reconfiguration."""

    def test_no_duplicate_handlers(
        self,
        logging_config: LoggingConfig,
    ) -> None:
        """Prevent duplicate handlers after repeated setup."""
        setup_logging(logging_config)

        original_count = len(get_owned_handlers())

        setup_logging(logging_config)
        setup_logging(logging_config)

        assert len(get_owned_handlers()) == original_count

    def test_preserve_external_handlers(
        self,
        logging_config: LoggingConfig,
    ) -> None:
        """Preserve handlers not managed by Albus."""
        root_logger = logging.getLogger()
        external_handler = logging.NullHandler()

        root_logger.addHandler(external_handler)

        try:
            setup_logging(logging_config)

            assert external_handler in root_logger.handlers

        finally:
            root_logger.removeHandler(external_handler)
            external_handler.close()

    def test_reconfigure_log_level(self) -> None:
        """Apply updated logging levels."""
        setup_logging(
            LoggingConfig(
                log_level="DEBUG",
                file_enabled=False,
            )
        )

        assert logging.getLogger().level == logging.DEBUG

        setup_logging(
            LoggingConfig(
                log_level="ERROR",
                file_enabled=False,
            )
        )

        assert logging.getLogger().level == logging.ERROR


class TestLogLevelFiltering:
    """Verify filtering of events below the configured level."""

    def test_debug_events_filtered(
        self,
        log_directory: Path,
    ) -> None:
        """Exclude DEBUG events when the level is INFO."""
        setup_logging(
            LoggingConfig(
                log_level="INFO",
                console_enabled=False,
                file_enabled=True,
                log_dir=log_directory,
            )
        )

        logger = get_logger("albus.filtering")

        logger.debug("excluded_debug_event")
        logger.info("included_info_event")

        content = (
            log_directory / "filtering.log"
        ).read_text(encoding="utf-8")

        assert "excluded_debug_event" not in content
        assert "included_info_event" in content


class TestThirdPartyLogging:
    """Verify third-party logging configuration."""

    @pytest.mark.parametrize(
        "logger_name",
        ["httpx", "httpcore", "PIL", "urllib3"],
    )
    def test_noisy_logger_levels(
        self,
        logging_config: LoggingConfig,
        logger_name: str,
    ) -> None:
        """Restrict noisy third-party logger levels."""
        setup_logging(logging_config)

        assert (
            logging.getLogger(logger_name).level
            == logging.WARNING
        )

    def test_standard_library_integration(
        self,
        logging_config: LoggingConfig,
        log_directory: Path,
    ) -> None:
        """Process ordinary Python logging records."""
        setup_logging(logging_config)

        logger = logging.getLogger("albus.standard")
        logger.info("standard_library_event")

        content = (
            log_directory / "standard.log"
        ).read_text(encoding="utf-8")

        record = json.loads(content.splitlines()[-1])

        assert record["event"] == "standard_library_event"
        assert record["level"] == "info"


class TestConsoleLogging:
    """Verify console rendering."""

    def test_json_console_output(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Render structured JSON to the console."""
        setup_logging(
            LoggingConfig(
                console_enabled=True,
                console_format="json",
                file_enabled=False,
            )
        )

        get_logger("albus.console").info(
            "console_json_event",
        )

        captured = capsys.readouterr()

        output = captured.err or captured.out

        records = [
            json.loads(line)
            for line in output.splitlines()
            if line.strip()
        ]

        assert any(
            record.get("event") == "console_json_event"
            for record in records
        )

    def test_human_readable_console_output(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Render human-readable console output."""
        setup_logging(
            LoggingConfig(
                console_enabled=True,
                console_format="console",
                file_enabled=False,
            )
        )

        get_logger("albus.console").info(
            "console_readable_event",
        )

        captured = capsys.readouterr()

        assert "console_readable_event" in (
            captured.out + captured.err
        )
