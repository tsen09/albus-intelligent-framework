
# Albus Shared

Shared infrastructure, utilities, and core components for the Albus Framework.

## Installation

Install the package in editable mode from the Albus project root.

### Using uv

```bash
uv pip install -e backend/modules/albus-shared
```

### Using pip

```bash
pip install -e backend/modules/albus-shared
```

### Development Installation

To install the package along with development dependencies:

**Using uv:**

```bash
uv pip install -e "backend/modules/albus-shared[dev]"
```

**Using pip:**

```bash
pip install -e "backend/modules/albus-shared[dev]"
```

## Features

- Structured logging with `structlog`.
- Configuration and environment variable utilities.
- Database connectivity and session management.
- Shared validation utilities.
- Custom exceptions.

## Requirements

- Python 3.13+
