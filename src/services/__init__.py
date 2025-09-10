"""Services package for kicad_builder.

Expose commonly used service entry points here for convenience.
"""

from . import config_manager  # re-export
from . import plugin_system

__all__ = ["config_manager", "plugin_system"]
