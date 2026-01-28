"""
Front Panel for Storage Box drawer.

Handle, label frame, and decorative elements.
"""

import math
from typing import Optional, Tuple

try:
    import bpy
    import bmesh
    HAS_BPY = True
except ImportError:
    HAS_BPY = False

from ..config.derived_config import DerivedConfig
from ..config.design_tokens import DesignTokens


def ensure_bpy():
    """Check if bpy is available."""
    if not HAS_BPY:
        raise RuntimeError("Blender Python API (bpy) not available")


def build_front_panel(
    config: DerivedConfig,
    tokens: DesignTokens,
    name: str = "FrontPanel",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Create front panel with handle and label frame.
    
    Features:
    - Panel base with appropriate thickness
    - Handle cutout (style-dependent)
    - Label frame (style-dependent)
    - Internal ribs for stiffness
    - Shadow gap (if premium style)
    
    Args:
        config: DerivedConfig
        tokens: DesignTokens for current style
        name: Object name
        location: Object location
    
    Returns:
        Blender object
    """
    ensure_bpy()
    
    width = config.config.width
    height = config.config.height
    thickness = config.front_panel_thickness
    
    # Create base panel
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    panel = bpy.context.active_object
    if panel is None:
        return None
    
    panel.name = name
    panel.scale = (width, thickness, height)
    bpy.ops.object.transform_apply(scale=True)
    
    # Add handle cutout
    handle = _build_handle(config, tokens)
    if handle:
        from ..geometry.boolean_ops import boolean_difference
        # Position handle at center-top area
        handle_z = height * 0.3  # 30% from top
        handle.location = (0, thickness / 2, handle_z)
        boolean_difference(panel, handle)
    
    # Add label frame
    if config.features_enabled.get("label", False):
        label = _build_label_frame(config, tokens)
        if label:
            from ..geometry.boolean_ops import boolean_difference
            # Position label above handle
            label_z = height * 0.55
            label.location = (0, thickness / 2, label_z)
            boolean_difference(panel, label)
    
    return panel


def _build_handle(
    config: DerivedConfig,
    tokens: DesignTokens,
) -> Optional["bpy.types.Object"]:
    """
    Create handle cutout based on style.
    
    Handle profiles:
    - pinch: Narrow slot for two-finger pinch
    - hook: Bottom hook for finger catch
    - hidden_bottom: Invisible bottom edge cutout
    - hidden_hook_rune: Belovodye style with tactile mark
    - rune_slot: Hexagonal rune shape
    - invisible: No visible handle (push-latch)
    """
    ensure_bpy()
    
    profile = tokens.handle_profile
    width = tokens.handle_width
    height = tokens.handle_height
    inner_radius = tokens.handle_inner_radius
    
    if profile == "invisible":
        return None
    
    if profile == "pinch":
        # Narrow horizontal slot
        return _build_pinch_handle(width, height, inner_radius)
    
    elif profile == "hook":
        # Bottom hook cutout
        return _build_hook_handle(width, height, inner_radius)
    
    elif profile == "hidden_bottom":
        # Cutout along bottom edge
        return _build_hidden_bottom_handle(
            config.config.width * 0.6, height, inner_radius
        )
    
    elif profile == "hidden_hook_rune":
        # Belovodye: hidden hook with tactile mark
        return _build_belovodie_handle(width, height, inner_radius)
    
    elif profile == "rune_slot":
        # Hexagonal rune shape
        return _build_rune_slot_handle(width, height, inner_radius)
    
    else:
        # Default hook style
        return _build_hook_handle(width, height, inner_radius)


def _build_pinch_handle(
    width: float,
    height: float,
    inner_radius: float,
) -> Optional["bpy.types.Object"]:
    """Narrow slot for pinch grip."""
    ensure_bpy()
    
    bm = bmesh.new()
    
    # Rounded rectangle slot
    half_w = width / 2
    half_h = height / 2
    r = min(inner_radius, half_h)
    
    # Simple rectangle (would add fillet in production)
    verts = [
        bm.verts.new((-half_w, 0, -half_h)),
        bm.verts.new((half_w, 0, -half_h)),
        bm.verts.new((half_w, 0, half_h)),
        bm.verts.new((-half_w, 0, half_h)),
    ]
    verts_back = [
        bm.verts.new((v.co.x, 10, v.co.z)) for v in verts
    ]
    
    bm.faces.new(verts)
    bm.faces.new(list(reversed(verts_back)))
    for i in range(4):
        next_i = (i + 1) % 4
        bm.faces.new([verts[i], verts[next_i],
                      verts_back[next_i], verts_back[i]])
    
    mesh = bpy.data.meshes.new("PinchHandle")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("PinchHandle", mesh)
    bpy.context.collection.objects.link(obj)
    
    return obj


def _build_hook_handle(
    width: float,
    height: float,
    inner_radius: float,
) -> Optional["bpy.types.Object"]:
    """Bottom hook for finger catch."""
    ensure_bpy()
    
    bm = bmesh.new()
    
    half_w = width / 2
    hook_depth = height * 0.6
    
    # Hook profile: L-shape with rounded inner corner
    verts = [
        bm.verts.new((-half_w, 0, 0)),
        bm.verts.new((half_w, 0, 0)),
        bm.verts.new((half_w, 0, -height)),
        bm.verts.new((half_w - inner_radius, 0, -height)),
        bm.verts.new((half_w - inner_radius, 0, -hook_depth)),
        bm.verts.new((-half_w + inner_radius, 0, -hook_depth)),
        bm.verts.new((-half_w + inner_radius, 0, -height)),
        bm.verts.new((-half_w, 0, -height)),
    ]
    
    verts_back = [
        bm.verts.new((v.co.x, 10, v.co.z)) for v in verts
    ]
    
    bm.faces.new(verts)
    bm.faces.new(list(reversed(verts_back)))
    for i in range(len(verts)):
        next_i = (i + 1) % len(verts)
        bm.faces.new([verts[i], verts[next_i],
                      verts_back[next_i], verts_back[i]])
    
    mesh = bpy.data.meshes.new("HookHandle")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("HookHandle", mesh)
    bpy.context.collection.objects.link(obj)
    
    return obj


def _build_hidden_bottom_handle(
    width: float,
    height: float,
    inner_radius: float,
) -> Optional["bpy.types.Object"]:
    """Invisible cutout along bottom edge."""
    ensure_bpy()
    
    # Simple angled cutout at bottom
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.active_object
    if obj is not None:
        obj.name = "HiddenBottomHandle"
        obj.scale = (width, 10, height)
        bpy.ops.object.transform_apply(scale=True)
    
    return obj


def _build_belovodie_handle(
    width: float,
    height: float,
    inner_radius: float,
) -> Optional["bpy.types.Object"]:
    """Belovodye hidden hook with tactile center mark."""
    ensure_bpy()
    
    # Hook cutout + small tactile dot
    handle = _build_hook_handle(width, height, inner_radius)
    
    # Add tactile mark (small cylinder emboss)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=1.5,
        depth=0.3,
        location=(0, 0, -height * 0.3),
    )
    mark = bpy.context.active_object
    
    if handle and mark:
        from ..geometry.boolean_ops import boolean_union
        boolean_union(handle, mark)
    
    return handle


def _build_rune_slot_handle(
    width: float,
    height: float,
    inner_radius: float,
) -> Optional["bpy.types.Object"]:
    """Hexagonal rune-shaped slot."""
    ensure_bpy()
    
    bm = bmesh.new()
    
    # Hexagonal profile
    half_w = width / 2
    half_h = height / 2
    inset = height * 0.3
    
    verts = [
        bm.verts.new((-half_w + inset, 0, half_h)),
        bm.verts.new((half_w - inset, 0, half_h)),
        bm.verts.new((half_w, 0, 0)),
        bm.verts.new((half_w - inset, 0, -half_h)),
        bm.verts.new((-half_w + inset, 0, -half_h)),
        bm.verts.new((-half_w, 0, 0)),
    ]
    
    verts_back = [
        bm.verts.new((v.co.x, 10, v.co.z)) for v in verts
    ]
    
    bm.faces.new(verts)
    bm.faces.new(list(reversed(verts_back)))
    for i in range(6):
        next_i = (i + 1) % 6
        bm.faces.new([verts[i], verts[next_i],
                      verts_back[next_i], verts_back[i]])
    
    mesh = bpy.data.meshes.new("RuneSlotHandle")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("RuneSlotHandle", mesh)
    bpy.context.collection.objects.link(obj)
    
    return obj


def _build_label_frame(
    config: DerivedConfig,
    tokens: DesignTokens,
) -> Optional["bpy.types.Object"]:
    """
    Create label frame based on style.
    
    Frame styles:
    - flush: Level with panel surface
    - raised: Proud of panel (for contrast insert)
    - recessed: Inset into panel
    - recessed_portal: Belovodye style with top/bottom breaks
    """
    ensure_bpy()
    
    style = tokens.label_frame_style
    frame_width = tokens.label_frame_width
    
    # Label dimensions (60% of panel width)
    label_width = config.config.width * 0.5
    label_height = config.config.height * 0.15
    
    if style == "recessed_portal":
        return _build_portal_label(
            label_width, label_height, frame_width,
            tokens.label_shadow_gap
        )
    else:
        # Simple rectangular frame
        bpy.ops.mesh.primitive_cube_add(size=1)
        obj = bpy.context.active_object
        if obj is not None:
            obj.name = "LabelFrame"
            obj.scale = (label_width, 10, label_height)
            bpy.ops.object.transform_apply(scale=True)
        return obj


def _build_portal_label(
    width: float,
    height: float,
    frame_width: float,
    shadow_gap: float,
) -> Optional["bpy.types.Object"]:
    """Belovodye 'portal' style label frame with top/bottom breaks."""
    ensure_bpy()
    
    bm = bmesh.new()
    
    half_w = width / 2
    half_h = height / 2
    break_width = width * 0.2  # 20% breaks at top/bottom
    
    # Portal frame profile (rectangle with top/bottom insets)
    verts = [
        # Bottom left
        bm.verts.new((-half_w, 0, -half_h)),
        # Bottom center left
        bm.verts.new((-break_width, 0, -half_h)),
        bm.verts.new((-break_width, 0, -half_h - frame_width)),
        bm.verts.new((break_width, 0, -half_h - frame_width)),
        bm.verts.new((break_width, 0, -half_h)),
        # Bottom right
        bm.verts.new((half_w, 0, -half_h)),
        # Top right
        bm.verts.new((half_w, 0, half_h)),
        # Top center right
        bm.verts.new((break_width, 0, half_h)),
        bm.verts.new((break_width, 0, half_h + frame_width)),
        bm.verts.new((-break_width, 0, half_h + frame_width)),
        bm.verts.new((-break_width, 0, half_h)),
        # Top left
        bm.verts.new((-half_w, 0, half_h)),
    ]
    
    verts_back = [
        bm.verts.new((v.co.x, 5, v.co.z)) for v in verts
    ]
    
    bm.faces.new(verts)
    bm.faces.new(list(reversed(verts_back)))
    for i in range(len(verts)):
        next_i = (i + 1) % len(verts)
        bm.faces.new([verts[i], verts[next_i],
                      verts_back[next_i], verts_back[i]])
    
    mesh = bpy.data.meshes.new("PortalLabel")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("PortalLabel", mesh)
    bpy.context.collection.objects.link(obj)
    
    return obj


def build_stiffening_ribs(
    config: DerivedConfig,
    name: str = "StiffeningRibs",
) -> list:
    """
    Create internal stiffening ribs for front panel.
    
    Cross or frame pattern inside the panel for rigidity.
    Rib height: 3mm, thickness: 1.2mm
    
    Args:
        config: DerivedConfig
        name: Base name for rib objects
    
    Returns:
        List of rib objects
    """
    ensure_bpy()
    
    width = config.config.width
    height = config.config.height
    
    rib_height = 3.0
    rib_thickness = 1.2
    
    ribs: list = []
    
    # Horizontal rib
    bpy.ops.mesh.primitive_cube_add(size=1)
    h_rib = bpy.context.active_object
    if h_rib is not None:
        h_rib.name = f"{name}_H"
        h_rib.scale = (width * 0.8, rib_thickness, rib_height)
        bpy.ops.object.transform_apply(scale=True)
        ribs.append(h_rib)
    
    # Vertical rib
    bpy.ops.mesh.primitive_cube_add(size=1)
    v_rib = bpy.context.active_object
    if v_rib is not None:
        v_rib.name = f"{name}_V"
        v_rib.scale = (rib_thickness, rib_height, height * 0.6)
        bpy.ops.object.transform_apply(scale=True)
        ribs.append(v_rib)
    
    return ribs
