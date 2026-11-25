
"""
Albus Shared Logging - Smoke Test

Performs standalone operational verification of the Albus logging
subsystem without requiring pytest or external infrastructure.

Usage:
    uv run python packages/albus-shared/tests/smoke/logging/logging_smoke.py

Exit codes:
    0 - All smoke checks passed.
    1 - One or more smoke checks failed.
"""

from __future__ import annotations

import json
import logging
import traceback
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from albus.shared.logging import (
    LoggingConfig,
    bind_contextvars,
    clear_contextvars,
    create_logger,
    get_contextvars,
    get_logger,
    setup_logging,
    unbind_contextvars,
)


# ============================================================================
# Constants
# ============================================================================

REQUEST_ID = "albus-smoke-request-001"
TEST_PASSWORD = "albus-smoke-fake-password-123"


# ============================================================================
# Smoke Test Utilities
# ============================================================================


def print_section(title: str) -> None:
    """Print a formatted smoke test section."""

    print(f"\n{'=' * 72}")
    print(f"  {title}")
    print(f"{'=' * 72}", flush=True)


def check(condition: bool, message: str) -> None:
    """Validate a smoke test condition."""

    if not condition:
        raise AssertionError(message)

    print(f"  [PASS] {message}", flush=True)


def read_log_records(log_file: Path) -> list[dict[str, Any]]:
    """Read structured JSON records from a log file."""

    records: list[dict[str, Any]] = []

    with log_file.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            record = json.loads(line)

            if not isinstance(record, dict):
                raise ValueError(
                    f"Invalid JSON log record in {log_file.name}"
                )

            records.append(record)

    return records


def get_owned_handlers() -> list[logging.Handler]:
    """Return handlers managed by the Albus logging subsystem."""

    return [
        handler
        for handler in logging.getLogger().handlers
        if getattr(handler, "_albus_owned", False)
    ]


def cleanup_logging() -> None:
    """Remove and close Albus-owned logging handlers."""

    clear_contextvars()

    root_logger = logging.getLogger()

    for handler in get_owned_handlers():
        root_logger.removeHandler(handler)

        try:
            handler.flush()
        finally:
            handler.close()


# ============================================================================
# Smoke Test Configuration
# ============================================================================


def build_config(log_directory: Path) -> LoggingConfig:
    """Create an isolated logging configuration for smoke testing."""

    return LoggingConfig(
        log_level="DEBUG",
        console_enabled=True,
        console_format="console",
        file_enabled=True,
        log_dir=log_directory,
        module_namespace="albus",
        rotation_when="midnight",
        rotation_interval=1,
        retention_days=1,
        compression=True,
        redact_sensitive=True,
    )


# ============================================================================
# Logging Smoke Test
# ============================================================================


