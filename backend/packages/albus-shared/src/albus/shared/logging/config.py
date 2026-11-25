"""Validated environment-driven configuration for Albus logging."""
from __future__ import annotations
from pathlib import Path
from typing import Literal, Self
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
ConsoleFormat = Literal["auto", "console", "json"]
RotationWhen = Literal["S", "M", "H", "D", "midnight", "W0", "W1", "W2", "W3", "W4", "W5", "W6"]

class LoggingConfig(BaseSettings):
    """Immutable, validated settings loaded from ALBUS_LOG_* variables."""
    model_config = SettingsConfigDict(
        env_prefix="ALBUS_LOG_",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
        validate_by_name=True,
        validate_by_alias=True,
    )

    log_level: LogLevel = Field("INFO", validation_alias="ALBUS_LOG_LEVEL")
    console_enabled: bool = True
    console_format: ConsoleFormat = "auto"
    file_enabled: bool = True
    log_dir: Path = Field(Path("logs"), validation_alias="ALBUS_LOG_DIRECTORY")
    module_namespace: str = "albus"
    rotation_when: RotationWhen = Field("midnight", validation_alias="ALBUS_LOG_ROTATION")
    rotation_interval: int = Field(1, ge=1)
    retention_days: int = Field(14, ge=0)
    compression: bool = True
    redact_sensitive: bool = True

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_level(cls, value: object) -> object:
        return value.strip().upper() if isinstance(value, str) else value

    @field_validator("console_format", mode="before")
    @classmethod
    def normalize_format(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("module_namespace")
    @classmethod
    def validate_namespace(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("module_namespace cannot be empty")
        return value

    @model_validator(mode="after")
    def validate_handlers(self) -> Self:
        if not self.console_enabled and not self.file_enabled:
            raise ValueError("At least one logging output must be enabled")
        return self

    @classmethod
    def from_env(cls) -> Self:
        """Compatibility factory for existing callers."""
        return cls()
