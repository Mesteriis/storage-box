"""
Shell Component for Storage Box.

Main outer container with rails, connections, and dust labyrinth.
"""

from typing import Optional, Tuple

try:
    import bpy
    HAS_BPY = True
except ImportError:
    HAS_BPY = False

from ..config.derived_config import DerivedConfig
from ..config.design_tokens import DesignTokens
from ..config.enums import ConnectionType


def ensure_bpy():
    """Check if bpy is available."""
    if not HAS_BPY:
        raise RuntimeError("Blender Python API (bpy) not available")


def build_shell(
    config: DerivedConfig,
    tokens: DesignTokens,
    name: str = "Shell",
) -> Optional["bpy.types.Object"]:
    """
    Build complete shell with all features.
    
    Components:
    - Outer walls with style-appropriate corners
    - V-profile rails on sides
    - Dust labyrinth on rails
    - Rail windows for debris exit
    - Connection elements (dovetail/magnet/clip)
    - Stacking keys
    - Service channel (if enabled)
    - Smart cartridge bay
    - Micro-feet
    
    Args:
        config: DerivedConfig with all parameters
        tokens: DesignTokens for visual style
        name: Object name
    
    Returns:
        Complete shell object
    """
    ensure_bpy()
    
    from ..geometry.boolean_ops import (
        boolean_difference,
        boolean_union,
        boolean_batch_difference,
    )
    from .rails import (
        build_rail_with_dust_lip,
        build_rail_windows,
        build_guide_cone,
        build_service_channel,
    )
    from .connections import build_connection_set
    
    width = config.config.width
    depth = config.config.depth
    height = config.config.height
    wall = config.wall_thickness
    floor = config.floor_thickness
    
    # Step 1: Create outer shell box
    shell = _create_outer_box(width, depth, height, name)
    if shell is None:
        return None
    
    # Step 2: Create inner cavity
    inner = _create_inner_cavity(
        width - 2 * wall,
        depth - 2 * wall,
        height - floor,
        config
    )
    if inner:
        inner.location = (0, 0, floor / 2)
        boolean_difference(shell, inner)
    
    # Step 3: Add V-rails on sides
    rail_left = build_rail_with_dust_lip(
        depth - 2 * wall,
        config,
        name="RailLeft",
        location=(-width / 2 + wall + config.RAIL_WIDTH / 2, -depth / 2 + wall, 0)
    )
    rail_right = build_rail_with_dust_lip(
        depth - 2 * wall,
        config,
        name="RailRight",
        location=(width / 2 - wall - config.RAIL_WIDTH / 2, -depth / 2 + wall, 0)
    )
    
    if rail_left:
        build_rail_windows(rail_left, depth - 2 * wall, config)
        boolean_union(shell, rail_left)
    if rail_right:
        build_rail_windows(rail_right, depth - 2 * wall, config)
        boolean_union(shell, rail_right)
    
    # Step 4: Add guide cones at rail entry
    if config.features_enabled.get("guide_cones", True):
        _add_guide_cones(shell, config)
    
    # Step 5: Add service channel (dusty mode)
    if config.features_enabled.get("service_channel", False):
        channel = build_service_channel(
            depth,
            name="ServiceChannel",
            location=(0, 0, floor / 2)
        )
        if channel:
            boolean_difference(shell, channel)
    
    # Step 6: Add connections (top surface)
    top_connections = build_connection_set(config, is_top=True)
    for conn in top_connections:
        conn.location = (
            conn.location[0],
            conn.location[1],
            height - 2
        )
        boolean_union(shell, conn)
    
    # Step 7: Add connection pockets (bottom surface)
    bottom_connections = build_connection_set(config, is_top=False)
    cutouts: list["bpy.types.Object"] = []
    for conn in bottom_connections:
        conn.location = (conn.location[0], conn.location[1], 0)
        cutouts.append(conn)
    if cutouts:
        boolean_batch_difference(shell, cutouts)
    
    # Step 8: Add smart cartridge bay
    if config.features_enabled.get("smart_cartridge", False):
        _add_smart_cartridge_bay(shell, config)
    
    # Step 9: Add micro-feet
    _add_micro_feet(shell, config)
    
    # Step 10: Apply style-specific features
    _apply_style_features(shell, config, tokens)
    
    return shell


def _create_outer_box(
    width: float,
    depth: float,
    height: float,
    name: str,
) -> Optional["bpy.types.Object"]:
    """Create basic outer shell box."""
    ensure_bpy()
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, height / 2)
    )
    obj = bpy.context.active_object
    if obj is not None:
        obj.name = name
        obj.scale = (width, depth, height)
        bpy.ops.object.transform_apply(scale=True)
    
    return obj


def _create_inner_cavity(
    width: float,
    depth: float,
    height: float,
    config: DerivedConfig,
) -> Optional["bpy.types.Object"]:
    """Create inner cavity for drawer space."""
    ensure_bpy()
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, height / 2)
    )
    obj = bpy.context.active_object
    if obj is not None:
        obj.name = "InnerCavity"
        obj.scale = (width, depth, height)
        bpy.ops.object.transform_apply(scale=True)
    
    return obj


