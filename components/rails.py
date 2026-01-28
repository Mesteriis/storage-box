"""
Rail System for Storage Box.

V-profile rails with self-centering, dust labyrinth, and service channel.
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


def ensure_bpy():
    """Check if bpy is available."""
    if not HAS_BPY:
        raise RuntimeError("Blender Python API (bpy) not available")


def build_v_rail(
    length: float,
    width: float = 5.0,
    depth: float = 4.0,
    angle: float = 45.0,
    name: str = "VRail",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Create a V-profile rail for self-centering drawer slides.
    
    V-profile provides:
    - Self-centering when drawer is inserted
    - Temperature expansion compensation
    - Smooth sliding action
    
    Args:
        length: Rail length (Y axis)
        width: Rail width (X axis)
        depth: Rail depth (Z axis)
        angle: V angle in degrees (45° optimal for PLA/PETG)
        name: Object name
        location: Object location
    
    Returns:
        Blender object
    """
    ensure_bpy()
    
    bm = bmesh.new()
    
    # V profile geometry
    half_width = width / 2
    rad = math.radians(angle / 2)
    v_depth = half_width * math.tan(rad)
    
    # Profile: front face (looking from -Y)
    # Creates outward-pointing V (rail on shell)
    verts_front = [
        bm.verts.new((-half_width, 0, 0)),           # Left base
        bm.verts.new((0, 0, -v_depth)),              # V point (down)
        bm.verts.new((half_width, 0, 0)),            # Right base
        bm.verts.new((half_width, 0, depth)),        # Right top
        bm.verts.new((-half_width, 0, depth)),       # Left top
    ]
    
    # Profile: back face
    verts_back = [
        bm.verts.new((-half_width, length, 0)),
        bm.verts.new((0, length, -v_depth)),
        bm.verts.new((half_width, length, 0)),
        bm.verts.new((half_width, length, depth)),
        bm.verts.new((-half_width, length, depth)),
    ]
    
    # Create faces
    # Front face
    bm.faces.new([verts_front[4], verts_front[3], 
                  verts_front[2], verts_front[1], verts_front[0]])
    # Back face
    bm.faces.new([verts_back[0], verts_back[1], 
                  verts_back[2], verts_back[3], verts_back[4]])
    
    # Side faces
    for i in range(5):
        next_i = (i + 1) % 5
        bm.faces.new([
            verts_front[i], verts_front[next_i],
            verts_back[next_i], verts_back[i]
        ])
    
    # Create mesh
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    
    return obj


