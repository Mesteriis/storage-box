"""
Drawer Component for Storage Box.

Sliding drawer with stops, front panel, and divider slots.
"""

from typing import Optional, Tuple

try:
    import bpy
    HAS_BPY = True
except ImportError:
    HAS_BPY = False

from ..config.derived_config import DerivedConfig
from ..config.design_tokens import DesignTokens


def ensure_bpy():
    """Check if bpy is available."""
    if not HAS_BPY:
        raise RuntimeError("Blender Python API (bpy) not available")


def build_drawer(
    config: DerivedConfig,
    tokens: DesignTokens,
    name: str = "Drawer",
) -> Optional["bpy.types.Object"]:
    """
    Build complete drawer with all features.
    
    Components:
    - Tray body with V-grooves for rails
    - Dust shelves on grooves
    - Internal divider slots
    - Front panel with handle/label
    - Slide pads mounting points
    - Micro lip for content retention
    - Weep holes for cleaning
    
    Args:
        config: DerivedConfig with all parameters
        tokens: DesignTokens for visual style
        name: Object name
    
    Returns:
        Complete drawer object
    """
    ensure_bpy()
    
    from ..geometry.boolean_ops import (
        boolean_difference,
        boolean_union,
        boolean_batch_difference,
    )
    from .rails import build_v_groove
    from .front_panel import build_front_panel
    from .stops import build_two_stage_stop
    
    width = config.drawer_width
    depth = config.drawer_depth
    height = config.drawer_height
    wall = config.wall_thickness
    floor = config.floor_thickness
    
    # Step 1: Create drawer tray
    drawer = _create_tray(width, depth, height, floor, name)
    if drawer is None:
        return None
    
    # Step 2: Create inner cavity
    inner = _create_inner_cavity(
        width - 2 * wall,
        depth - 2 * wall,
        height - floor,
    )
    if inner:
        inner.location = (0, 0, floor / 2)
        boolean_difference(drawer, inner)
    
    # Step 3: Add V-grooves on sides for rail engagement
    clearance = config.tolerances["slide"]
    groove_left = build_v_groove(
        depth,
        width=config.RAIL_WIDTH,
        depth=config.RAIL_DEPTH,
        clearance=clearance,
        name="GrooveLeft",
        location=(-width / 2, -depth / 2, height / 2)
    )
    groove_right = build_v_groove(
        depth,
        width=config.RAIL_WIDTH,
        depth=config.RAIL_DEPTH,
        clearance=clearance,
        name="GrooveRight",
        location=(width / 2, -depth / 2, height / 2)
    )
    
    grooves: list["bpy.types.Object"] = []
    if groove_left:
        grooves.append(groove_left)
    if groove_right:
        grooves.append(groove_right)
    if grooves:
        boolean_batch_difference(drawer, grooves)
    
    # Step 4: Add dust shelves on grooves
    _add_dust_shelves(drawer, config)
    
    # Step 5: Add divider slots
    if config.features_enabled.get("dividers", False):
        _add_divider_slots(drawer, config)
    
    # Step 6: Add front panel
    front = build_front_panel(
        config, tokens,
        name="FrontPanel",
        location=(0, -depth / 2 - config.front_panel_thickness / 2, height / 2)
    )
    if front:
        boolean_union(drawer, front)
    
    # Step 7: Add stop engagement features
    _add_stop_features(drawer, config)
    
    # Step 8: Add slide pad mounts
    _add_slide_pad_mounts(drawer, config)
    
    # Step 9: Add micro lip for content retention
    _add_micro_lip(drawer, config)
    
    # Step 10: Add weep holes
    _add_weep_holes(drawer, config)
    
    return drawer


def _create_tray(
    width: float,
    depth: float,
    height: float,
    floor: float,
    name: str,
) -> Optional["bpy.types.Object"]:
    """Create basic drawer tray."""
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
) -> Optional["bpy.types.Object"]:
    """Create inner cavity for drawer contents."""
    ensure_bpy()
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, height / 2)
    )
    obj = bpy.context.active_object
    if obj is not None:
        obj.name = "DrawerCavity"
        obj.scale = (width, depth, height)
        bpy.ops.object.transform_apply(scale=True)
    
    return obj


def _add_dust_shelves(
    drawer: "bpy.types.Object",
    config: DerivedConfig,
) -> None:
    """Add dust shelves on V-grooves."""
    from ..geometry.boolean_ops import boolean_union
    
    width = config.drawer_width
    depth = config.drawer_depth
    height = config.drawer_height
    shelf_h = config.DUST_SHELF
    
    # Small shelf above each groove
    for side in [-1, 1]:
        x = side * (width / 2 - 1)
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(x, 0, height - shelf_h / 2)
        )
        shelf = bpy.context.active_object
        if shelf is not None:
            shelf.name = f"DustShelf_{'L' if side < 0 else 'R'}"
            shelf.scale = (2, depth - 10, shelf_h)
            bpy.ops.object.transform_apply(scale=True)
            boolean_union(drawer, shelf)


