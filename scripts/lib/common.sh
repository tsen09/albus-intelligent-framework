#!/usr/bin/env bash

# ============================================================
# Albus - Terminal Styling & Logging Utilities
# ============================================================

# ------------------------------------------------------------
# Terminal Colours
# Obsidian | Platinum | Electric Blue | Slate
# ------------------------------------------------------------

if [[ -t 1 ]]; then
    RESET=$'\033[0m'
    BOLD=$'\033[1m'
    DIM=$'\033[2m'

    # Primary palette
    OBSIDIAN=$'\033[38;5;238m'
    PLATINUM=$'\033[38;5;255m'
    ELECTRIC_BLUE=$'\033[38;5;75m'
    SLATE=$'\033[38;5;245m'

    # Semantic colours
    RED=$'\033[38;5;167m'
    GREEN=$'\033[38;5;114m'
    AMBER=$'\033[38;5;221m'
    BLUE=$'\033[38;5;75m'

    # Emphasis
    BRIGHT_BLUE=$'\033[1;38;5;117m'
    BRIGHT_WHITE=$'\033[1;38;5;255m'
else
    RESET=''
    BOLD=''
    DIM=''

    OBSIDIAN=''
    PLATINUM=''
    ELECTRIC_BLUE=''
    SLATE=''

    RED=''
    GREEN=''
    AMBER=''
    BLUE=''

    BRIGHT_BLUE=''
    BRIGHT_WHITE=''
fi

# ------------------------------------------------------------
# Logging
# ------------------------------------------------------------

log_info() {
    printf '  %bℹ%b  %s\n' "$BLUE" "$RESET" "$*"
}

log_success() {
    printf '  %b✔%b  %s\n' "$GREEN" "$RESET" "$*"
}

log_warning() {
    printf '  %b⚠%b  %s\n' "$AMBER" "$RESET" "$*"
}

log_error() {
    printf '  %b✖%b  %s\n' "$RED" "$RESET" "$*" >&2
}

log_step() {
    printf '\n  %b[%s]%b %b%s%b\n' \
        "$BOLD$ELECTRIC_BLUE" "$1" "$RESET" \
        "$PLATINUM" "$2" "$RESET"
}

# ------------------------------------------------------------
# Layout
# ------------------------------------------------------------

print_line() {
    printf '  %b────────────────────────────────────────────%b\n' \
        "$SLATE" "$RESET"
}

# ------------------------------------------------------------
# CLI Banner
# ------------------------------------------------------------

print_banner() {
    printf '\n'

    printf '  %b    █████╗ ██╗     ██████╗ ██╗   ██╗███████╗%b\n' \
        "$BOLD$ELECTRIC_BLUE" "$RESET"
    printf '  %b   ██╔══██╗██║     ██╔══██╗██║   ██║██╔════╝%b\n' \
        "$BOLD$ELECTRIC_BLUE" "$RESET"
    printf '  %b   ███████║██║     ██████╔╝██║   ██║███████╗%b\n' \
        "$BOLD$ELECTRIC_BLUE" "$RESET"
    printf '  %b   ██╔══██║██║     ██╔══██╗██║   ██║╚════██║%b\n' \
        "$BOLD$ELECTRIC_BLUE" "$RESET"
    printf '  %b   ██║  ██║███████╗██████╔╝╚██████╔╝███████║%b\n' \
        "$BOLD$ELECTRIC_BLUE" "$RESET"
    printf '  %b   ╚═╝  ╚═╝╚══════╝╚═════╝  ╚═════╝ ╚══════╝%b\n' \
        "$BOLD$ELECTRIC_BLUE" "$RESET"

    printf '\n'

    printf '  %bMODULAR PYTHON BACKEND FRAMEWORK%b\n' \
        "$BOLD$PLATINUM" "$RESET"

    printf '  %bThe foundation for intelligent agent systems.%b\n' \
        "$DIM$SLATE" "$RESET"

    printf '\n'

    printf '  %bINFRASTRUCTURE%b %b•%b %bMODULARITY%b %b•%b %bINTELLIGENCE%b\n' \
        "$ELECTRIC_BLUE" "$RESET" \
        "$SLATE" "$RESET" \
        "$ELECTRIC_BLUE" "$RESET" \
        "$SLATE" "$RESET" \
        "$ELECTRIC_BLUE" "$RESET"

    print_line
}

# ------------------------------------------------------------
# Sections
# ------------------------------------------------------------

print_section() {
    printf '\n'
    printf '  %b◆ %s%b\n' "$BOLD$ELECTRIC_BLUE" "$1" "$RESET"

    print_line
}

# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------

print_footer() {
    print_line

    printf '  %bAlbus%b %b| Infrastructure for intelligent agents.%b\n\n' \
        "$BOLD$ELECTRIC_BLUE" "$DIM$SLATE" "$RESET"
}
