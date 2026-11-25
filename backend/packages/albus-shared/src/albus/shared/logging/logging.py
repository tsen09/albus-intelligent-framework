"""Compatibility imports; the canonical initialization lives in setup.py."""
from .factory import create_logger, get_logger
from .setup import setup_logging

__all__ = ["create_logger", "get_logger", "setup_logging"]
