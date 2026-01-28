"""
Geometry Primitives for Storage Box System.

Basic geometric shapes and profiles using Blender Python API (bpy).
All functions work in headless mode for scripted generation.
"""

import math
from typing import Tuple, List, Optional

# Try to import bpy, but allow running without Blender for testing
try:
    import bpy
    import bmesh
    from mathutils import Vector, Matrix
    HAS_BPY = True
except ImportError:
    HAS_BPY = False
    print("Warning: bpy not available, geometry functions will not work")


def ensure_bpy():
    """Check if bpy is available."""
    if not HAS_BPY:
        raise RuntimeError("Blender Python API (bpy) not available")


def create_box(
    width: float, 
    depth: float, 
    height: float,
    name: str = "Box",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Create a box mesh.
    
    Args:
        width: X dimension
        depth: Y dimension
        height: Z dimension
        name: Object name
        location: Object location
    
    Returns:
        Blender object
    """
    ensure_bpy()
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=location,
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (width, depth, height)
    
    # Apply scale
    bpy.ops.object.transform_apply(scale=True)
    
    return obj


def create_cylinder(
    radius: float,
    height: float,
    vertices: int = 32,
    name: str = "Cylinder",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Create a cylinder mesh.
    
    Args:
        radius: Cylinder radius
        height: Cylinder height
        vertices: Number of vertices around circumference
        name: Object name
        location: Object location
    
    Returns:
        Blender object
    """
    ensure_bpy()
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=height,
        vertices=vertices,
        location=location,
    )
    obj = bpy.context.active_object
    obj.name = name
    
    return obj