def _add_guide_cones(
    shell: "bpy.types.Object",
    config: DerivedConfig,
) -> None:
    """Add guide cones at rail entry for auto-alignment."""
    from .rails import build_guide_cone
    from ..geometry.boolean_ops import boolean_union
    
    width = config.config.width
    depth = config.config.depth
    wall = config.wall_thickness
    rail_w = config.RAIL_WIDTH
    
    # Four cones at rail entry corners
    positions = [
        (-width / 2 + wall + rail_w / 2 - 2, -depth / 2 + wall + 2),
        (-width / 2 + wall + rail_w / 2 + 2, -depth / 2 + wall + 2),
        (width / 2 - wall - rail_w / 2 - 2, -depth / 2 + wall + 2),
        (width / 2 - wall - rail_w / 2 + 2, -depth / 2 + wall + 2),
    ]
    
    for i, (x, y) in enumerate(positions):
        cone = build_guide_cone(
            height=1.5,
            base_radius=2.0,
            name=f"GuideCone_{i}",
            location=(x, y, config.floor_thickness + 1)
        )
        if cone:
            boolean_union(shell, cone)


def _add_smart_cartridge_bay(
    shell: "bpy.types.Object",
    config: DerivedConfig,
) -> None:
    """Add smart cartridge bay at rear of shell."""
    from ..geometry.boolean_ops import boolean_difference
    
    width = config.config.width
    depth = config.config.depth
    
    # Cartridge pocket dimensions
    c_w = config.CARTRIDGE_W
    c_h = config.CARTRIDGE_H
    c_d = config.CARTRIDGE_D
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, depth / 2 - c_d / 2, c_h / 2 + config.floor_thickness)
    )
    pocket = bpy.context.active_object
    if pocket is not None:
        pocket.name = "CartridgeBay"
        pocket.scale = (c_w, c_d, c_h)
        bpy.ops.object.transform_apply(scale=True)
        boolean_difference(shell, pocket)


def _add_micro_feet(
    shell: "bpy.types.Object",
    config: DerivedConfig,
) -> None:
    """Add micro-feet at corners for stability."""
    from ..geometry.boolean_ops import boolean_union
    
    width = config.config.width
    depth = config.config.depth
    
    foot_height = 0.6
    foot_radius = 4.0
    
    positions = [
        (width / 2 - 10, depth / 2 - 10),
        (width / 2 - 10, -depth / 2 + 10),
        (-width / 2 + 10, depth / 2 - 10),
        (-width / 2 + 10, -depth / 2 + 10),
    ]
    
    for i, (x, y) in enumerate(positions):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=24,
            radius=foot_radius,
            depth=foot_height,
            location=(x, y, -foot_height / 2)
        )
        foot = bpy.context.active_object
        if foot is not None:
            foot.name = f"MicroFoot_{i}"
            boolean_union(shell, foot)


def _apply_style_features(
    shell: "bpy.types.Object",
    config: DerivedConfig,
    tokens: DesignTokens,
) -> None:
    """Apply style-specific features to shell."""
    from ..geometry.patterns import apply_rune_pattern
    from ..geometry.boolean_ops import boolean_difference
    
    # Apply corner treatment based on style
    if tokens.radius_outer > 0:
        # Would apply fillet modifier here
        pass
    
    if tokens.chamfer > 0:
        # Would apply chamfer here
        pass
    
    # Apply rune patterns if Belovodye style
    if tokens.pattern_type == "runes":
        params = tokens.pattern_params
        pattern = apply_rune_pattern(
            shell,
            motif=params.get("motif", "chevron_rune"),
            position=params.get("band_position", "back_edge"),
            spacing=params.get("spacing", 8),
            band_height=params.get("band_height", 14),
            config=config,
        )
        if pattern:
            boolean_difference(shell, pattern)
    
    # Add version mark if enabled
    if tokens.version_mark:
        _add_version_mark(shell, config)


def _add_version_mark(
    shell: "bpy.types.Object",
    config: DerivedConfig,
) -> None:
    """Add version mark on bottom of shell."""
    # Version mark would be embossed text "BV-1.x"
    # For now, just a placeholder marker
    from ..geometry.boolean_ops import boolean_difference
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, -0.15)
    )
    mark = bpy.context.active_object
    if mark is not None:
        mark.name = "VersionMark"
        mark.scale = (20, 8, 0.3)
        bpy.ops.object.transform_apply(scale=True)
        boolean_difference(shell, mark)


def build_shell_simple(
    width: float,
    depth: float,
    height: float,
    wall: float = 2.0,
    name: str = "ShellSimple",
) -> Optional["bpy.types.Object"]:
    """
    Build simplified shell without advanced features.
    
    Useful for quick prototyping or MVP preset.
    
    Args:
        width: External width
        depth: External depth
        height: External height
        wall: Wall thickness
        name: Object name
    
    Returns:
        Simple shell object
    """
    ensure_bpy()
    
    from ..geometry.boolean_ops import boolean_difference
    
    # Outer box
    shell = _create_outer_box(width, depth, height, name)
    if shell is None:
        return None
    
    # Inner cavity
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, height / 2 + wall / 2)
    )
    inner = bpy.context.active_object
    if inner is not None:
        inner.name = "InnerCavity"
        inner.scale = (width - 2 * wall, depth - 2 * wall, height - wall)
        bpy.ops.object.transform_apply(scale=True)
        boolean_difference(shell, inner)
    
    return shell
