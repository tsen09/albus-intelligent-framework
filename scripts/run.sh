#!/usr/bin/env bash

set -Eeuo pipefail

# ============================================================================
# Albus - Intelligent Personal Butler
# Application Startup Script
# ============================================================================

# ----------------------------------------------------------------------------
# Project Paths
# ----------------------------------------------------------------------------

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

SCRIPTS_DIR="$PROJECT_ROOT/scripts"
CONFIG_DIR="$PROJECT_ROOT/backend/config"

ENV_FILE="$PROJECT_ROOT/.env"
SETUP_SCRIPT="$SCRIPTS_DIR/setup.sh"

VENV_DIR="$PROJECT_ROOT/backend/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"

# ----------------------------------------------------------------------------
# Shared Terminal Utilities
# ----------------------------------------------------------------------------

source "$SCRIPTS_DIR/lib/common.sh"

# ============================================================================
# Environment Validation & Setup
# ============================================================================

is_setup_complete() {
    [[ -x "$VENV_PYTHON" ]] &&
        "$VENV_PYTHON" -c "import uvicorn" &>/dev/null
}

confirm_setup() {

    printf '\n'
    printf '%bSETUP REQUIRED%b\n' "$YELLOW" "$RESET"
    printf '  Albus has not been set up yet.\n'
    printf '  You need to configure the project environment before launching it.\n\n'

    if [[ ! -t 0 ]]; then
        log_error "Setup required. Run './albus.sh setup' first."
        exit 1
    fi

    read -r -p "  Would you like to set up Albus now? [y/N]: " response

    case "$response" in
        [yY]|[yY][eE][sS])
            printf '\n'
            log_info "Starting Albus setup..."
            ;;

        *)
            printf '\n'
            log_info "Startup cancelled. Run './albus.sh setup' when ready."
            exit 0
            ;;
    esac
}

ensure_setup() {

    if is_setup_complete; then
        log_success "Project environment is ready."
        return 0
    fi

    confirm_setup

    if [[ ! -f "$SETUP_SCRIPT" ]]; then
        log_error "Setup script not found: $SETUP_SCRIPT"
        exit 1
    fi

    bash "$SETUP_SCRIPT"

    printf '\n'

    if ! is_setup_complete; then
        log_error "Albus setup did not complete successfully."
        log_error "Please check the setup logs and try again."
        exit 1
    fi

    log_success "Project environment is ready."
}

# ============================================================================
# Configuration Loading
# ============================================================================

load_toml_exports() {

    local toml_file="$1"

    "$VENV_PYTHON" - "$toml_file" <<'PY'
import shlex
import sys
import tomllib

with open(sys.argv[1], "rb") as f:
    data = tomllib.load(f)

# ------------------------------------------------------------------------
# Configuration Sections
# ------------------------------------------------------------------------

app = data.get("application", data.get("app", {}))
db = data.get("database", {})
py = data.get("python", {})
logging = data.get("logging", {})

# ------------------------------------------------------------------------
# Configuration Exports
# ------------------------------------------------------------------------

exports = {

    # Application Configuration
    "ALBUS_APP_MODULE": app.get("module"),
    "APP_NAME": app.get("name"),
    "APP_DEBUG": app.get("debug"),
    "ALBUS_HOST": app.get("host"),
    "ALBUS_PORT": app.get("port"),

    # Database Configuration
    "DB_DRIVER": db.get("driver"),
    "DB_HOST": db.get("host"),
    "DB_PORT": db.get("port"),
    "DB_NAME": db.get("name"),
    "DB_POOL_SIZE": db.get("pool_size"),
    "DB_MAX_OVERFLOW": db.get("max_overflow"),

    # Python Configuration
    "PYTHONUNBUFFERED": py.get("unbuffered"),
    "PYTHONDONTWRITEBYTECODE": py.get("dont_write_bytecode"),

    # Logging Configuration
    "ALBUS_LOG_LEVEL": logging.get("level"),
    "ALBUS_LOG_CONSOLE_ENABLED": logging.get("console_enabled"),
    "ALBUS_LOG_CONSOLE_FORMAT": logging.get("console_format"),

    "ALBUS_LOG_FILE_ENABLED": logging.get("file_enabled"),
    "ALBUS_LOG_DIRECTORY": logging.get("directory"),
    "ALBUS_LOG_MODULE_NAMESPACE": logging.get("module_namespace"),

    # Log Rotation
    "ALBUS_LOG_ROTATION": logging.get("rotation"),
    "ALBUS_LOG_ROTATION_INTERVAL": logging.get("rotation_interval"),
    "ALBUS_LOG_RETENTION_DAYS": logging.get("retention_days"),
    "ALBUS_LOG_COMPRESSION": logging.get("compression"),

    # Security
    "ALBUS_LOG_REDACT_SENSITIVE": logging.get("redact_sensitive"),
}

# ------------------------------------------------------------------------
# Generate Shell Exports
# ------------------------------------------------------------------------

for key, val in exports.items():

    if val is None:
        continue

    if isinstance(val, bool):
        val = str(val).lower()

    print(f"export {key}={shlex.quote(str(val))}")

PY
}