def create_plane(
    width: float,
    depth: float,
    name: str = "Plane",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Create a plane mesh.
    
    Args:
        width: X dimension
        depth: Y dimension
        name: Object name
        location: Object location
    
    Returns:
        Blender object
    """
    ensure_bpy()
    
    bpy.ops.mesh.primitive_plane_add(
        size=1,
        location=location,
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (width, depth, 1)
    
    bpy.ops.object.transform_apply(scale=True)
    
    return obj


def create_v_rail(
    length: float,
    width: float,
    depth: float,
    angle: float = 45.0,
    name: str = "VRail",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Create a V-profile rail for self-centering drawer slides.
    
    Args:
        length: Rail length (along Y axis)
        width: Rail width (X axis)
        depth: Rail depth (Z axis)
        angle: V angle in degrees
        name: Object name
        location: Object location
    
    Returns:
        Blender object
    """
    ensure_bpy()
    
    # Create V profile using bmesh
    bm = bmesh.new()
    
    # Calculate V profile vertices
    half_width = width / 2
    rad = math.radians(angle / 2)
    v_depth = half_width * math.tan(rad)
    
    # Profile vertices (front face)
    verts_front = [
        bm.verts.new((-half_width, 0, 0)),           # Left top
        bm.verts.new((0, 0, -v_depth)),              # Center bottom (V point)
        bm.verts.new((half_width, 0, 0)),            # Right top
        bm.verts.new((half_width, 0, depth)),        # Right top back
        bm.verts.new((-half_width, 0, depth)),       # Left top back
    ]
    
    # Profile vertices (back face)
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
    
    # Side faces (connect front to back)
    for i in range(5):
        next_i = (i + 1) % 5
        bm.faces.new([
            verts_front[i], verts_front[next_i],
            verts_back[next_i], verts_back[i]
        ])
    
    # Create mesh and object
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    
    return obj


def create_v_groove(
    length: float,
    width: float,
    depth: float,
    angle: float = 45.0,
    name: str = "VGroove",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Create a V-groove (inverse of V-rail) for drawer sides.
    
    Args:
        length: Groove length (along Y axis)
        width: Groove width (X axis)
        depth: Groove depth (Z axis, into material)
        angle: V angle in degrees
        name: Object name
        location: Object location
    
    Returns:
        Blender object (for boolean subtraction)
    """
    ensure_bpy()
    
    bm = bmesh.new()
    
    # V groove is inverted V rail
    half_width = width / 2
    rad = math.radians(angle / 2)
    v_depth = half_width * math.tan(rad)
    
    # Profile vertices (groove pointing up into material)
    verts_front = [
        bm.verts.new((-half_width, 0, 0)),
        bm.verts.new((0, 0, v_depth)),  # V point goes up
        bm.verts.new((half_width, 0, 0)),
    ]
    
    verts_back = [
        bm.verts.new((-half_width, length, 0)),
        bm.verts.new((0, length, v_depth)),
        bm.verts.new((half_width, length, 0)),
    ]
    
    # Create faces
    bm.faces.new([verts_front[0], verts_front[1], verts_front[2]])
    bm.faces.new([verts_back[2], verts_back[1], verts_back[0]])
    
    # Side faces
    bm.faces.new([verts_front[0], verts_back[0], 
                  verts_back[1], verts_front[1]])
    bm.faces.new([verts_front[1], verts_back[1], 
                  verts_back[2], verts_front[2]])
    bm.faces.new([verts_front[2], verts_back[2], 
                  verts_back[0], verts_front[0]])
    
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    
    return obj


def create_chamfer_profile(
    width: float,
    angle: float = 45.0,
    secondary_width: float = 0.0,
    secondary_angle: float = 22.0,
) -> List[Tuple[float, float]]:
    """
    Create a 2D chamfer profile (for Belovodye two-step chamfer).
    
    Args:
        width: Primary chamfer width
        angle: Primary chamfer angle (degrees)
        secondary_width: Secondary chamfer width (0 for single chamfer)
        secondary_angle: Secondary chamfer angle (degrees)
    
    Returns:
        List of (x, z) coordinate tuples for profile
    """
    profile = [(0, 0)]  # Start at corner
    
    # Primary chamfer
    rad1 = math.radians(angle)
    x1 = width * math.cos(rad1)
    z1 = width * math.sin(rad1)
    profile.append((x1, z1))
    
    # Secondary chamfer (Belovodye style)
    if secondary_width > 0:
        rad2 = math.radians(secondary_angle)
        x2 = x1 + secondary_width * math.cos(rad2)
        z2 = z1 + secondary_width * math.sin(rad2)
        profile.append((x2, z2))
    
    return profile


def create_fillet_profile(
    radius: float,
    segments: int = 8,
) -> List[Tuple[float, float]]:
    """
    Create a 2D fillet (rounded corner) profile.
    
    Args:
        radius: Fillet radius
        segments: Number of segments in arc
    
    Returns:
        List of (x, z) coordinate tuples for profile
    """
    profile = []
    for i in range(segments + 1):
        angle = (math.pi / 2) * (i / segments)
        x = radius * (1 - math.cos(angle))
        z = radius * (1 - math.sin(angle))
        profile.append((x, z))
    return profile


def create_dovetail_profile(
    width: float,
    depth: float,
    angle: float = 14.0,
) -> List[Tuple[float, float]]:
    """
    Create a 2D dovetail profile.
    
    Args:
        width: Dovetail width at top
        depth: Dovetail depth
        angle: Dovetail angle (degrees)
    
    Returns:
        List of (x, z) coordinate tuples
    """
    rad = math.radians(angle)
    offset = depth * math.tan(rad)
    
    half_top = width / 2
    half_bottom = half_top + offset
    
    return [
        (-half_top, 0),
        (-half_bottom, depth),
        (half_bottom, depth),
        (half_top, 0),
    ]


def extrude_profile(
    profile: List[Tuple[float, float]],
    length: float,
    name: str = "Extruded",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Extrude a 2D profile along Y axis.
    
    Args:
        profile: List of (x, z) coordinates
        length: Extrusion length
        name: Object name
        location: Object location
    
    Returns:
        Blender object
    """
    ensure_bpy()
    
    bm = bmesh.new()
    
    # Create front vertices
    verts_front = [bm.verts.new((x, 0, z)) for x, z in profile]
    
    # Create back vertices
    verts_back = [bm.verts.new((x, length, z)) for x, z in profile]
    
    # Create front face
    if len(verts_front) >= 3:
        bm.faces.new(verts_front)
    
    # Create back face (reversed)
    if len(verts_back) >= 3:
        bm.faces.new(list(reversed(verts_back)))
    
    # Create side faces
    n = len(profile)
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
