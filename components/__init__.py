"""
Storage Box Components.

Main building blocks for the parametric storage box system:
- Shell: outer container with rails and connections
- Drawer: sliding tray with stops and front panel
- Dividers: removable partitions
- FrontPanel: front panel with handle and label
- Rails: V-profile rail system
- Connections: stacking connections (dovetail, magnet, clip)
"""

from .shell import build_shell
from .drawer import build_drawer
from .rails import build_v_rail, build_rail_with_dust_lip, build_rail_windows
from .connections import build_dovetail, build_magnet_pocket, build_clip
from .front_panel import build_front_panel
from .stops import build_two_stage_stop, build_acoustic_tab

__all__ = [
    "build_shell",
    "build_drawer",
    "build_v_rail",
    "build_rail_with_dust_lip",
    "build_rail_windows",
    "build_dovetail",
    "build_magnet_pocket",
    "build_clip",
    "build_front_panel",
    "build_two_stage_stop",
    "build_acoustic_tab",
]