def _add_divider_slots(
    drawer: "bpy.types.Object",
    config: DerivedConfig,
) -> None:
    """Add universal slots for divider insertion."""
    from ..geometry.boolean_ops import boolean_batch_difference
    
    cols, rows = config.divider_count
    if cols == 0 and rows == 0:
        return
    
    width = config.drawer_width - 2 * config.wall_thickness
    depth = config.drawer_depth - 2 * config.wall_thickness
    
    slot_w = config.SLOT_WIDTH
    slot_d = config.SLOT_DEPTH
    
    slots: list["bpy.types.Object"] = []
    
    # Column divider slots (along X axis)
    if cols > 0:
        spacing = width / (cols + 1)
        for i in range(1, cols + 1):
            x = -width / 2 + i * spacing
            bpy.ops.mesh.primitive_cube_add(
                size=1,
                location=(x, 0, slot_d / 2 + config.floor_thickness)
            )
            slot = bpy.context.active_object
            if slot is not None:
                slot.name = f"ColSlot_{i}"
                slot.scale = (slot_w, depth - 5, slot_d)
                bpy.ops.object.transform_apply(scale=True)
                slots.append(slot)
    
    # Row divider slots (along Y axis)
    if rows > 0:
        spacing = depth / (rows + 1)
        for i in range(1, rows + 1):
            y = -depth / 2 + i * spacing
            bpy.ops.mesh.primitive_cube_add(
                size=1,
                location=(0, y, slot_d / 2 + config.floor_thickness)
            )
            slot = bpy.context.active_object
            if slot is not None:
                slot.name = f"RowSlot_{i}"
                slot.scale = (width - 5, slot_w, slot_d)
                bpy.ops.object.transform_apply(scale=True)
                slots.append(slot)
    
    if slots:
        boolean_batch_difference(drawer, slots)


def _add_stop_features(
    drawer: "bpy.types.Object",
    config: DerivedConfig,
) -> None:
    """Add engagement features for drawer stops."""
    from ..geometry.boolean_ops import boolean_difference
    
    # Notch for spring tab engagement
    depth = config.drawer_depth
    height = config.drawer_height
    
    notch_w = 12.0
    notch_h = 4.0
    notch_d = 3.0
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, depth / 2 - notch_d / 2, height - notch_h / 2)
    )
    notch = bpy.context.active_object
    if notch is not None:
        notch.name = "StopNotch"
        notch.scale = (notch_w, notch_d, notch_h)
        bpy.ops.object.transform_apply(scale=True)
        boolean_difference(drawer, notch)


def _add_slide_pad_mounts(
    drawer: "bpy.types.Object",
    config: DerivedConfig,
) -> None:
    """Add mounting slots for replaceable slide pads."""
    from ..geometry.boolean_ops import boolean_batch_difference
    
    width = config.drawer_width
    depth = config.drawer_depth
    
    # 4-6 pad locations
    pad_w = 8.0
    pad_d = 20.0
    pad_slot_h = 1.2
    
    positions = [
        (width * 0.3, depth * 0.25),
        (width * 0.3, -depth * 0.25),
        (-width * 0.3, depth * 0.25),
        (-width * 0.3, -depth * 0.25),
    ]
    
    mounts: list["bpy.types.Object"] = []
    for i, (x, y) in enumerate(positions):
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(x, y, pad_slot_h / 2)
        )
        mount = bpy.context.active_object
        if mount is not None:
            mount.name = f"PadMount_{i}"
            mount.scale = (pad_w + 0.4, pad_d + 0.4, pad_slot_h)
            bpy.ops.object.transform_apply(scale=True)
            mounts.append(mount)
    
    if mounts:
        boolean_batch_difference(drawer, mounts)


def _add_micro_lip(
    drawer: "bpy.types.Object",
    config: DerivedConfig,
) -> None:
    """Add micro lip at front to prevent content spillage."""
    from ..geometry.boolean_ops import boolean_union
    
    width = config.drawer_width - 2 * config.wall_thickness
    lip_height = 1.8
    lip_thickness = config.wall_thickness
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(
            0,
            -config.drawer_depth / 2 + lip_thickness / 2,
            config.drawer_height - lip_height / 2
        )
    )
    lip = bpy.context.active_object
    if lip is not None:
        lip.name = "MicroLip"
        lip.scale = (width, lip_thickness, lip_height)
        bpy.ops.object.transform_apply(scale=True)
        boolean_union(drawer, lip)


def _add_weep_holes(
    drawer: "bpy.types.Object",
    config: DerivedConfig,
) -> None:
    """Add drainage holes in corners for cleaning."""
    from ..geometry.boolean_ops import boolean_batch_difference
    
    width = config.drawer_width
    depth = config.drawer_depth
    floor = config.floor_thickness
    
    hole_radius = 1.5
    
    positions = [
        (width / 2 - 8, depth / 2 - 8),
        (width / 2 - 8, -depth / 2 + 8),
        (-width / 2 + 8, depth / 2 - 8),
        (-width / 2 + 8, -depth / 2 + 8),
    ]
    
    holes: list["bpy.types.Object"] = []
    for i, (x, y) in enumerate(positions):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=16,
            radius=hole_radius,
            depth=floor + 1,
            location=(x, y, floor / 2)
        )
        hole = bpy.context.active_object
        if hole is not None:
            hole.name = f"WeepHole_{i}"
            holes.append(hole)
    
    if holes:
        boolean_batch_difference(drawer, holes)


def build_drawer_simple(
    width: float,
    depth: float,
    height: float,
    wall: float = 2.0,
    name: str = "DrawerSimple",
) -> Optional["bpy.types.Object"]:
    """
    Build simplified drawer without advanced features.
    
    Useful for quick prototyping or MVP preset.
    
    Args:
        width: External width
        depth: External depth
        height: External height
        wall: Wall thickness
        name: Object name
    
    Returns:
        Simple drawer object
    """
    ensure_bpy()
    
    from ..geometry.boolean_ops import boolean_difference
    
    # Outer box
    drawer = _create_tray(width, depth, height, wall, name)
    if drawer is None:
        return None
    
    # Inner cavity
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, height / 2 + wall / 2)
    )
    inner = bpy.context.active_object
    if inner is not None:
        inner.name = "DrawerCavity"
        inner.scale = (width - 2 * wall, depth - 2 * wall, height - wall)
        bpy.ops.object.transform_apply(scale=True)
        boolean_difference(drawer, inner)
    
    return drawer
