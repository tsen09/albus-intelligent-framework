
"""Unit tests for the Albus logging configuration."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from albus.shared.logging import LoggingConfig


pytestmark = [
    pytest.mark.unit,
    pytest.mark.logging,
]


class TestLoggingConfigDefaults:
    """Verify default logging configuration values."""

    def test_default_log_level(self) -> None:
        """Verify the default logging level."""
        assert LoggingConfig().log_level == "INFO"

    def test_default_console_enabled(self) -> None:
        """Verify console logging is enabled by default."""
        assert LoggingConfig().console_enabled is True

    def test_default_console_format(self) -> None:
        """Verify automatic console formatting."""
        assert LoggingConfig().console_format == "auto"

    def test_default_file_enabled(self) -> None:
        """Verify file logging is enabled by default."""
        assert LoggingConfig().file_enabled is True

    def test_default_log_directory(self) -> None:
        """Verify the default log directory."""
        assert LoggingConfig().log_dir == Path("logs")

    def test_default_namespace(self) -> None:
        """Verify the default module namespace."""
        assert LoggingConfig().module_namespace == "albus"

    def test_default_rotation(self) -> None:
        """Verify default rotation settings."""
        config = LoggingConfig()

        assert config.rotation_when == "midnight"
        assert config.rotation_interval == 1

    def test_default_retention(self) -> None:
        """Verify default retention settings."""
        assert LoggingConfig().retention_days == 14

    def test_default_compression(self) -> None:
        """Verify compression is enabled by default."""
        assert LoggingConfig().compression is True

    def test_default_redaction(self) -> None:
        """Verify sensitive-data redaction is enabled."""
        assert LoggingConfig().redact_sensitive is True


class TestLoggingConfigValidation:
    """Verify configuration validation and normalization."""

    @pytest.mark.parametrize(
        "level",
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    def test_valid_log_levels(self, level: str) -> None:
        """Accept all supported logging levels."""
        config = LoggingConfig(log_level=level)

        assert config.log_level == level

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("debug", "DEBUG"),
            ("info", "INFO"),
            ("Warning", "WARNING"),
            ("error", "ERROR"),
        ],
    )
    def test_log_level_normalization(
        self,
        value: str,
        expected: str,
    ) -> None:
        """Normalize logging levels to uppercase."""
        assert LoggingConfig(log_level=value).log_level == expected

    @pytest.mark.parametrize(
        "level",
        ["INVALID", "TRACE", "", "123"],
    )
    def test_invalid_log_levels(self, level: str) -> None:
        """Reject unsupported logging levels."""
        with pytest.raises(ValidationError):
            LoggingConfig(log_level=level)

    @pytest.mark.parametrize(
        "console_format",
        ["auto", "console", "json"],
    )
    def test_valid_console_formats(
        self,
        console_format: str,
    ) -> None:
        """Accept supported console formats."""
        config = LoggingConfig(
            console_format=console_format,
        )

        assert config.console_format == console_format

    def test_invalid_console_format(self) -> None:
        """Reject unsupported console formats."""
        with pytest.raises(ValidationError):
            LoggingConfig(console_format="xml")

    @pytest.mark.parametrize(
        "rotation",
        [
            "S",
            "M",
            "H",
            "D",
            "midnight",
            "W0",
            "W1",
            "W2",
            "W3",
            "W4",
            "W5",
            "W6",
        ],
    )
    def test_valid_rotation_values(
        self,
        rotation: str,
    ) -> None:
        """Accept supported timed rotation values."""
        config = LoggingConfig(rotation_when=rotation)

        assert config.rotation_when == rotation

    @pytest.mark.parametrize(
        "rotation",
        ["INVALID", "W7", ""],
    )
    def test_invalid_rotation_values(
        self,
        rotation: str,
    ) -> None:
        """Reject invalid rotation schedules."""
        with pytest.raises(ValidationError):
            LoggingConfig(rotation_when=rotation)

    @pytest.mark.parametrize("interval", [0, -1, -10])
    def test_invalid_rotation_interval(
        self,
        interval: int,
    ) -> None:
        """Reject non-positive rotation intervals."""
        with pytest.raises(ValidationError):
            LoggingConfig(rotation_interval=interval)

    @pytest.mark.parametrize("days", [0, 1, 7, 14, 30])
    def test_valid_retention_days(self, days: int) -> None:
        """Accept non-negative retention periods."""
        assert LoggingConfig(retention_days=days).retention_days == days

    def test_negative_retention_days(self) -> None:
        """Reject negative retention periods."""
        with pytest.raises(ValidationError):
            LoggingConfig(retention_days=-1)

    def test_empty_namespace(self) -> None:
        """Reject an empty module namespace."""
        with pytest.raises(ValidationError):
            LoggingConfig(module_namespace="")

    def test_whitespace_namespace(self) -> None:
        """Reject a whitespace-only namespace."""
        with pytest.raises(ValidationError):
            LoggingConfig(module_namespace="   ")

    def test_both_outputs_disabled(self) -> None:
        """Reject configurations without any logging output."""
        with pytest.raises(ValidationError):
            LoggingConfig(
                console_enabled=False,
                file_enabled=False,
            )

    def test_console_only_configuration(self) -> None:
        """Allow console-only logging."""
        config = LoggingConfig(
            console_enabled=True,
            file_enabled=False,
        )

        assert config.console_enabled is True
        assert config.file_enabled is False

    def test_file_only_configuration(self) -> None:
        """Allow file-only logging."""
        config = LoggingConfig(
            console_enabled=False,
            file_enabled=True,
        )

        assert config.console_enabled is False
        assert config.file_enabled is True

    def test_configuration_is_immutable(self) -> None:
        """Prevent mutation of validated configuration."""
        config = LoggingConfig()

        with pytest.raises(ValidationError):
            setattr(config, "log_level", "DEBUG")


class TestLoggingConfigEnvironment:
    """Verify environment-driven configuration."""

    def test_log_level_from_environment(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Load the logging level from environment variables."""
        monkeypatch.setenv("ALBUS_LOG_LEVEL", "ERROR")

        assert LoggingConfig.from_env().log_level == "ERROR"

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("true", True),
            ("false", False),
            ("1", True),
            ("0", False),
        ],
    )
    def test_boolean_environment_parsing(
        self,
        monkeypatch: pytest.MonkeyPatch,
        value: str,
        expected: bool,
    ) -> None:
        """Parse boolean environment values."""
        monkeypatch.setenv(
            "ALBUS_LOG_COMPRESSION",
            value,
        )

        assert LoggingConfig.from_env().compression is expected

    def test_directory_from_environment(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """Load the log directory from the environment."""
        monkeypatch.setenv(
            "ALBUS_LOG_DIRECTORY",
            str(tmp_path),
        )

        assert LoggingConfig.from_env().log_dir == tmp_path

    def test_retention_from_environment(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Parse integer retention settings."""
        monkeypatch.setenv(
            "ALBUS_LOG_RETENTION_DAYS",
            "30",
        )

        assert LoggingConfig.from_env().retention_days == 30

    def test_invalid_environment_value(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Reject invalid environment configuration."""
        monkeypatch.setenv(
            "ALBUS_LOG_LEVEL",
            "INVALID",
        )

        with pytest.raises(ValidationError):
            LoggingConfig.from_env()


class TestLoggingConfigRegression:
    """Prevent previously identified configuration regressions."""

    def test_explicit_field_name_initialization(self) -> None:
        """Accept explicit Python field names."""
        config = LoggingConfig(log_level="DEBUG")

        assert config.log_level == "DEBUG"

    def test_explicit_values_override_environment(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Give explicit settings precedence over environment."""
        monkeypatch.setenv("ALBUS_LOG_LEVEL", "ERROR")

        config = LoggingConfig(log_level="DEBUG")

        assert config.log_level == "DEBUG"

    def test_explicit_directory_override(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """Prevent environment settings overriding test paths."""
        monkeypatch.setenv(
            "ALBUS_LOG_DIRECTORY",
            "/unexpected/logs",
        )

        config = LoggingConfig(log_dir=tmp_path)

        assert config.log_dir == tmp_path

    def test_configuration_serialization(self) -> None:
        """Serialize configuration into JSON-compatible values."""
        config = LoggingConfig(log_level="DEBUG")

        data = config.model_dump(mode="json")

        assert data["log_level"] == "DEBUG"
        assert isinstance(data["log_dir"], str)
