"""
Connection System for Storage Box stacking.

Supports dovetail, magnet pockets, and clip connections.
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
from ..config.enums import ConnectionType


def ensure_bpy():
    """Check if bpy is available."""
    if not HAS_BPY:
        raise RuntimeError("Blender Python API (bpy) not available")


def build_dovetail(
    width: float,
    depth: float,
    height: float,
    angle: float = 14.0,
    is_male: bool = True,
    name: str = "Dovetail",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Create a dovetail joint (male or female).
    
    Dovetail provides:
    - Strong mechanical interlock
    - Good for heavy loads and stacking
    - Self-aligning during assembly
    
    Args:
        width: Dovetail width at narrow end
        depth: Dovetail depth
        height: Dovetail height (extrusion length)
        angle: Dovetail angle (14° standard)
        is_male: True for protrusion, False for pocket
        name: Object name
        location: Object location
    
    Returns:
        Blender object
    """
    ensure_bpy()
    
    bm = bmesh.new()
    
    # Calculate dovetail profile
    rad = math.radians(angle)
    offset = depth * math.tan(rad)
    
    half_narrow = width / 2
    half_wide = half_narrow + offset
    
    if is_male:
        # Male dovetail (wider at top)
        verts_front = [
            bm.verts.new((-half_narrow, 0, 0)),
            bm.verts.new((half_narrow, 0, 0)),
            bm.verts.new((half_wide, 0, depth)),
            bm.verts.new((-half_wide, 0, depth)),
        ]
    else:
        # Female dovetail pocket (wider at bottom)
        verts_front = [
            bm.verts.new((-half_wide, 0, 0)),
            bm.verts.new((half_wide, 0, 0)),
            bm.verts.new((half_narrow, 0, depth)),
            bm.verts.new((-half_narrow, 0, depth)),
        ]
    
    verts_back = [
        bm.verts.new((v.co.x, height, v.co.z)) for v in verts_front
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


def build_magnet_pocket(
    diameter: float = 6.1,
    depth: float = 3.1,
    arch_top: bool = True,
    name: str = "MagnetPocket",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Create pocket for 6x3mm magnets with pressfit tolerance.
    
    Features:
    - Pressfit tolerance (6.1mm for 6mm magnet)
    - Optional arched top for overhang-free printing
    - Designed for upgradeable magnet insertion
    
    Args:
        diameter: Pocket diameter (6.1mm for 6mm magnet)
        depth: Pocket depth (3.1mm for 3mm magnet)
        arch_top: Add arch for overhang-free printing
        name: Object name
        location: Object location
    
    Returns:
        Blender object (for boolean subtraction)
    """
    ensure_bpy()
    
    if arch_top:
        # Create cylinder with arched top (45° overhang safe)
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=32,
            radius=diameter / 2,
            depth=depth,
            location=location,
        )
        obj = bpy.context.active_object
        if obj is not None:
            obj.name = name
        
        # Add arch top using cone
        arch_height = diameter / 2 * 0.5  # 45° slope
        bpy.ops.mesh.primitive_cone_add(
            vertices=32,
            radius1=diameter / 2,
            radius2=0,
            depth=arch_height,
            location=(location[0], location[1], location[2] + depth / 2),
        )
        arch = bpy.context.active_object
        
        # Union arch with cylinder
        if obj is not None and arch is not None:
            from ..geometry.boolean_ops import boolean_union
            boolean_union(obj, arch)
        
        return obj
    else:
        # Simple cylinder pocket
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=32,
            radius=diameter / 2,
            depth=depth,
            location=location,
        )
        obj = bpy.context.active_object
        if obj is not None:
            obj.name = name
        
        return obj


def build_clip(
    width: float = 8.0,
    height: float = 6.0,
    depth: float = 3.0,
    lip_height: float = 1.5,
    is_male: bool = True,
    name: str = "Clip",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Create snap-fit clip connection.
    
    Features:
    - Quick assembly without tools
    - Spring action from material flex
    - 45° entry angle for smooth engagement
    
    Args:
        width: Clip width
        height: Clip height
        depth: Clip depth
        lip_height: Retaining lip height
        is_male: True for clip, False for socket
        name: Object name
        location: Object location
    
    Returns:
        Blender object
    """
    ensure_bpy()
    
    bm = bmesh.new()
    
    if is_male:
        # Male clip with 45° entry ramp
        half_width = width / 2
        
        verts = [
            # Base
            bm.verts.new((-half_width, 0, 0)),
            bm.verts.new((half_width, 0, 0)),
            bm.verts.new((half_width, depth, 0)),
            bm.verts.new((-half_width, depth, 0)),
            # Top with lip
            bm.verts.new((-half_width, 0, height - lip_height)),
            bm.verts.new((half_width, 0, height - lip_height)),
            bm.verts.new((half_width, depth - lip_height, height - lip_height)),
            bm.verts.new((-half_width, depth - lip_height, height - lip_height)),
            # Entry ramp (45° angle)
            bm.verts.new((-half_width, depth, height)),
            bm.verts.new((half_width, depth, height)),
            bm.verts.new((half_width, depth - lip_height, height)),
            bm.verts.new((-half_width, depth - lip_height, height)),
        ]
        
        # Create faces for clip shape
        # Bottom
        bm.faces.new([verts[0], verts[1], verts[2], verts[3]])
        # Front
        bm.faces.new([verts[0], verts[4], verts[5], verts[1]])
        # Sides
        bm.faces.new([verts[0], verts[3], verts[8], verts[11], verts[7], verts[4]])
        bm.faces.new([verts[1], verts[5], verts[6], verts[10], verts[9], verts[2]])
        # Top surfaces
        bm.faces.new([verts[4], verts[7], verts[6], verts[5]])
        bm.faces.new([verts[7], verts[11], verts[10], verts[6]])
        # Back ramp
        bm.faces.new([verts[8], verts[9], verts[10], verts[11]])
        bm.faces.new([verts[3], verts[2], verts[9], verts[8]])
        
    else:
        # Female socket (simple rectangular pocket)
        half_width = width / 2 + 0.15  # Add clearance
        
        verts = [
            bm.verts.new((-half_width, 0, 0)),
            bm.verts.new((half_width, 0, 0)),
            bm.verts.new((half_width, depth + 0.1, 0)),
            bm.verts.new((-half_width, depth + 0.1, 0)),
            bm.verts.new((-half_width, 0, height + 0.1)),
            bm.verts.new((half_width, 0, height + 0.1)),
            bm.verts.new((half_width, depth + 0.1, height + 0.1)),
            bm.verts.new((-half_width, depth + 0.1, height + 0.1)),
        ]
        
        # Simple box faces
        bm.faces.new([verts[0], verts[1], verts[2], verts[3]])
        bm.faces.new([verts[7], verts[6], verts[5], verts[4]])
        bm.faces.new([verts[0], verts[4], verts[5], verts[1]])
        bm.faces.new([verts[2], verts[6], verts[7], verts[3]])
        bm.faces.new([verts[0], verts[3], verts[7], verts[4]])
        bm.faces.new([verts[1], verts[5], verts[6], verts[2]])
    
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    
    return obj


def build_stacking_key(
    width: float = 4.0,
    depth: float = 4.0,
    height: float = 2.0,
    shape: str = "triangle",
    name: str = "StackingKey",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Create anti-rotation stacking key.
    
    Asymmetric keys prevent wrong-way stacking:
    - Triangle + diamond at diagonal corners
    - Only fits one orientation
    
    Args:
        width: Key width
        depth: Key depth
        height: Key height
        shape: "triangle" or "diamond"
        name: Object name
        location: Object location
    
    Returns:
        Blender object
    """
    ensure_bpy()
    
    bm = bmesh.new()
    
    if shape == "triangle":
        # Triangular key
        verts_bottom = [
            bm.verts.new((0, -depth / 2, 0)),
            bm.verts.new((width / 2, depth / 2, 0)),
            bm.verts.new((-width / 2, depth / 2, 0)),
        ]
        verts_top = [
            bm.verts.new((v.co.x, v.co.y, height)) for v in verts_bottom
        ]
        
        bm.faces.new(verts_bottom)
        bm.faces.new(list(reversed(verts_top)))
        for i in range(3):
            next_i = (i + 1) % 3
            bm.faces.new([
                verts_bottom[i], verts_bottom[next_i],
                verts_top[next_i], verts_top[i]
            ])
        
    else:  # diamond
        # Diamond key
        half_w = width / 2
        half_d = depth / 2
        verts_bottom = [
            bm.verts.new((0, -half_d, 0)),
            bm.verts.new((half_w, 0, 0)),
            bm.verts.new((0, half_d, 0)),
            bm.verts.new((-half_w, 0, 0)),
        ]
        verts_top = [
            bm.verts.new((v.co.x, v.co.y, height)) for v in verts_bottom
        ]
        
        bm.faces.new(verts_bottom)
        bm.faces.new(list(reversed(verts_top)))
        for i in range(4):
            next_i = (i + 1) % 4
            bm.faces.new([
                verts_bottom[i], verts_bottom[next_i],
                verts_top[next_i], verts_top[i]
            ])
    
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    
    return obj


def build_micro_teeth(
    length: float,
    width: float = 10.0,
    tooth_height: float = 0.35,
    tooth_pitch: float = 1.0,
    name: str = "MicroTeeth",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Create anti-slide micro teeth for contact surfaces.
    
    Teeth profile:
    - Height: 0.3-0.4mm (invisible but effective)
    - 45° slopes (print without support)
    - Prevents lateral sliding when stacked
    
    Args:
        length: Teeth strip length
        width: Teeth strip width
        tooth_height: Individual tooth height
        tooth_pitch: Distance between teeth
        name: Object name
        location: Object location
    
    Returns:
        Blender object
    """
    ensure_bpy()
    
    bm = bmesh.new()
    
    half_width = width / 2
    num_teeth = int(length / tooth_pitch)
    
    # Create sawtooth profile along Y
    verts: list = []
    
    for i in range(num_teeth + 1):
        y = i * tooth_pitch
        # Base of tooth
        verts.extend([
            bm.verts.new((-half_width, y, 0)),
            bm.verts.new((half_width, y, 0)),
        ])
        # Peak of tooth (45° safe)
        if i < num_teeth:
            y_peak = y + tooth_pitch / 2
            verts.extend([
                bm.verts.new((-half_width, y_peak, tooth_height)),
                bm.verts.new((half_width, y_peak, tooth_height)),
            ])
    
    # Create faces connecting vertices
    # This creates a series of triangular teeth
    for i in range(0, len(verts) - 4, 4):
        # Left side triangle
        bm.faces.new([verts[i], verts[i + 2], verts[i + 4]])
        # Right side triangle
        bm.faces.new([verts[i + 1], verts[i + 5], verts[i + 3]])
        # Top face
        bm.faces.new([verts[i + 2], verts[i + 3], verts[i + 5], verts[i + 4]])
        # Front ramp
        bm.faces.new([verts[i], verts[i + 1], verts[i + 3], verts[i + 2]])
    
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    
    return obj


def build_connection_set(
    config: DerivedConfig,
    is_top: bool = True,
) -> list:
    """
    Build complete connection set based on config.
    
    Args:
        config: DerivedConfig with connection settings
        is_top: True for top connections, False for bottom
    
    Returns:
        List of connection objects
    """
    connection_type = config.connection_auto
    width = config.config.width
    depth = config.config.depth
    
    connections: list = []
    
    if connection_type == ConnectionType.DOVETAIL:
        # Four dovetails at corners
        positions = [
            (width * 0.2, depth * 0.2),
            (width * 0.8, depth * 0.2),
            (width * 0.2, depth * 0.8),
            (width * 0.8, depth * 0.8),
        ]
        for i, (x, y) in enumerate(positions):
            dt = build_dovetail(
                width=8, depth=4, height=6,
                is_male=is_top,
                name=f"Dovetail_{i}",
                location=(x - width / 2, y - depth / 2, 0)
            )
            if dt:
                connections.append(dt)
    
    elif connection_type == ConnectionType.MAGNET:
        # Four magnet pockets at corners
        positions = [
            (width * 0.15, depth * 0.15),
            (width * 0.85, depth * 0.15),
            (width * 0.15, depth * 0.85),
            (width * 0.85, depth * 0.85),
        ]
        for i, (x, y) in enumerate(positions):
            mp = build_magnet_pocket(
                diameter=config.MAGNET_DIA,
                depth=config.MAGNET_DEPTH,
                name=f"MagnetPocket_{i}",
                location=(x - width / 2, y - depth / 2, 0)
            )
            if mp:
                connections.append(mp)
    
    elif connection_type == ConnectionType.CLIP:
        # Two clips on long sides
        positions = [
            (width / 2, depth * 0.2),
            (width / 2, depth * 0.8),
        ]
        for i, (x, y) in enumerate(positions):
            clip = build_clip(
                is_male=is_top,
                name=f"Clip_{i}",
                location=(x - width / 2, y - depth / 2, 0)
            )
            if clip:
                connections.append(clip)
    
    # Add stacking keys (always)
    if is_top:
        # Triangle key front-left, diamond key back-right
        key1 = build_stacking_key(
            shape="triangle",
            name="StackKey_Triangle",
            location=(-width / 2 + 15, -depth / 2 + 15, 0)
        )
        key2 = build_stacking_key(
            shape="diamond",
            name="StackKey_Diamond",
            location=(width / 2 - 15, depth / 2 - 15, 0)
        )
        if key1:
            connections.append(key1)
        if key2:
            connections.append(key2)
    
    return connections
