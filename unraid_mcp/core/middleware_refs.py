"""Shared references to middleware instances.

Set by server.py at startup; read by tools that need middleware stats.
This module breaks the circular dependency between server.py (which imports
tools/unraid.py) and tools/unraid.py (which previously imported server to
access _error_middleware).

Usage:
    # In server.py (after creating the instance):
    from .core import middleware_refs
    middleware_refs.error_middleware = _error_middleware

    # In tools/unraid.py (inside a function, not at module level):
    from ..core.middleware_refs import error_middleware
    stats = error_middleware.get_error_stats() if error_middleware else {}
"""

from typing import Any


# Populated by server.py before any tool is called.
# None until server startup completes.
error_middleware: Any = None