load_configuration() {

    # ------------------------------------------------------------------------
    # Load Base Environment Variables (.env)
    # ------------------------------------------------------------------------

    if [[ ! -f "$ENV_FILE" ]]; then
        log_error ".env file not found: $ENV_FILE"
        log_info "Create one using .env.example in the project root."
        exit 1
    fi

    set -a

    # shellcheck disable=SC1090
    source "$ENV_FILE"

    set +a

    # ------------------------------------------------------------------------
    # Validate Environment
    # ------------------------------------------------------------------------

    if [[ -z "${ENV:-}" ]]; then
        log_error "ENV is not defined in .env."
        exit 1
    fi

    case "$ENV" in

        development|testing|staging|production)
            SETTINGS_FILE="$CONFIG_DIR/${ENV}.toml"
            ;;

        *)
            log_error "Invalid environment: $ENV"
            log_error "Allowed environments: development, testing, staging, production"
            exit 1
            ;;
    esac

    # ------------------------------------------------------------------------
    # Load Environment-Specific TOML Settings
    # ------------------------------------------------------------------------

    if [[ ! -f "$SETTINGS_FILE" ]]; then
        log_error "Configuration file not found: $SETTINGS_FILE"
        exit 1
    fi

    local toml_exports

    if ! toml_exports="$(load_toml_exports "$SETTINGS_FILE")"; then
        log_error "Failed to load configuration: $SETTINGS_FILE"
        exit 1
    fi

    eval "$toml_exports"

    # ------------------------------------------------------------------------
    # Application Defaults
    # ------------------------------------------------------------------------

    APP_MODULE="${ALBUS_APP_MODULE:-app.main:app}"
    HOST="${ALBUS_HOST:-127.0.0.1}"
    PORT="${ALBUS_PORT:-8000}"

    # ------------------------------------------------------------------------
    # Logging Defaults
    # ------------------------------------------------------------------------

    ALBUS_LOG_LEVEL="${ALBUS_LOG_LEVEL:-INFO}"

    ALBUS_LOG_CONSOLE_ENABLED="${ALBUS_LOG_CONSOLE_ENABLED:-true}"
    ALBUS_LOG_CONSOLE_FORMAT="${ALBUS_LOG_CONSOLE_FORMAT:-auto}"

    ALBUS_LOG_FILE_ENABLED="${ALBUS_LOG_FILE_ENABLED:-true}"
    ALBUS_LOG_DIRECTORY="${ALBUS_LOG_DIRECTORY:-logs}"
    ALBUS_LOG_MODULE_NAMESPACE="${ALBUS_LOG_MODULE_NAMESPACE:-albus}"

    ALBUS_LOG_ROTATION="${ALBUS_LOG_ROTATION:-midnight}"
    ALBUS_LOG_ROTATION_INTERVAL="${ALBUS_LOG_ROTATION_INTERVAL:-1}"
    ALBUS_LOG_RETENTION_DAYS="${ALBUS_LOG_RETENTION_DAYS:-14}"
    ALBUS_LOG_COMPRESSION="${ALBUS_LOG_COMPRESSION:-true}"

    ALBUS_LOG_REDACT_SENSITIVE="${ALBUS_LOG_REDACT_SENSITIVE:-true}"

    export APP_MODULE HOST PORT
    export ALBUS_LOG_LEVEL
    export ALBUS_LOG_CONSOLE_ENABLED ALBUS_LOG_CONSOLE_FORMAT
    export ALBUS_LOG_FILE_ENABLED ALBUS_LOG_DIRECTORY
    export ALBUS_LOG_MODULE_NAMESPACE
    export ALBUS_LOG_ROTATION ALBUS_LOG_ROTATION_INTERVAL
    export ALBUS_LOG_RETENTION_DAYS ALBUS_LOG_COMPRESSION
    export ALBUS_LOG_REDACT_SENSITIVE
}