def build_v_groove(
    length: float,
    width: float = 5.0,
    depth: float = 4.0,
    angle: float = 45.0,
    clearance: float = 0.3,
    name: str = "VGroove",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Create V-groove (matching groove for V-rail) on drawer side.
    
    Args:
        length: Groove length (Y axis)
        width: Groove width (X axis)
        depth: Groove depth (Z axis)
        angle: V angle in degrees
        clearance: Gap between rail and groove
        name: Object name
        location: Object location
    
    Returns:
        Blender object (for boolean subtraction)
    """
    ensure_bpy()
    
    # Groove is slightly larger than rail for clearance
    effective_width = width + clearance
    
    bm = bmesh.new()
    
    half_width = effective_width / 2
    rad = math.radians(angle / 2)
    v_depth = half_width * math.tan(rad) + clearance
    
    # V-groove profile (inverted V - pointing up)
    verts_front = [
        bm.verts.new((-half_width, 0, -depth)),     # Left bottom
        bm.verts.new((-half_width, 0, 0)),          # Left top
        bm.verts.new((0, 0, v_depth)),              # V point (up)
        bm.verts.new((half_width, 0, 0)),           # Right top
        bm.verts.new((half_width, 0, -depth)),      # Right bottom
    ]
    
    verts_back = [
        bm.verts.new((-half_width, length, -depth)),
        bm.verts.new((-half_width, length, 0)),
        bm.verts.new((0, length, v_depth)),
        bm.verts.new((half_width, length, 0)),
        bm.verts.new((half_width, length, -depth)),
    ]
    
    # Front face
    bm.faces.new([verts_front[0], verts_front[1], verts_front[2],
                  verts_front[3], verts_front[4]])
    # Back face
    bm.faces.new([verts_back[4], verts_back[3], verts_back[2],
                  verts_back[1], verts_back[0]])
    
    # Side faces
    for i in range(5):
        next_i = (i + 1) % 5
        bm.faces.new([
            verts_front[i], verts_back[i],
            verts_back[next_i], verts_front[next_i]
        ])
    
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    
    return obj


def build_rail_with_dust_lip(
    length: float,
    config: DerivedConfig,
    name: str = "RailWithDustLip",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Create V-rail with integrated dust labyrinth.
    
    Dust labyrinth features:
    - Overhanging lip on shell rail (козырёк 1mm down)
    - Matching shelf on drawer (полка 0.8mm up)
    - Prevents dust from entering rail contact surface
    
    Args:
        length: Rail length
        config: DerivedConfig with rail parameters
        name: Object name
        location: Object location
    
    Returns:
        Blender object
    """
    ensure_bpy()
    
    bm = bmesh.new()
    
    rail_width = config.RAIL_WIDTH
    rail_depth = config.RAIL_DEPTH
    dust_lip = config.DUST_LIP
    
    half_width = rail_width / 2
    rad = math.radians(45 / 2)
    v_depth = half_width * math.tan(rad)
    
    # Profile with dust lip extension
    # Main V-rail + overhanging lip
    lip_extension = 1.5  # Lip extends past rail
    
    verts_front = [
        # V-rail portion
        bm.verts.new((-half_width, 0, 0)),
        bm.verts.new((0, 0, -v_depth)),
        bm.verts.new((half_width, 0, 0)),
        # Top portion
        bm.verts.new((half_width, 0, rail_depth)),
        # Dust lip (overhanging)
        bm.verts.new((half_width + lip_extension, 0, rail_depth)),
        bm.verts.new((half_width + lip_extension, 0, rail_depth - dust_lip)),
        bm.verts.new((half_width, 0, rail_depth - dust_lip)),
        # Back to origin side
        bm.verts.new((-half_width, 0, rail_depth - dust_lip)),
        bm.verts.new((-half_width - lip_extension, 0, rail_depth - dust_lip)),
        bm.verts.new((-half_width - lip_extension, 0, rail_depth)),
        bm.verts.new((-half_width, 0, rail_depth)),
    ]
    
    verts_back = []
    for v in verts_front:
        verts_back.append(bm.verts.new((v.co.x, length, v.co.z)))
    
    # Front face
    bm.faces.new(list(reversed(verts_front)))
    # Back face
    bm.faces.new(verts_back)
    
    # Side faces
    n = len(verts_front)
    for i in range(n):
        next_i = (i + 1) % n
        bm.faces.new([
            verts_front[i], verts_front[next_i],
            verts_back[next_i], verts_back[i]
        ])
    
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    
    return obj


def build_rail_windows(
    rail_obj: "bpy.types.Object",
    length: float,
    config: DerivedConfig,
) -> "bpy.types.Object":
    """
    Add ventilation windows to rail (reduces friction, allows debris exit).
    
    Windows every 35mm along the rail.
    
    Args:
        rail_obj: Rail object to modify
        length: Rail length
        config: DerivedConfig
    
    Returns:
        Modified rail object
    """
    ensure_bpy()
    
    from ..geometry.boolean_ops import boolean_batch_difference
    from ..geometry.primitives import create_box
    
    window_spacing = config.RAIL_WINDOW_SPACING
    window_width = 8.0
    window_depth = 3.0
    window_height = config.RAIL_DEPTH - 1.0
    
    windows: list["bpy.types.Object"] = []
    y_pos = window_spacing / 2
    
    while y_pos < length - window_spacing / 2:
        window = create_box(
            window_width, window_depth, window_height,
            name=f"RailWindow_{len(windows)}",
            location=(0, y_pos, config.RAIL_DEPTH / 2)
        )
        if window is not None:
            windows.append(window)
        y_pos += window_spacing
    
    if windows:
        boolean_batch_difference(rail_obj, windows)
    
    return rail_obj


def build_lead_in_zone(
    length: float,
    width: float,
    config: DerivedConfig,
    name: str = "LeadIn",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Create lead-in zone for anti-jam entry.
    
    Lead-in features:
    - 15° entry chamfer on first 10-15mm
    - +0.05-0.1mm extra clearance at entry
    - Prevents jamming during diagonal insertion
    
    Args:
        length: Lead-in length (typically 15mm)
        width: Rail width
        config: DerivedConfig
        name: Object name
        location: Object location
    
    Returns:
        Blender object
    """
    ensure_bpy()
    
    bm = bmesh.new()
    
    half_width = width / 2
    lead_in_extra = config.lead_in_tolerance
    entry_width = half_width + lead_in_extra
    
    # Tapered entry profile
    verts_front = [
        bm.verts.new((-entry_width, 0, 0)),
        bm.verts.new((entry_width, 0, 0)),
        bm.verts.new((entry_width, 0, config.RAIL_DEPTH)),
        bm.verts.new((-entry_width, 0, config.RAIL_DEPTH)),
    ]
    
    verts_back = [
        bm.verts.new((-half_width, length, 0)),
        bm.verts.new((half_width, length, 0)),
        bm.verts.new((half_width, length, config.RAIL_DEPTH)),
        bm.verts.new((-half_width, length, config.RAIL_DEPTH)),
    ]
    
    # Faces
    bm.faces.new(verts_front)
    bm.faces.new(list(reversed(verts_back)))
    
    for i in range(4):
        next_i = (i + 1) % 4
        bm.faces.new([
            verts_front[i], verts_front[next_i],
            verts_back[next_i], verts_back[i]
        ])
    
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    
    return obj


def build_guide_cone(
    height: float = 1.5,
    base_radius: float = 2.0,
    angle: float = 30.0,
    name: str = "GuideCone",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Create micro guide cone for auto-alignment.
    
    Guide cones at rail entry help drawer "find" the rail
    automatically during insertion.
    
    Args:
        height: Cone height
        base_radius: Cone base radius
        angle: Cone angle
        name: Object name
        location: Object location
    
    Returns:
        Blender object
    """
    ensure_bpy()
    
    bpy.ops.mesh.primitive_cone_add(
        vertices=16,
        radius1=base_radius,
        radius2=0.2,
        depth=height,
        location=location,
    )
    obj = bpy.context.active_object
    if obj is not None:
        obj.name = name
    
    return obj


def build_service_channel(
    length: float,
    channel_width: float = 2.0,
    channel_height: float = 4.0,
    name: str = "ServiceChannel",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Create service channel for dusty mode (blowout port).
    
    Thin tunnel along the rail for compressed air cleaning.
    Service port at bottom of shell for compressor nozzle.
    
    Args:
        length: Channel length (full rail length)
        channel_width: Channel width (2mm)
        channel_height: Channel height (4mm)
        name: Object name
        location: Object location
    
    Returns:
        Blender object (for boolean subtraction)
    """
    ensure_bpy()
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    if obj is not None:
        obj.name = name
        obj.scale = (channel_width, length, channel_height)
        bpy.ops.object.transform_apply(scale=True)
    
    return obj
