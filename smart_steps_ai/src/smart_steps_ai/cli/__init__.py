"""Command-line interface for the Smart Steps AI module."""

from .main import app
from .commands import register_commands

__all__ = ["app", "register_commands"]
