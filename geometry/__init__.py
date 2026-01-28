"""Geometry module for Storage Box System."""

from .primitives import (
    create_box,
    create_cylinder,
    create_plane,
    create_v_rail,
    create_v_groove,
    create_chamfer_profile,
    create_fillet_profile,
)

from .boolean_ops import (
    boolean_union,
    boolean_difference,
    boolean_intersect,
)

from .patterns import (
    create_chevron_pattern,
    create_knot_pattern,
    create_wave_pattern,
    create_pattern_band,
)

__all__ = [
    "create_box",
    "create_cylinder",
    "create_plane",
    "create_v_rail",
    "create_v_groove",
    "create_chamfer_profile",
    "create_fillet_profile",
    "boolean_union",
    "boolean_difference",
    "boolean_intersect",
    "create_chevron_pattern",
    "create_knot_pattern",
    "create_wave_pattern",
    "create_pattern_band",
]
