"""Shared pytest fixtures for the Albus shared package."""

from pathlib import Path

import pytest


@pytest.fixture
def temporary_directory(tmp_path: Path) -> Path:
    """Provide an isolated temporary working directory."""
    directory = tmp_path / "albus"
    directory.mkdir()

    return directory