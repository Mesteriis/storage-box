"""
Pattern Generation for Storage Box.

Creates rune patterns for Belovodye style:
- Chevron (protection)
- Knot (interrupted line)
- Wave (broken wave, not sine)
- Grid with dots
"""

import math
from typing import List, Tuple, Optional, Dict

try:
    import bpy
    import bmesh
    HAS_BPY = True
except ImportError:
    HAS_BPY = False


def ensure_bpy():
    """Check if bpy is available."""
    if not HAS_BPY:
        raise RuntimeError("Blender Python API (bpy) not available")


def create_chevron_pattern(
    width: float,
    height: float,
    spacing: float = 8.0,
    groove_width: float = 0.8,
    groove_depth: float = 0.35,
    name: str = "ChevronPattern",
) -> Optional["bpy.types.Object"]:
    """
    Create chevron (herringbone) rune pattern.
    
    Pattern: ╱╲╱╲╱╲╱╲
             ╲╱╲╱╲╱╲╱
    
    Args:
        width: Pattern width
        height: Pattern height (band height)
        spacing: Distance between chevron peaks
        groove_width: Width of groove lines
        groove_depth: Depth of inset groove
        name: Object name
    
    Returns:
        Blender object (for boolean subtraction)
    """
    ensure_bpy()
    
    bm = bmesh.new()
    
    num_chevrons = int(width / spacing) + 1
    half_height = height / 2
    
    for i in range(num_chevrons):
        x = i * spacing
        
        # Each chevron is two angled grooves meeting at a point
        # Top half: /\
        _create_groove_segment(
            bm, 
            x - spacing/2, half_height,
            x, 0,
            groove_width, groove_depth
        )
        _create_groove_segment(
            bm,
            x, 0,
            x + spacing/2, half_height,
            groove_width, groove_depth
        )
        
        # Bottom half: \/
        _create_groove_segment(
            bm,
            x - spacing/2, -half_height,
            x, 0,
            groove_width, groove_depth
        )
        _create_groove_segment(
            bm,
            x, 0,
            x + spacing/2, -half_height,
            groove_width, groove_depth
        )
    
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    return obj


def create_knot_pattern(
    width: float,
    height: float,
    spacing: float = 8.0,
    groove_width: float = 0.8,
    groove_depth: float = 0.35,
    gap_ratio: float = 0.3,
    name: str = "KnotPattern",
) -> Optional["bpy.types.Object"]:
    """
    Create knot (interrupted line) pattern.
    
    Pattern: ───  ───  ───
             ─────────────
    
    Args:
        width: Pattern width
        height: Pattern height (band height)
        spacing: Distance between segments
        groove_width: Width of groove lines
        groove_depth: Depth of inset groove
        gap_ratio: Ratio of gap to segment length
        name: Object name
    
    Returns:
        Blender object
    """
    ensure_bpy()
    
    bm = bmesh.new()
    
    segment_length = spacing * (1 - gap_ratio)
    gap_length = spacing * gap_ratio
    quarter_height = height / 4
    
    x = 0
    while x < width:
        # Top row (interrupted)
        _create_groove_segment(
            bm,
            x, quarter_height,
            x + segment_length, quarter_height,
            groove_width, groove_depth
        )
        x += spacing
    
    # Bottom row (continuous)
    _create_groove_segment(
        bm,
        0, -quarter_height,
        width, -quarter_height,
        groove_width, groove_depth
    )
    
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    return obj


def create_wave_pattern(
    width: float,
    height: float,
    spacing: float = 8.0,
    groove_width: float = 0.8,
    groove_depth: float = 0.35,
    name: str = "WavePattern",
) -> Optional["bpy.types.Object"]:
    """
    Create broken wave pattern (not sine wave!).
    
    Pattern: ╱╲_╱╲_╱╲
             ╲╱ ╲╱ ╲╱
    
    Args:
        width: Pattern width
        height: Pattern height
        spacing: Wave period
        groove_width: Width of groove lines
        groove_depth: Depth of groove
        name: Object name
    
    Returns:
        Blender object
    """
    ensure_bpy()
    
    bm = bmesh.new()
    
    num_waves = int(width / spacing) + 1
    quarter_height = height / 4
    
    for i in range(num_waves):
        x = i * spacing
        
        # Rising edge
        _create_groove_segment(
            bm,
            x, -quarter_height,
            x + spacing * 0.25, quarter_height,
            groove_width, groove_depth
        )
        
        # Falling edge
        _create_groove_segment(
            bm,
            x + spacing * 0.25, quarter_height,
            x + spacing * 0.5, -quarter_height,
            groove_width, groove_depth
        )
        
        # Flat section (the "broken" part)
        _create_groove_segment(
            bm,
            x + spacing * 0.5, -quarter_height,
            x + spacing * 0.75, -quarter_height,
            groove_width, groove_depth
        )
    
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    return obj


