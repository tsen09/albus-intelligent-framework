#!/usr/bin/env bash

set -Eeuo pipefail

# ============================================================
# Albus - Development Preflight Checks
# ============================================================

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"

COMMON_FILE="$SCRIPT_DIR/lib/common.sh"
WORKFLOWS_DIR="$PROJECT_ROOT/.github/workflows"

# ============================================================
# Shared Utilities
# ============================================================

if [[ ! -f "$COMMON_FILE" ]]; then
    printf 'ERROR: Common utilities not found: %s\n' "$COMMON_FILE" >&2
    exit 1
fi

source "$COMMON_FILE"

cd "$PROJECT_ROOT"

# ============================================================
# Error Handling
# ============================================================

handle_error() {
    local exit_code=$?

    log_error "Preflight checks failed. Exit code: $exit_code"
    log_error "Review the output above and resolve the reported issues."

    exit "$exit_code"
}

trap handle_error ERR

# ============================================================
# Project Initialization
# ============================================================

print_banner "Albus - Development Preflight"

if [[ ! -f "$PROJECT_ROOT/pyproject.toml" ]]; then
    log_error "pyproject.toml not found in project root."
    exit 1
fi

if [[ ! -f "$PROJECT_ROOT/uv.lock" ]]; then
    log_error "uv.lock not found. Run ./scripts/setup.sh first."
    exit 1
fi

# ============================================================
# Step 1 - Verify Prerequisites
# ============================================================

print_section "Checking Prerequisites"

if ! command -v uv >/dev/null 2>&1; then
    log_error "uv is not installed or is not available in PATH."
    exit 1
fi

log_success "uv is available: $(uv --version)"

if [[ ! -d "$PROJECT_ROOT/.venv" ]]; then
    log_error "Virtual environment not found. Run ./scripts/setup.sh first."
    exit 1
fi

log_success "Virtual environment found."

# ============================================================
# Step 2 - Validate Lockfile
# ============================================================

print_section "Dependency Validation"

log_step "Checking dependency lockfile..."

uv lock --check

log_success "Dependency lockfile is valid."

# ============================================================
# Step 3 - Ruff Linting
# ============================================================

print_section "Code Quality"

log_step "Running Ruff linting..."

uv run --locked --no-sync ruff check .

log_success "Ruff linting passed."

# ============================================================
# Step 4 - Ruff Formatting
# ============================================================

log_step "Checking code formatting..."

uv run --locked --no-sync ruff format --check .

log_success "Code formatting check passed."

# ============================================================
# Step 5 - Static Type Checking
# ============================================================

print_section "Static Analysis"

log_step "Running Pyright..."

uv run --locked --no-sync pyright

log_success "Static type checking passed."

# ============================================================
# Step 6 - Test Suite and Coverage
# ============================================================

print_section "Testing"

log_step "Executing Pytest..."

uv run --locked --no-sync pytest

log_success "All tests passed."

# ============================================================
# Step 7 - Code Complexity
# ============================================================

print_section "Code Complexity Analysis"

log_step "Checking cyclomatic complexity..."

uv run --locked --no-sync radon cc backend -s -n B

log_success "Cyclomatic complexity check completed."

log_step "Checking maintainability index..."

uv run --locked --no-sync radon mi backend -s -n B

log_success "Maintainability analysis completed."

# ============================================================
# Step 8 - Dependency Security Audit
# ============================================================

print_section "Dependency Security"

log_step "Auditing Python dependencies..."

uv run --locked --no-sync pip-audit

log_success "Dependency security audit passed."

# ============================================================
# Step 9 - Secret Detection
# ============================================================

log_step "Scanning for accidentally committed secrets..."

uv run --locked --no-sync detect-secrets scan

log_success "Secret detection scan completed."

# ============================================================
# Step 10 - GitHub Actions Security
# ============================================================

if [[ -d "$WORKFLOWS_DIR" ]]; then

    print_section "GitHub Actions Security"

    log_step "Auditing GitHub Actions workflows..."

    uv run --locked --no-sync zizmor "$WORKFLOWS_DIR"

    log_success "GitHub Actions security audit passed."

else
    log_warning "No GitHub Actions workflows found. Skipping Zizmor."
fi

# ============================================================
# Step 11 - Final Summary
# ============================================================

print_footer

log_success "All preflight checks completed successfully."

log_info "Project: Albus"
log_info "Python: $(uv run --locked --no-sync python --version)"
log_info "Environment: $PROJECT_ROOT/.venv"

log_info "Your development environment is ready."