def run_smoke_test(log_directory: Path) -> None:
    """Execute operational checks against the logging subsystem."""

    # ------------------------------------------------------------------------
    # 1. Configuration
    # ------------------------------------------------------------------------

    print_section("1. Logging Configuration")

    config = build_config(log_directory)

    check(
        isinstance(config, LoggingConfig),
        "Logging configuration initialized successfully",
    )

    check(
        config.log_level == "DEBUG",
        "Logging level configured correctly",
    )

    check(
        config.console_enabled and config.file_enabled,
        "Console and file logging enabled",
    )

    print(
        json.dumps(
            config.model_dump(mode="json"),
            indent=4,
        )
    )

    # ------------------------------------------------------------------------
    # 2. Logging Initialization
    # ------------------------------------------------------------------------

    print_section("2. Logging Initialization")

    setup_logging(config)

    check(
        bool(get_owned_handlers()),
        "Albus logging handlers registered",
    )

    check(
        logging.getLogger().level == logging.DEBUG,
        "Root logger level configured correctly",
    )

    # ------------------------------------------------------------------------
    # 3. Logger Factory
    # ------------------------------------------------------------------------

    print_section("3. Logger Factory")

    logger = get_logger("albus.smoke")
    worker_logger = create_logger("albus.worker", config)

    check(
        logger is not None,
        "get_logger() returned a logger",
    )

    check(
        worker_logger is not None,
        "create_logger() returned a logger",
    )

    # ------------------------------------------------------------------------
    # 4. Logging Levels
    # ------------------------------------------------------------------------

    print_section("4. Logging Levels")

    logger.debug("smoke_debug_event")
    logger.info("smoke_info_event")
    logger.warning("smoke_warning_event")
    logger.error("smoke_error_event")
    logger.critical("smoke_critical_event")

    # ------------------------------------------------------------------------
    # 5. Structured Logging
    # ------------------------------------------------------------------------

    print_section("5. Structured Logging")

    logger.info(
        "smoke_structured_event",
        component="logging",
        operation="smoke_test",
        duration_ms=125,
        success=True,
    )

    # ------------------------------------------------------------------------
    # 6. Module-Based Logging
    # ------------------------------------------------------------------------

    print_section("6. Module-Based File Routing")

    logger.info(
        "smoke_module_event",
        module="smoke",
    )

    worker_logger.info(
        "worker_module_event",
        module="worker",
    )

    # ------------------------------------------------------------------------
    # 7. Context Management
    # ------------------------------------------------------------------------

    print_section("7. Context Management")

    clear_contextvars()

    bind_contextvars(
        request_id=REQUEST_ID,
        environment="testing",
        operation="logging_smoke_test",
    )

    context = get_contextvars()

    check(
        context.get("request_id") == REQUEST_ID,
        "Request context bound successfully",
    )

    logger.info("smoke_context_event")

    unbind_contextvars("operation")

    check(
        "operation" not in get_contextvars(),
        "Individual context variable removed",
    )

    logger.info("smoke_unbound_context_event")

    clear_contextvars()

    check(
        not get_contextvars(),
        "Logging context cleared successfully",
    )

    logger.info("smoke_cleared_context_event")

    # ------------------------------------------------------------------------
    # 8. Sensitive Data Redaction
    # ------------------------------------------------------------------------

    print_section("8. Sensitive Data Redaction")

    logger.info(
        "smoke_redaction_event",
        username="smoke-user",
        password=TEST_PASSWORD,
    )

    # ------------------------------------------------------------------------
    # 9. Exception Logging
    # ------------------------------------------------------------------------

    print_section("9. Exception Logging")

    try:
        raise RuntimeError("Intentional smoke test exception")

    except RuntimeError:
        logger.exception(
            "smoke_exception_event",
            operation="exception_verification",
        )

    # ------------------------------------------------------------------------
    # 10. Standard Library Logging
    # ------------------------------------------------------------------------

    print_section("10. Standard Library Logging")

    standard_logger = logging.getLogger("albus.standard")

    standard_logger.info("smoke_standard_library_event")

    # ------------------------------------------------------------------------
    # 11. Logging Reinitialization
    # ------------------------------------------------------------------------

    print_section("11. Logging Reinitialization")

    initial_handler_count = len(get_owned_handlers())

    setup_logging(config)

    current_handler_count = len(get_owned_handlers())

    check(
        initial_handler_count == current_handler_count,
        "Repeated initialization did not duplicate handlers",
    )

    logger = get_logger("albus.smoke")

    logger.info("smoke_reinitialization_event")

    # ------------------------------------------------------------------------
    # 12. Flush and Close Log Handlers
    # ------------------------------------------------------------------------

    print_section("12. Handler Cleanup")

    cleanup_logging()

    check(
        not get_owned_handlers(),
        "Albus logging handlers closed and removed",
    )

    # ------------------------------------------------------------------------
    # 13. File Creation Verification
    # ------------------------------------------------------------------------

    print_section("13. Log File Verification")

    smoke_file = log_directory / "smoke.log"
    worker_file = log_directory / "worker.log"
    standard_file = log_directory / "standard.log"

    for log_file in (smoke_file, worker_file, standard_file):
        check(
            log_file.is_file(),
            f"{log_file.name} created successfully",
        )

        check(
            log_file.stat().st_size > 0,
            f"{log_file.name} contains log records",
        )

    # ------------------------------------------------------------------------
    # 14. Structured JSON Verification
    # ------------------------------------------------------------------------

    print_section("14. Structured JSON Verification")

    smoke_records = read_log_records(smoke_file)
    worker_records = read_log_records(worker_file)
    standard_records = read_log_records(standard_file)

    check(
        bool(smoke_records),
        "Smoke log contains valid JSON records",
    )

    check(
        bool(worker_records),
        "Worker log contains valid JSON records",
    )

    check(
        bool(standard_records),
        "Standard library log contains valid JSON records",
    )

    events = {
        record.get("event"): record
        for record in smoke_records
    }

    # ------------------------------------------------------------------------
    # 15. Log Level Verification
    # ------------------------------------------------------------------------

    print_section("15. Log Level Verification")

    for level in ("debug", "info", "warning", "error", "critical"):
        event_name = f"smoke_{level}_event"
        record = events.get(event_name, {})

        check(
            record.get("level") == level,
            f"{level.upper()} event recorded correctly",
        )

    # ------------------------------------------------------------------------
    # 16. Structured Metadata Verification
    # ------------------------------------------------------------------------

    print_section("16. Structured Metadata Verification")

    structured_record = events.get(
        "smoke_structured_event",
        {},
    )

    check(
        structured_record.get("component") == "logging",
        "Structured component metadata preserved",
    )

    check(
        structured_record.get("duration_ms") == 125,
        "Numeric metadata preserved",
    )

    check(
        structured_record.get("success") is True,
        "Boolean metadata preserved",
    )

    # ------------------------------------------------------------------------
    # 17. Context Propagation Verification
    # ------------------------------------------------------------------------

    print_section("17. Context Propagation Verification")

    context_record = events.get("smoke_context_event", {})

    check(
        context_record.get("request_id") == REQUEST_ID,
        "Request ID propagated into structured log",
    )

    check(
        context_record.get("environment") == "testing",
        "Environment context propagated into structured log",
    )

    unbound_record = events.get(
        "smoke_unbound_context_event",
        {},
    )

    check(
        bool(unbound_record)
        and "operation" not in unbound_record,
        "Unbound context excluded from subsequent logs",
    )

    cleared_record = events.get(
        "smoke_cleared_context_event",
        {},
    )

    check(
        bool(cleared_record)
        and "request_id" not in cleared_record,
        "Cleared context excluded from subsequent logs",
    )

    # ------------------------------------------------------------------------
    # 18. Sensitive Data Verification
    # ------------------------------------------------------------------------

    print_section("18. Sensitive Data Verification")

    redacted_record = events.get(
        "smoke_redaction_event",
        {},
    )

    check(
        bool(redacted_record),
        "Redaction test event recorded",
    )

    check(
        "password" in redacted_record
        and redacted_record["password"] != TEST_PASSWORD,
        "Password field redacted successfully",
    )

    for log_file in log_directory.rglob("*.log"):
        check(
            TEST_PASSWORD not in log_file.read_text(
                encoding="utf-8"
            ),
            f"No plaintext test password in {log_file.name}",
        )

    # ------------------------------------------------------------------------
    # 19. Exception Verification
    # ------------------------------------------------------------------------

    print_section("19. Exception Verification")

    exception_record = events.get(
        "smoke_exception_event",
        {},
    )

    check(
        bool(exception_record),
        "Exception event recorded successfully",
    )

    check(
        bool(exception_record.get("exception")),
        "Exception traceback included in structured log",
    )

    # ------------------------------------------------------------------------
    # 20. Module Routing Verification
    # ------------------------------------------------------------------------

    print_section("20. Module Routing Verification")

    check(
        any(
            record.get("event") == "worker_module_event"
            for record in worker_records
        ),
        "Worker event routed to worker.log",
    )

    check(
        any(
            record.get("event") == "smoke_standard_library_event"
            for record in standard_records
        ),
        "Standard library event routed to standard.log",
    )

    check(
        not any(
            record.get("event") == "worker_module_event"
            for record in smoke_records
        ),
        "Worker events isolated from smoke.log",
    )

    check(
        sum(
            record.get("event") == "smoke_reinitialization_event"
            for record in smoke_records
        ) == 1,
        "Reinitialization event recorded exactly once",
    )

    # ------------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------------

    print_section("Log File Summary")

    for log_file in sorted(log_directory.rglob("*.log")):
        print(
            f"  {log_file.name:<25}"
            f"{log_file.stat().st_size:>10,} bytes"
        )


# ============================================================================
# Entry Point
# ============================================================================


def main() -> int:
    """Execute the logging smoke test."""

    print_section("ALBUS SHARED - LOGGING SMOKE TEST")

    root_logger = logging.getLogger()
    original_level = root_logger.level

    try:
        with TemporaryDirectory(
            prefix="albus-logging-smoke-"
        ) as temporary_directory:

            log_directory = Path(temporary_directory) / "logs"
            log_directory.mkdir(parents=True, exist_ok=True)

            print(f"\n  Log directory: {log_directory}")

            try:
                run_smoke_test(log_directory)

            finally:
                cleanup_logging()

        print_section("SMOKE TEST PASSED")

        print("  All logging smoke checks completed successfully.")
        print("  Temporary log files removed.")
        print("  Exit code: 0\n")

        return 0

    except Exception:
        print_section("SMOKE TEST FAILED")

        traceback.print_exc()

        print("\n  One or more logging smoke checks failed.")
        print("  Exit code: 1\n")

        return 1

    finally:
        root_logger.setLevel(original_level)


if __name__ == "__main__":
    raise SystemExit(main())
