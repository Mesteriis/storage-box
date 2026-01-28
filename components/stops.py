"""
Stop System for Storage Box drawer.

Two-stage stops with acoustic options.
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
from ..config.enums import SoundProfile


def ensure_bpy():
    """Check if bpy is available."""
    if not HAS_BPY:
        raise RuntimeError("Blender Python API (bpy) not available")


def build_two_stage_stop(
    config: DerivedConfig,
    name: str = "TwoStageStop",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Create two-stage drawer stop mechanism.
    
    Stage 1: PETG spring tab (1.2mm thick, 8mm long)
             - Soft tactile stop
             - 15° entry angle for smooth engagement
    
    Stage 2: Hard physical stop (3mm height)
             - Prevents drawer ejection on hard pull
             - Acts as safety backup
    
    Args:
        config: DerivedConfig with stop parameters
        name: Object name
        location: Object location
    
    Returns:
        Blender object
    """
    ensure_bpy()
    
    bm = bmesh.new()
    
    tab_thickness = config.STOP1_THICKNESS  # 1.2mm
    tab_length = config.STOP1_LENGTH        # 8mm
    hard_stop_height = config.STOP2_HEIGHT  # 3mm
    
    # Base block for the stop assembly
    base_width = 10.0
    base_depth = tab_length + 5.0
    base_height = hard_stop_height + 2.0
    
    # Spring tab profile with 15° entry angle
    entry_angle_rad = math.radians(15)
    entry_length = tab_thickness / math.tan(entry_angle_rad)
    
    # Create spring tab vertices
    verts = [
        # Base rectangle
        bm.verts.new((-base_width / 2, 0, 0)),
        bm.verts.new((base_width / 2, 0, 0)),
        bm.verts.new((base_width / 2, base_depth, 0)),
        bm.verts.new((-base_width / 2, base_depth, 0)),
        # Top with tab
        bm.verts.new((-base_width / 2, 0, base_height)),
        bm.verts.new((base_width / 2, 0, base_height)),
        bm.verts.new((base_width / 2, tab_length, base_height)),
        bm.verts.new((-base_width / 2, tab_length, base_height)),
        # Tab tip with entry angle
        bm.verts.new((-base_width / 2, tab_length + entry_length,
                      base_height - tab_thickness)),
        bm.verts.new((base_width / 2, tab_length + entry_length,
                      base_height - tab_thickness)),
        # Hard stop
        bm.verts.new((-base_width / 2, base_depth, hard_stop_height)),
        bm.verts.new((base_width / 2, base_depth, hard_stop_height)),
    ]
    
    # Create faces
    # Bottom
    bm.faces.new([verts[0], verts[1], verts[2], verts[3]])
    # Front
    bm.faces.new([verts[0], verts[4], verts[5], verts[1]])
    # Back
    bm.faces.new([verts[2], verts[11], verts[10], verts[3]])
    # Left side
    bm.faces.new([verts[0], verts[3], verts[10], verts[8], verts[7], verts[4]])
    # Right side
    bm.faces.new([verts[1], verts[5], verts[6], verts[9], verts[11], verts[2]])
    # Top surfaces
    bm.faces.new([verts[4], verts[7], verts[6], verts[5]])
    bm.faces.new([verts[7], verts[8], verts[9], verts[6]])
    # Hard stop top
    bm.faces.new([verts[10], verts[11], verts[9], verts[8]])
    
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    
    return obj


def build_acoustic_tab(
    width: float = 0.8,
    height: float = 6.0,
    length: float = 18.0,
    name: str = "AcousticTab",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Create acoustic resonator tab for MECH_CLICK sound profile.
    
    The tab resonates when contacted by the stop mechanism,
    producing a satisfying click sound like quality hardware.
    
    Dimensions: 0.8 x 6 x 18mm (thin enough to resonate)
    
    Args:
        width: Tab thickness (0.8mm for resonance)
        height: Tab height
        length: Tab length (cantilever)
        name: Object name
        location: Object location
    
    Returns:
        Blender object
    """
    ensure_bpy()
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    if obj is not None:
        obj.name = name
        obj.scale = (width, length, height)
        bpy.ops.object.transform_apply(scale=True)
    
    return obj


def build_soft_damper(
    config: DerivedConfig,
    name: str = "SoftDamper",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Create soft-close damper pocket for SILENT sound profile.
    
    Pocket designed to hold:
    - TPU printed bumper
    - Silicone bumpstop (Ø6-8mm)
    
    Damper slows last 10mm of travel for whisper-quiet closing.
    
    Args:
        config: DerivedConfig
        name: Object name
        location: Object location
    
    Returns:
        Blender object (pocket for boolean subtraction)
    """
    ensure_bpy()
    
    # Pocket for Ø8mm silicone bumper
    pocket_diameter = 8.5  # With clearance
    pocket_depth = 5.0
    
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24,
        radius=pocket_diameter / 2,
        depth=pocket_depth,
        location=location,
    )
    obj = bpy.context.active_object
    if obj is not None:
        obj.name = name
    
    return obj


def build_release_slot(
    width: float = 15.0,
    height: float = 5.0,
    depth: float = 3.0,
    name: str = "ReleaseSlot",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Create release slot for drawer removal.
    
    Slot at bottom of shell allows:
    - Fingernail/screwdriver access
    - Press down on spring tab to release drawer
    - Full drawer removal without damage
    
    Dimensions: 15 x 5mm (comfortable for finger access)
    
    Args:
        width: Slot width
        height: Slot height  
        depth: Slot depth (into shell)
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
        obj.scale = (width, depth, height)
        bpy.ops.object.transform_apply(scale=True)
    
    return obj


def build_stop_set(
    config: DerivedConfig,
    sound_profile: SoundProfile,
) -> list:
    """
    Build complete stop assembly based on sound profile.
    
    SILENT: Two-stage stop + soft damper pocket
    SOFT_CLICK: Two-stage stop with optimized spring
    MECH_CLICK: Two-stage stop + acoustic tab
    
    Args:
        config: DerivedConfig
        sound_profile: Desired sound profile
    
    Returns:
        List of stop objects
    """
    stops: list = []
    
    # Two-stage stop is always included
    stop = build_two_stage_stop(
        config,
        name="TwoStageStop",
        location=(0, 0, 0)
    )
    if stop:
        stops.append(stop)
    
    if sound_profile == SoundProfile.SILENT:
        # Add soft damper pocket
        damper = build_soft_damper(
            config,
            name="SoftDamper",
            location=(0, -15, 0)  # Before stop
        )
        if damper:
            stops.append(damper)
    
    elif sound_profile == SoundProfile.MECH_CLICK:
        # Add acoustic resonator tab
        tab = build_acoustic_tab(
            name="AcousticTab",
            location=(0, 5, 0)  # Adjacent to stop
        )
        if tab:
            stops.append(tab)
    
    # Release slot for all profiles
    release = build_release_slot(
        width=config.RELEASE_SLOT_W,
        height=config.RELEASE_SLOT_H,
        name="ReleaseSlot",
        location=(0, 0, -config.wall_thickness)
    )
    if release:
        stops.append(release)
    
    return stops