def create_pattern_band(
    pattern_type: str,
    width: float,
    band_height: float,
    extrusion_length: float,
    groove_width: float = 0.8,
    groove_depth: float = 0.35,
    spacing: float = 8.0,
    name: str = "PatternBand",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Create a 3D pattern band for boolean subtraction.
    
    Args:
        pattern_type: "chevron", "knot", "wave", "grid"
        width: Band width (pattern repeat direction)
        band_height: Band height
        extrusion_length: How deep to extrude (Y axis)
        groove_width: Width of groove lines
        groove_depth: Depth of grooves (Z axis)
        spacing: Pattern spacing
        name: Object name
        location: Object location
    
    Returns:
        Blender object for boolean subtraction
    """
    ensure_bpy()
    
    # Create base box for the band
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    band = bpy.context.active_object
    band.name = name
    band.scale = (width, extrusion_length, band_height)
    bpy.ops.object.transform_apply(scale=True)
    
    # Create pattern grooves based on type
    pattern_funcs = {
        "chevron": create_chevron_pattern,
        "knot": create_knot_pattern,
        "wave": create_wave_pattern,
    }
    
    func = pattern_funcs.get(pattern_type)
    if func:
        pattern = func(
            width=width,
            height=band_height,
            spacing=spacing,
            groove_width=groove_width,
            groove_depth=groove_depth,
        )
        
        if pattern:
            # Position pattern and extrude for boolean
            pattern.location = (location[0], location[1], location[2])
            
            # Add solidify modifier to give it depth
            mod = pattern.modifiers.new(name="Solidify", type='SOLIDIFY')
            mod.thickness = extrusion_length
            mod.offset = 0
            
            bpy.context.view_layer.objects.active = pattern
            bpy.ops.object.modifier_apply(modifier=mod.name)
            
            return pattern
    
    return band


def _create_groove_segment(
    bm: "bmesh.types.BMesh",
    x1: float, z1: float,
    x2: float, z2: float,
    width: float,
    depth: float,
) -> None:
    """
    Create a groove segment in bmesh.
    
    Args:
        bm: BMesh to add geometry to
        x1, z1: Start point
        x2, z2: End point
        width: Groove width
        depth: Groove depth (Y direction)
    """
    # Calculate perpendicular offset for width
    dx = x2 - x1
    dz = z2 - z1
    length = math.sqrt(dx*dx + dz*dz)
    
    if length < 0.001:
        return
    
    # Perpendicular unit vector
    px = -dz / length * (width / 2)
    pz = dx / length * (width / 2)
    
    # Create vertices for groove (rectangular cross-section)
    # Front face (Y=0)
    v1 = bm.verts.new((x1 + px, 0, z1 + pz))
    v2 = bm.verts.new((x1 - px, 0, z1 - pz))
    v3 = bm.verts.new((x2 - px, 0, z2 - pz))
    v4 = bm.verts.new((x2 + px, 0, z2 + pz))
    
    # Back face (Y=depth)
    v5 = bm.verts.new((x1 + px, depth, z1 + pz))
    v6 = bm.verts.new((x1 - px, depth, z1 - pz))
    v7 = bm.verts.new((x2 - px, depth, z2 - pz))
    v8 = bm.verts.new((x2 + px, depth, z2 + pz))
    
    # Create faces
    try:
        bm.faces.new([v1, v2, v3, v4])  # Front
        bm.faces.new([v8, v7, v6, v5])  # Back
        bm.faces.new([v1, v4, v8, v5])  # Top
        bm.faces.new([v2, v6, v7, v3])  # Bottom
        bm.faces.new([v1, v5, v6, v2])  # Left
        bm.faces.new([v4, v3, v7, v8])  # Right
    except ValueError:
        # Face already exists or invalid geometry
        pass
