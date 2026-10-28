"""FastAPI Application Main Entrypoint Alias.

Re-exports app and main entrypoint from api package.
"""

from api import app, main

__all__ = ["app", "main"]
