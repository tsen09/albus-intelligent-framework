# Albus Shared Logging

Centralized, structured, environment-driven logging for **Albus**, built on Python's `logging` module, [Structlog](https://www.structlog.org/), **Pydantic v2**, and `pydantic-settings`.

The logging package provides a consistent way for Albus services to emit operational events without each service having to configure its own handlers, formatters, context fields, or file rotation.

> **Scope:** This guide documents the nine Python modules in the `albus.shared.logging` package. It describes the implementation as supplied, including current limitations.

## Table of contents

1. [Features](#features)
2. [How logging works](#how-logging-works)
3. [Package structure](#package-structure)
4. [Installation](#installation)
5. [Quick start](#quick-start)
6. [Configuration reference](#configuration-reference)
7. [Environment-specific TOML configuration](#environment-specific-toml-configuration)
8. [Logger naming and file routing](#logger-naming-and-file-routing)
9. [Formatting and structured events](#formatting-and-structured-events)
10. [Request and workflow context](#request-and-workflow-context)
11. [Sensitive-data redaction](#sensitive-data-redaction)
12. [Rotation, compression and retention](#rotation-compression-and-retention)
13. [Standard-library and third-party logging](#standard-library-and-third-party-logging)
14. [FastAPI integration](#fastapi-integration)
15. [Testing](#testing)
16. [Troubleshooting](#troubleshooting)
17. [Production considerations](#production-considerations)
18. [API reference](#api-reference)

---

## Features

- **Structured logging:** Structlog event dictionaries with optional key/value fields.
- **Pydantic v2 settings:** typed, validated, immutable configuration sourced from `ALBUS_LOG_*` environment variables.
- **Two output types:** console and module-specific files, independently enabled.
- **Console rendering:** human-readable console or JSON; `auto` selects based on environment and TTY detection.
- **File rendering:** JSON output for file logs.
- **Module routing:** logger names determine which file receives each event.
- **Timed rotation:** second, minute, hour, day, midnight or weekday schedules.
- **Optional gzip:** rotated files can be compressed.
- **Age-based retention:** cleanup of rotated files older than the configured window.
- **Context variables:** attach request or workflow metadata to events in the current execution context.
- **Best-effort redaction:** masks selected sensitive keys and recognizable credential patterns.
- **Standard-library integration:** supports events emitted through `logging.getLogger(...)`.
- **Controlled reinitialization:** removes only handlers marked as owned by Albus.

## How logging works

```text
backend/config/{ENV}.toml
          |
          | scripts/run.sh reads TOML and exports ALBUS_LOG_* variables
          v
LoggingConfig.from_env()           [config.py]
          |
          | Pydantic parses, normalizes and validates
          v
setup_logging(config)              [setup.py]
          |
          +--> structlog configuration
          |
          +--> console handler --> console or JSON renderer
          |
          +--> ModuleFileRouter --> per-module rotating file handler
          |
          +--> third-party logger level adjustments

Application code
    |
    +--> get_logger("albus.api") --> structured event
    |                                  |
    +--> logging.getLogger(...) ------+
                                       |
                                       v
                             processors / context
                                       |
                                       v
                           formatter / redaction
                                       |
                                       v
                             console and/or files
```

**Two distinct operations matter:**

1. `setup_logging(...)` configures the logging system. Call it once during application startup, before you rely on log output.
2. `get_logger(...)` retrieves a logger for a module or service. It does **not** create handlers or reload settings.

`create_logger(name, config)` is also available. It checks the supplied configuration type and logger name, then returns a Structlog logger. **It does not initialize logging**; call `setup_logging(config)` first.

## Package structure

```text
packages/
└── albus-shared/
    ├── pyproject.toml
    └── src/
        └── albus/
            └── shared/
                └── logging/
                    ├── __init__.py
                    ├── config.py
                    ├── context.py
                    ├── factory.py
                    ├── filters.py
                    ├── handlers.py
                    ├── logging.py
                    ├── processors.py
                    └── setup.py
```

| File | Responsibility |
| --- | --- |
| `config.py` | `LoggingConfig`, field validation, environment parsing |
| `context.py` | Bind, read, unbind and clear context variables |
| `factory.py` | `get_logger()` and `create_logger()` |
| `filters.py` | Sensitive key and credential-pattern redaction |
| `handlers.py` | Module-based file routing, timed rotation, gzip and cleanup |
| `logging.py` | Compatibility re-exports of public logging functions |
| `processors.py` | Structlog processor chains and event metadata |
| `setup.py` | Main initialization, formatter creation and handler installation |
| `__init__.py` | Public package imports |

## Installation

The shared package must be importable in the application's Python environment. Install it using the project’s existing package management strategy; for a local editable installation, one possible command from the repository root is:

```bash
uv pip install -e packages/albus-shared
```

The environment must include:

```bash
uv pip install "pydantic>=2" "pydantic-settings>=2" structlog
```

These commands assume `uv` is installed and the desired virtual environment is active or selected. If your `pyproject.toml` already declares these dependencies, install through the normal project sync workflow instead.

> This module does not read TOML directly. The Albus startup script reads the selected TOML file and exports environment variables before the Python application starts.

## Quick start

### 1. Initialize once

```python
from albus.shared.logging import LoggingConfig, setup_logging

config = LoggingConfig.from_env()
setup_logging(config)
```

`LoggingConfig()` and `LoggingConfig.from_env()` both load the environment. The class is frozen, so configuration fields cannot be reassigned after creation.

### 2. Retrieve a logger

```python
from albus.shared.logging import get_logger

logger = get_logger("albus.api")

logger.info("Application started", version="0.1.0")
logger.warning("Request took longer than expected", elapsed_ms=820)
logger.error("Operation failed", operation="sync")
```

Use stable, descriptive event messages and pass metadata as keyword arguments. Avoid concatenating identifiers or secret values into free-text messages.

### 3. Inject configuration explicitly

```python
from albus.shared.logging import LoggingConfig, create_logger, setup_logging

config = LoggingConfig(
    log_level="DEBUG",
    console_enabled=True,
    file_enabled=False,
)

setup_logging(config)
logger = create_logger("albus.worker", config)
logger.debug("Worker ready", queue="default")
```

`BaseSettings` can still read environment values for fields not explicitly supplied.

## Configuration reference

The fields below are the **actual fields supported by the supplied `LoggingConfig`**.

| Python field | Environment variable | Default | Meaning |
| --- | --- | --- | --- |
| `log_level` | `ALBUS_LOG_LEVEL` | `INFO` | Minimum root logger level |
| `console_enabled` | `ALBUS_LOG_CONSOLE_ENABLED` | `true` | Install console handler |
| `console_format` | `ALBUS_LOG_CONSOLE_FORMAT` | `auto` | `auto`, `console` or `json` |
| `file_enabled` | `ALBUS_LOG_FILE_ENABLED` | `true` | Install module file router |
| `log_dir` | `ALBUS_LOG_DIRECTORY` | `logs` | Directory for log files |
| `module_namespace` | `ALBUS_LOG_MODULE_NAMESPACE` | `albus` | Logger namespace used for file routing |
| `rotation_when` | `ALBUS_LOG_ROTATION` | `midnight` | Timed rotation unit |
| `rotation_interval` | `ALBUS_LOG_ROTATION_INTERVAL` | `1` | Number of rotation units |
| `retention_days` | `ALBUS_LOG_RETENTION_DAYS` | `14` | Age threshold for rotated files; `0` disables age cleanup |
| `compression` | `ALBUS_LOG_COMPRESSION` | `true` | Gzip rotated files |
| `redact_sensitive` | `ALBUS_LOG_REDACT_SENSITIVE` | `true` | Enable redaction processor |

### Validation rules

- Levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`; input is normalized to uppercase.
- Console formats: `auto`, `console`, `json`; input is normalized to lowercase.
- Rotation units: `S`, `M`, `H`, `D`, `midnight`, `W0`–`W6`.
- Rotation interval: integer **at least 1**.
- Retention days: integer **at least 0**.
- Namespace: must contain non-whitespace text.
- At least one of console and file logging must be enabled.
- Pydantic parses supported boolean strings such as `true` and `false`.

Invalid settings raise Pydantic validation errors during initialization.

### Example environment variables

```bash
export ALBUS_LOG_LEVEL=DEBUG
export ALBUS_LOG_CONSOLE_ENABLED=true
export ALBUS_LOG_CONSOLE_FORMAT=console
export ALBUS_LOG_FILE_ENABLED=true
export ALBUS_LOG_DIRECTORY=logs
export ALBUS_LOG_MODULE_NAMESPACE=albus
export ALBUS_LOG_ROTATION=midnight
export ALBUS_LOG_ROTATION_INTERVAL=1
export ALBUS_LOG_RETENTION_DAYS=14
export ALBUS_LOG_COMPRESSION=true
export ALBUS_LOG_REDACT_SENSITIVE=true
```

**Precedence:** Explicit values passed to `LoggingConfig(...)` take precedence over corresponding environment values. The `run.sh` version supplied earlier exports TOML values into the process environment, so those become the effective settings when you call `LoggingConfig.from_env()`.

## Environment-specific TOML configuration

The existing startup design selects an environment using `ENV` in the root `.env` file:

```dotenv
ENV=development
```

The startup script selects `backend/config/development.toml`, `testing.toml`, `staging.toml` or `production.toml`, then exports logging values.

### Development

```toml
[logging]
level = "INFO"
console_enabled = true
console_format = "auto"
file_enabled = true
directory = "logs"
module_namespace = "albus"
rotation = "midnight"
rotation_interval = 1
retention_days = 14
compression = true
redact_sensitive = true
```

### Testing

```toml
[logging]
level = "DEBUG"
console_enabled = true
console_format = "console"
file_enabled = true
directory = "logs"
module_namespace = "albus"
rotation = "midnight"
rotation_interval = 1
retention_days = 3
compression = false
redact_sensitive = true
```

### Staging

```toml
[logging]
level = "INFO"
console_enabled = true
console_format = "json"
file_enabled = true
directory = "logs"
module_namespace = "albus"
rotation = "midnight"
rotation_interval = 1
retention_days = 14
compression = true
redact_sensitive = true
```

### Production

```toml
[logging]
level = "INFO"
console_enabled = true
console_format = "json"
file_enabled = true
directory = "logs"
module_namespace = "albus"
rotation = "midnight"
rotation_interval = 1
retention_days = 30
compression = true
redact_sensitive = true
```

These are **recommended example policies**, not hard-coded environment behavior. You may choose `WARNING` for a quieter production environment; the application simply uses the exported level.

## Logger naming and file routing

`ModuleFileRouter` routes log records according to their logger name. The default namespace is `albus`.

| Logger name | File |
| --- | --- |
| `albus` | `logs/core.log` |
| `albus.api` | `logs/api.log` |
| `albus.database` | `logs/database.log` |
| `albus.agents.planner` | `logs/agents_planner.log` |
| `uvicorn.error` | `logs/external.log` |
| `other.package` | `logs/external.log` |

The router strips the namespace prefix and replaces characters outside `[A-Za-z0-9_-]` with underscores. All names outside the configured namespace share `external.log`.

```python
api_logger = get_logger("albus.api")
db_logger = get_logger("albus.database")

api_logger.info("Request received", method="GET")
db_logger.info("Database connection established")
```

The resulting files are based on **logger names**, not automatic discovery of Python source-file paths. Use `get_logger(__name__)` only if your module import names align with the configured namespace; otherwise choose explicit `albus.*` names.

The log directory is a `Path`. Relative paths are resolved against the process working directory. The Albus `run.sh` shown previously changes to `backend/` before launching Uvicorn, so `directory = "logs"` normally means `backend/logs/` in that startup flow.

## Formatting and structured events

### Console output

- `console`: Structlog's human-readable `ConsoleRenderer` with colors enabled.
- `json`: Structlog's `JSONRenderer`.
- `auto`: chooses `json` in `production` (or `prod`), or when standard error is not a TTY; otherwise chooses `console`.

The `auto` resolver checks `ALBUS_ENV`, then `ENV`, then defaults to `development`. Explicit `console` or `json` overrides this selection.

Console logs are written to **standard error**, not standard output.

### File output

File logging always uses JSON rendering in the supplied implementation, regardless of `console_format`.

Illustrative JSON event (actual fields depend on the logger, callsite and event):

```json
{
  "event": "Request completed",
  "status_code": 200,
  "elapsed_ms": 42,
  "logger": "albus.api",
  "level": "info",
  "timestamp": "2026-11-23T08:00:00Z"
}
```

### Processing pipeline

`processors.py` configures two main paths:

**Structlog events**

1. Merge context variables.
2. Add logger name.
3. Add severity.
4. Render stack information.
5. Add callsite metadata.
6. Wrap for `ProcessorFormatter`.

**Standard-library events**

1. Merge context variables.
2. Add logger name and severity.
3. Add `logging` extra fields.
4. Add callsite metadata.

The final formatter removes internal processor metadata, adds an ISO UTC timestamp, optionally redacts sensitive values, converts exception information into structured tracebacks, and renders console text or JSON.

Callsite fields include filename, function, line number, module, pathname, process, process name, thread and thread name. These add useful diagnostics but can increase log volume.

## Request and workflow context

`context.py` uses Structlog context variables, which are useful for associating events within asynchronous request and workflow execution.

```python
from albus.shared.logging import (
    bind_contextvars,
    clear_contextvars,
    get_contextvars,
    unbind_contextvars,
    get_logger,
)

logger = get_logger("albus.workflow")

clear_contextvars()
bind_contextvars(
    request_id="req-123",
    workflow_id="wf-456",
)

logger.info("Workflow started", step="planning")

print(get_contextvars())

unbind_contextvars("workflow_id")
logger.info("Workflow finished")

clear_contextvars()
```

**Best practice:** Clear context at the start and end of each request to avoid carrying stale metadata into reused execution contexts. Do not bind passwords, raw access tokens or other secrets.

Context variables generally follow Python's async context propagation, but thread pools and external task queues may need explicit context propagation.

## Sensitive-data redaction

When `redact_sensitive = true`, the final formatting pipeline invokes `redact_sensitive_data`.

It recursively examines dictionaries, lists and tuples and masks known sensitive dictionary keys such as:

`password`, `passwd`, `secret`, `token`, `access_token`, `refresh_token`, `api_key`, `apikey`, `authorization`, `credentials`, `credential`, `private_key`, `client_secret`, `database_url`, and `connection_string`.

It also searches string values for recognizable `key=value` or `key: value` credential patterns and bearer tokens.

```python
logger.info(
    "Login attempt",
    username="example-user",
    password="do-not-log-this",
)
```

The `password` field is rendered as `[REDACTED]` when redaction is enabled.

**Security limitations:**

- Redaction is **best-effort**, not a guarantee that every secret is removed.
- Unknown field names and unusual credential formats may not match.
- Do not log credentials in the first place.
- The redaction processor runs at formatting time; another handler or external consumer receiving raw records may still see unredacted data.
- The setting can currently be disabled, so deployment policy must enforce it where necessary.

## Rotation, compression and retention

`handlers.py` provides:

- `GzipTimedRotatingFileHandler`: extends `TimedRotatingFileHandler`.
- `ModuleFileRouter`: creates and caches a rotating handler for each resolved module file.

### Rotation settings

| Value | Meaning |
| --- | --- |
| `S` | Seconds |
| `M` | Minutes |
| `H` | Hours |
| `D` | Days |
| `midnight` | Midnight rotation |
| `W0`–`W6` | Weekly rotation on Monday–Sunday |

`rotation_interval` specifies the interval for the selected rotation mode. The file handler is configured with `utc=True`, so scheduled rotation uses UTC rather than the local timezone.

### Compression

When enabled, rotated files receive a `.gz` suffix and are compressed using Python's `gzip` module.

Illustrative directory:

```text
logs/
├── api.log
├── api.log.2026-11-22.gz
├── database.log
├── database.log.2026-11-22.gz
└── external.log
```

The current active `.log` file remains uncompressed.

### Retention

The implementation overrides `getFilesToDelete()` to identify rotated files older than `retention_days`. A value of `0` means no age-based deletion.

**Important implementation caveat:** The supplied cleanup function interprets filename timestamps as UTC and recognizes only certain date/time suffix patterns. Standard `TimedRotatingFileHandler` suffixes and the chosen rotation mode must be tested together, especially for hourly, minutely and weekly schedules. The cleanup is performed during rollover, not by a separate background cleanup service. The supplied code should be verified with real rollover tests before relying on strict retention guarantees.

**Multi-process caveat:** Standard `TimedRotatingFileHandler` is not designed for multiple independent processes writing and rotating the same file concurrently. For multi-worker deployments, consider JSON console logging plus a centralized collector, or a process-safe logging architecture.

## Standard-library and third-party logging

The root logger receives Albus-owned handlers, so conventional Python logging records can also flow through the configured formatters:

```python
import logging

logger = logging.getLogger("albus.integration")
logger.info("Integration initialized")
```

The setup function explicitly raises the minimum level of these noisy third-party logger namespaces to `WARNING`:

- `httpx`
- `httpcore`
- `PIL`
- `urllib3`

This is separate from the global `ALBUS_LOG_LEVEL` setting. For example, setting Albus to `DEBUG` does not automatically enable `httpx` debug logs.

`setup_logging()` removes and closes only handlers carrying its `_albus_owned` marker, rather than removing all root handlers. However, it **does change the root logger level**, and repeated setup reconfigures global Structlog behavior. Treat it as an application-wide initialization operation.

## FastAPI integration

Initialize the logging system once before normal application traffic:

```python
from fastapi import FastAPI

from albus.shared.logging import (
    LoggingConfig,
    get_logger,
    setup_logging,
)

logging_config = LoggingConfig.from_env()
setup_logging(logging_config)

logger = get_logger("albus.api")

app = FastAPI(title="Albus")


@app.get("/")
async def home():
    logger.info("Home endpoint accessed", route="/")
    return {"message": "Welcome to Albus"}
```

### Optional request context middleware

```python
from uuid import uuid4

from fastapi import Request
from albus.shared.logging import (
    bind_contextvars,
    clear_contextvars,
    get_logger,
)

request_logger = get_logger("albus.http")


@app.middleware("http")
async def request_logging(request: Request, call_next):
    clear_contextvars()
    request_id = request.headers.get("x-request-id") or str(uuid4())

    bind_contextvars(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
    )

    try:
        response = await call_next(request)
        request_logger.info(
            "HTTP request completed",
            status_code=response.status_code,
        )
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        clear_contextvars()
```

This is an integration example, not middleware already included in the logging package. In externally exposed systems, validate or replace untrusted incoming request IDs before using them for correlation.

### Exception logging

```python
try:
    raise RuntimeError("Example failure")
except RuntimeError:
    logger.exception("Operation failed", operation="example")
```

The processor chain includes structured traceback rendering. Be careful: exception messages can themselves contain sensitive values.

## Testing

Tests should inject an explicit configuration rather than depend on the developer's shell.

```python
from albus.shared.logging import LoggingConfig, setup_logging, get_logger


def test_logger_initialization():
    config = LoggingConfig(
        log_level="DEBUG",
        console_enabled=True,
        file_enabled=False,
        console_format="json",
    )

    setup_logging(config)
    logger = get_logger("albus.test")
    logger.info("Test event", passed=True)
```

This is a smoke-test example, not a full assertion-based test. Because `BaseSettings` reads environment variables for unspecified fields, tests should control or clear relevant `ALBUS_LOG_*` variables.

### Recommended test coverage

- Valid and invalid log levels.
- Boolean parsing and default settings.
- Console format selection with and without a TTY.
- JSON event shape and expected context fields.
- Sensitive-key and bearer-token redaction.
- Namespace-to-filename routing.
- Repeated `setup_logging()` calls without duplicate Albus handlers.
- Gzip compression after rotation.
- Retention at 0, 1 and 14 days.
- UTC midnight and hourly rotation.
- Standard-library logging integration.
- Concurrent requests and context isolation.
- Multi-worker file logging behavior, if supported by the deployment architecture.

For file tests, use a temporary directory and close managed handlers after the test. Avoid modifying the shared root logger concurrently from multiple tests.

## Troubleshooting

| Symptom | Likely cause | What to check |
| --- | --- | --- |
| No log output | Setup not called or level too high | Call `setup_logging()` before retrieving/using loggers |
| Pydantic validation error | Invalid environment value | Check `ALBUS_LOG_*` exports and allowed values |
| Console shows JSON locally | `auto` sees a non-TTY stderr | Set `console_format="console"` explicitly |
| No log files | File logging disabled or wrong working directory | Check `ALBUS_LOG_FILE_ENABLED` and `ALBUS_LOG_DIRECTORY` |
| Events go to `external.log` | Logger name outside namespace | Use names beginning with `albus.` |
| Duplicate output | Other root handlers are installed | Inspect root handlers and application logging configuration |
| Old files not removed | No rollover or suffix mismatch | Test actual rollover and cleanup behavior |
| Unexpectedly missing HTTP client debug events | Third-party logger suppression | Inspect `httpx` / `httpcore` levels |
| Secrets visible in logs | Redaction disabled or pattern not recognized | Review log fields and redaction tests |
| Files collide across workers | Multiple processes use same log path | Prefer centralized stdout/stderr collection |

### Inspect effective configuration

```python
from albus.shared.logging import LoggingConfig

config = LoggingConfig.from_env()
print(config.model_dump(mode="json"))
```

Only print logging settings you are comfortable exposing; do not generalize this practice to configuration objects containing credentials.

### Inspect root handlers

```python
import logging

for handler in logging.getLogger().handlers:
    print(type(handler).__name__, handler.level)
```

## Production considerations

Before deploying this implementation to production:

1. **Choose an output strategy.** For containerized or multi-worker services, structured console output with external collection is generally safer than multiple processes sharing rotating files.
2. **Enforce redaction.** Keep it enabled and test real-world secret patterns.
3. **Test rotation and retention.** Do not treat the configured day count as proof of a storage retention guarantee.
4. **Control disk permissions and capacity.** Restrict access to log directories and monitor growth.
5. **Avoid logging sensitive payloads.** Prefer event names, safe identifiers and bounded metadata.
6. **Consider request correlation.** Use context variables and validated request IDs.
7. **Avoid logging overload.** `DEBUG` and detailed callsite metadata can increase volume and processing cost.
8. **Initialize once per process.** Logging configuration is global process state.
9. **Define operational retention separately.** Local file cleanup is not a substitute for compliance-driven retention and deletion policies.

## API reference

### Configuration

```python
LoggingConfig(...)
LoggingConfig.from_env()
```

`LoggingConfig` is a frozen `BaseSettings` subclass. `from_env()` returns a validated instance.

### Initialization

```python
setup_logging(config: LoggingConfig | None = None) -> None
```

Initializes Structlog, root handlers, console/file formatting and third-party logger levels. It returns `None`.

### Logger retrieval

```python
get_logger(name: str | None = None)
create_logger(name: str, config: LoggingConfig)
```

Both return Structlog loggers. `create_logger()` checks the configuration type and rejects blank logger names; neither function configures handlers.

### Context

```python
bind_contextvars(**values) -> None
clear_contextvars() -> None
unbind_contextvars(*keys: str) -> None
get_contextvars() -> dict[str, Any]
```

These functions manage contextual fields in the current execution context.

### Internal components

- `ModuleFileRouter`: routes standard-library records to per-module files.
- `GzipTimedRotatingFileHandler`: timed rotation and optional gzip.
- `redact_sensitive_data`: Structlog redaction processor.
- `get_structlog_processors`: Structlog event processor chain.
- `get_foreign_pre_chain`: processor chain for ordinary Python logging records.
- `get_formatter_processors`: final formatting and redaction processors.

Internal components can be tested independently but are not exported by the package's `__init__.py`.

---

## Recommended usage pattern

At application startup:

```python
config = LoggingConfig.from_env()
setup_logging(config)
```

In each module:

```python
logger = get_logger("albus.<module>")
logger.info("Meaningful event", key="safe-value")
```

At request boundaries, bind and clear context. Let the shared logging subsystem handle rendering, routing, redaction, rotation and compression.

**Design principle:** Application code should describe *what happened*. The shared logging subsystem decides *how and where it is recorded*.
