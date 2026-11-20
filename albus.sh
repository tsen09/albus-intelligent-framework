
#!/usr/bin/env bash

set -Eeuo pipefail

# ============================================================================
# Albus - Modular Python Backend Framework
# Main CLI Entry Point
# ============================================================================

# ----------------------------------------------------------------------------
# Project Paths
# ----------------------------------------------------------------------------

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"

SETUP_SCRIPT="$SCRIPTS_DIR/setup.sh"
RUN_SCRIPT="$SCRIPTS_DIR/run.sh"
REMOVE_SCRIPT="$SCRIPTS_DIR/remove.sh"

# ----------------------------------------------------------------------------
# Shared Terminal Utilities
# ----------------------------------------------------------------------------

# shellcheck source=scripts/lib/common.sh
source "$SCRIPTS_DIR/lib/common.sh"

# ============================================================================
# Help
# ============================================================================

show_help() {
    print_banner

    printf '%bUSAGE%b\n' "$BOLD" "$RESET"
    printf '  ./albus.sh <command> [options]\n\n'

    printf '%bCOMMANDS%b\n' "$BOLD" "$RESET"
    printf '  %bsetup%b       Set up the project environment\n' "$ELECTRIC_BLUE" "$RESET"
    printf '  %brun%b         Start the Albus backend\n' "$ELECTRIC_BLUE" "$RESET"
    printf '  %bremove%b      Remove the local project environment\n' "$ELECTRIC_BLUE" "$RESET"
    printf '  %bhelp%b        Display this help message\n\n' "$ELECTRIC_BLUE" "$RESET"

    printf '%bOPTIONS%b\n' "$BOLD" "$RESET"
    printf '  %b-s, --setup%b      Set up the project environment\n' "$ELECTRIC_BLUE" "$RESET"
    printf '  %b-r, --remove%b     Remove the local project environment\n' "$ELECTRIC_BLUE" "$RESET"
    printf '  %b-y, --yes%b        Skip removal confirmation\n' "$ELECTRIC_BLUE" "$RESET"
    printf '  %b-h, --help%b       Display help\n' "$ELECTRIC_BLUE" "$RESET"
    printf '  %b-v, --version%b    Display version information\n\n' "$ELECTRIC_BLUE" "$RESET"

    printf '%bEXAMPLES%b\n' "$BOLD" "$RESET"
    printf '  ./albus.sh setup\n'
    printf '  ./albus.sh --setup\n'
    printf '  ./albus.sh -s\n'
    printf '  ./albus.sh run\n'
    printf '  ./albus.sh remove\n'
    printf '  ./albus.sh -r\n'
    printf '  ./albus.sh --remove --yes\n\n'

    printf '%bAlbus | Modular Python Backend Framework | MIT License%b\n\n' \
        "$DIM" "$RESET"
}

# ============================================================================
# Command Execution
# ============================================================================

execute_script() {
    local script_path="$1"
    local script_name="$2"

    shift 2

    if [[ ! -f "$script_path" ]]; then
        log_error "Script not found: $script_path"
        exit 1
    fi

    log_info "$script_name"

    exec bash "$script_path" "$@"
}

# ============================================================================
# Removal Confirmation
# ============================================================================

confirm_removal() {
    local response

    printf '\n'
    printf '%bWARNING%b\n' "$AMBER" "$RESET"
    printf '  You are about to remove the local Albus environment.\n'
    printf '  Generated environment and build artifacts may be deleted.\n'
    printf '  Project source code and configuration files will be preserved.\n\n'

    if [[ ! -t 0 ]]; then
        log_error "Interactive confirmation required. Use --yes to proceed."
        exit 1
    fi

    read -r -p "  Are you sure you want to continue? [y/N]: " response

    case "$response" in
        [yY]|[yY][eE][sS])
            printf '\n'
            log_info "Removal confirmed."
            ;;

        *)
            printf '\n'
            log_info "Removal cancelled."
            exit 0
            ;;
    esac
}

# ============================================================================
# Version Information
# ============================================================================

show_version() {
    local pyproject_file="$PROJECT_ROOT/backend/pyproject.toml"
    local version

    print_banner

    if [[ ! -f "$pyproject_file" ]]; then
        log_error "pyproject.toml not found in backend directory."
        exit 1
    fi

    if ! command -v python3 &>/dev/null; then
        log_error "Python 3 is required to read the project version."
        exit 1
    fi

    if ! version="$(python3 -c '
import sys
import tomllib

with open(sys.argv[1], "rb") as file:
    project = tomllib.load(file)

print(project["project"]["version"])
' "$pyproject_file")"; then
        log_error "Unable to read the project version."
        exit 1
    fi

    printf '  %bAlbus v%s%b\n\n' "$BOLD$PLATINUM" "$version" "$RESET"
}

# ============================================================================
# Main
# ============================================================================

main() {
    local command="${1:-help}"
    local skip_confirmation=false

    case "$command" in

        setup|--setup|-s)
            shift
            print_banner
            execute_script "$SETUP_SCRIPT" "Preparing the Albus environment..." "$@"
            ;;

        run)
            shift
            print_banner
            execute_script "$RUN_SCRIPT" "Starting the Albus backend..." "$@"
            ;;

        remove|--remove|-r)
            shift

            while [[ $# -gt 0 ]]; do
                case "$1" in
                    --yes|-y)
                        skip_confirmation=true
                        shift
                        ;;

                    *)
                        log_error "Unknown option for remove: $1"
                        exit 1
                        ;;
                esac
            done

            print_banner

            if [[ "$skip_confirmation" == false ]]; then
                confirm_removal
            else
                log_info "Removal confirmation skipped."
            fi

            execute_script "$REMOVE_SCRIPT" "Removing the local Albus environment..."
            ;;

        help|--help|-h)
            show_help
            ;;

        --version|-v)
            show_version
            ;;

        *)
            print_banner
            log_error "Unknown command: $command"

            printf '\n'
            show_help

            exit 1
            ;;

    esac
}

main "$@"

# Ensure all project scripts are executable.
find "$SCRIPTS_DIR" -type f -name "*.sh" -exec chmod +x {} +