# ============================================================================
# Application Startup
# ============================================================================

start_albus() {

    local uvicorn_args=(
        "$APP_MODULE"
        --host "$HOST"
        --port "$PORT"
    )

    if [[ "$ENV" == "development" || "${APP_DEBUG:-false}" == "true" ]]; then
        uvicorn_args+=(--reload)
    fi

    printf '\n'
    log_info "Launching Albus..."

    # ------------------------------------------------------------------------
    # Application Configuration Summary
    # ------------------------------------------------------------------------

    printf '\n'
    printf '%bAPPLICATION CONFIGURATION%b\n' "$BOLD" "$RESET"

    printf '  Application : %s\n' "${APP_NAME:-Albus}"
    printf '  Environment : %s\n' "$ENV"
    printf '  Debug Mode  : %s\n' "${APP_DEBUG:-false}"
    printf '  Host        : %s\n' "$HOST"
    printf '  Port        : %s\n' "$PORT"
    printf '  Entry point : %s\n' "$APP_MODULE"

    # ------------------------------------------------------------------------
    # Logging Configuration Summary
    # ------------------------------------------------------------------------

    printf '\n'
    printf '%bLOGGING CONFIGURATION%b\n' "$BOLD" "$RESET"

    printf '  Log Level       : %s\n' "$ALBUS_LOG_LEVEL"
    printf '  Console Logging : %s\n' "$ALBUS_LOG_CONSOLE_ENABLED"
    printf '  Console Format  : %s\n' "$ALBUS_LOG_CONSOLE_FORMAT"

    printf '  File Logging    : %s\n' "$ALBUS_LOG_FILE_ENABLED"
    printf '  Log Directory   : %s\n' "$ALBUS_LOG_DIRECTORY"
    printf '  Module Namespace: %s\n' "$ALBUS_LOG_MODULE_NAMESPACE"

    printf '  Rotation        : %s\n' "$ALBUS_LOG_ROTATION"
    printf '  Rotation Interval: %s\n' "$ALBUS_LOG_ROTATION_INTERVAL"
    printf '  Retention       : %s days\n' "$ALBUS_LOG_RETENTION_DAYS"
    printf '  Compression     : %s\n' "$ALBUS_LOG_COMPRESSION"
    printf '  Redaction       : %s\n\n' "$ALBUS_LOG_REDACT_SENSITIVE"

    # ------------------------------------------------------------------------
    # Launch Application
    # ------------------------------------------------------------------------

    cd "$PROJECT_ROOT/backend"

    exec uv run \
        --project "$PROJECT_ROOT/backend" \
        --no-sync \
        python -m uvicorn "${uvicorn_args[@]}"
}

# ============================================================================
# Main
# ============================================================================

main() {

    if ! command -v uv &>/dev/null; then
        log_error "uv is not installed or not available in PATH."
        exit 1
    fi

    ensure_setup

    load_configuration

    start_albus
}

main "$@"
