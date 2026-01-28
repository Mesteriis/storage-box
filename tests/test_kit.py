"""
Test Kit for Storage Box calibration.

Print-before-full-build test pieces for tuning tolerances.
"""

from typing import Optional, Tuple

try:
    import bpy
    HAS_BPY = True
except ImportError:
    HAS_BPY = False

from storage_box.config.derived_config import DerivedConfig
from storage_box.config.enums import WhiskerVariant


def ensure_bpy():
    """Check if bpy is available."""
    if not HAS_BPY:
        raise RuntimeError("Blender Python API (bpy) not available")


def build_rail_clearance_test(
    config: DerivedConfig,
    name: str = "RailClearanceTest",
) -> Optional["bpy.types.Object"]:
    """
    Create rail clearance test piece with 3 tolerance levels.
    
    Tests slide tolerance: 0.25mm / 0.30mm / 0.35mm
    Print this first to find optimal clearance for your printer.
    
    Piece is ~10 min print time.
    
    Args:
        config: DerivedConfig
        name: Object name
    
    Returns:
        Test piece object
    """
    ensure_bpy()
    
    from ..geometry.boolean_ops import boolean_union, boolean_difference
    from .rails import build_v_rail, build_v_groove
    
    # Base plate
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, 3)
    )
    base = bpy.context.active_object
    if base is None:
        return None
    
    base.name = name
    base.scale = (60, 25, 6)
    bpy.ops.object.transform_apply(scale=True)
    
    # Three test sections with different clearances
    clearances = [0.25, 0.30, 0.35]
    
    for i, clearance in enumerate(clearances):
        x_pos = -20 + i * 20
        
        # Shell-side rail
        rail = build_v_rail(
            length=20,
            width=5.0,
            depth=4.0,
            name=f"TestRail_{clearance}",
            location=(x_pos, 0, 6)
        )
        if rail:
            boolean_union(base, rail)
        
        # Drawer-side groove (with specific clearance)
        groove = build_v_groove(
            length=20,
            width=5.0,
            depth=4.0,
            clearance=clearance,
            name=f"TestGroove_{clearance}",
            location=(x_pos, 0, 6)
        )
        if groove:
            boolean_difference(base, groove)
    
    # Add labels (simplified as rectangular markers)
    _add_test_labels(base, clearances)
    
    return base


def build_snap_fit_test(
    config: DerivedConfig,
    name: str = "SnapFitTest",
) -> Optional["bpy.types.Object"]:
    """
    Create snap-fit test piece with 3 spring stiffnesses.
    
    Tests different tab thicknesses: 0.8mm / 1.0mm / 1.2mm
    Find the snap that holds but releases easily.
    
    Args:
        config: DerivedConfig
        name: Object name
    
    Returns:
        Test piece object
    """
    ensure_bpy()
    
    from ..geometry.boolean_ops import boolean_union
    
    # Base plate
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, 4)
    )
    base = bpy.context.active_object
    if base is None:
        return None
    
    base.name = name
    base.scale = (50, 30, 8)
    bpy.ops.object.transform_apply(scale=True)
    
    # Three spring tabs with different thicknesses
    thicknesses = [0.8, 1.0, 1.2]
    
    for i, thick in enumerate(thicknesses):
        x_pos = -15 + i * 15
        _add_spring_tab(base, thick, 8.0, location=(x_pos, 0, 8))
    
    return base


def build_magnet_pressfit_test(
    config: DerivedConfig,
    name: str = "MagnetPressfitTest",
) -> Optional["bpy.types.Object"]:
    """
    Create magnet pocket test with 3 diameters.
    
    Tests pocket diameters: 6.0mm / 6.1mm / 6.2mm
    For 6x3mm magnets - find the pressfit that holds.
    
    Args:
        config: DerivedConfig
        name: Object name
    
    Returns:
        Test piece object
    """
    ensure_bpy()
    
    from ..geometry.boolean_ops import boolean_batch_difference
    
    # Base plate
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, 3)
    )
    base = bpy.context.active_object
    if base is None:
        return None
    
    base.name = name
    base.scale = (45, 20, 6)
    bpy.ops.object.transform_apply(scale=True)
    
    # Three pockets with different diameters
    diameters = [6.0, 6.1, 6.2]
    pocket_depth = 3.2
    
    pockets: list["bpy.types.Object"] = []
    for i, dia in enumerate(diameters):
        x_pos = -12 + i * 12
        
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=32,
            radius=dia / 2,
            depth=pocket_depth,
            location=(x_pos, 0, 6 - pocket_depth / 2)
        )
        pocket = bpy.context.active_object
        if pocket is not None:
            pocket.name = f"Pocket_{dia}"
            pockets.append(pocket)
    
    if pockets:
        boolean_batch_difference(base, pockets)
    
    return base


def build_whisker_test_kit(
    config: DerivedConfig,
) -> list:
    """
    Create spring whisker test kit (6 variants).
    
    Variants:
    - SOFT_S:  0.8mm × 12mm (soft, short)
    - SOFT_L:  0.8mm × 18mm (soft, long)
    - MED_S:   1.0mm × 12mm (medium, short)
    - MED_L:   1.0mm × 18mm (medium, long - standard)
    - FIRM_S:  1.2mm × 12mm (firm, short)
    - FIRM_L:  1.2mm × 18mm (firm, long)
    
    Args:
        config: DerivedConfig
    
    Returns:
        List of whisker insert objects
    """
    variants = [
        (WhiskerVariant.SOFT_S, 0.8, 12.0),
        (WhiskerVariant.SOFT_L, 0.8, 18.0),
        (WhiskerVariant.MED_S, 1.0, 12.0),
        (WhiskerVariant.MED_L, 1.0, 18.0),
        (WhiskerVariant.FIRM_S, 1.2, 12.0),
        (WhiskerVariant.FIRM_L, 1.2, 18.0),
    ]
    
    whiskers: list = []
    
    for variant, thickness, length in variants:
        whisker = _build_whisker_insert(
            thickness=thickness,
            length=length,
            name=f"Whisker_{variant.value}",
        )
        if whisker:
            whiskers.append(whisker)
    
    return whiskers


def _build_whisker_insert(
    thickness: float,
    length: float,
    name: str,
) -> Optional["bpy.types.Object"]:
    """
    Build single spring whisker insert.
    
    Insert snaps into pocket on shell side.
    Whisker presses against drawer for anti-wobble.
    """
    ensure_bpy()
    
    import bmesh
    
    bm = bmesh.new()
    
    # Snap base (rectangular)
    base_w = 6.0
    base_d = 4.0
    base_h = 3.0
    
    # Whisker arm
    arm_width = 3.0
    
    # Base vertices
    half_w = base_w / 2
    half_d = base_d / 2
    
    verts = [
        # Base block
        bm.verts.new((-half_w, -half_d, 0)),
        bm.verts.new((half_w, -half_d, 0)),
        bm.verts.new((half_w, half_d, 0)),
        bm.verts.new((-half_w, half_d, 0)),
        bm.verts.new((-half_w, -half_d, base_h)),
        bm.verts.new((half_w, -half_d, base_h)),
        bm.verts.new((half_w, half_d, base_h)),
        bm.verts.new((-half_w, half_d, base_h)),
        # Whisker arm start
        bm.verts.new((-arm_width / 2, half_d, base_h - thickness)),
        bm.verts.new((arm_width / 2, half_d, base_h - thickness)),
        bm.verts.new((arm_width / 2, half_d, base_h)),
        bm.verts.new((-arm_width / 2, half_d, base_h)),
        # Whisker arm end
        bm.verts.new((-arm_width / 2, half_d + length, base_h - thickness * 0.7)),
        bm.verts.new((arm_width / 2, half_d + length, base_h - thickness * 0.7)),
        bm.verts.new((arm_width / 2, half_d + length, base_h - thickness * 0.7 + thickness)),
        bm.verts.new((-arm_width / 2, half_d + length, base_h - thickness * 0.7 + thickness)),
    ]
    
    # Base box faces
    bm.faces.new([verts[0], verts[1], verts[2], verts[3]])  # bottom
    bm.faces.new([verts[7], verts[6], verts[5], verts[4]])  # top (partial)
    bm.faces.new([verts[0], verts[4], verts[5], verts[1]])  # front
    bm.faces.new([verts[0], verts[3], verts[7], verts[4]])  # left
    bm.faces.new([verts[1], verts[5], verts[6], verts[2]])  # right
    
    # Whisker arm faces
    bm.faces.new([verts[8], verts[9], verts[13], verts[12]])  # bottom
    bm.faces.new([verts[10], verts[11], verts[15], verts[14]])  # top
    bm.faces.new([verts[8], verts[12], verts[15], verts[11]])  # left
    bm.faces.new([verts[9], verts[10], verts[14], verts[13]])  # right
    bm.faces.new([verts[12], verts[13], verts[14], verts[15]])  # end
    
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    return obj


def _add_spring_tab(
    base: "bpy.types.Object",
    thickness: float,
    length: float,
    location: Tuple[float, float, float],
) -> None:
    """Add spring tab to test piece."""
    from ..geometry.boolean_ops import boolean_union
    
    import bmesh
    
    bm = bmesh.new()
    
    width = 6.0
    half_w = width / 2
    
    # Cantilever tab profile
    verts = [
        bm.verts.new((-half_w, 0, 0)),
        bm.verts.new((half_w, 0, 0)),
        bm.verts.new((half_w, length, thickness)),
        bm.verts.new((-half_w, length, thickness)),
        bm.verts.new((-half_w, 0, thickness)),
        bm.verts.new((half_w, 0, thickness)),
    ]
    
    # Faces
    bm.faces.new([verts[0], verts[1], verts[5], verts[4]])  # back
    bm.faces.new([verts[4], verts[5], verts[2], verts[3]])  # top
    bm.faces.new([verts[0], verts[4], verts[3], verts[2], verts[1]])  # bottom
    bm.faces.new([verts[0], verts[2], verts[3]])  # left (triangle)
    bm.faces.new([verts[1], verts[2], verts[5]])  # right (triangle)
    
    mesh = bpy.data.meshes.new("SpringTab")
    bm.to_mesh(mesh)
    bm.free()
    
    tab = bpy.data.objects.new("SpringTab", mesh)
    bpy.context.collection.objects.link(tab)
    tab.location = location
    
    boolean_union(base, tab)


def _add_test_labels(
    base: "bpy.types.Object",
    values: list,
) -> None:
    """Add visual markers for test values."""
    from ..geometry.boolean_ops import boolean_batch_difference
    
    # Simple notches as labels (real implementation would use text)
    markers: list["bpy.types.Object"] = []
    
    for i, val in enumerate(values):
        x_pos = -20 + i * 20
        num_notches = int(val * 10)  # 0.25 -> 2, 0.30 -> 3, 0.35 -> 3
        
        for j in range(num_notches):
            bpy.ops.mesh.primitive_cube_add(
                size=1,
                location=(x_pos - 3 + j * 2, -12, 0)
            )
            notch = bpy.context.active_object
            if notch is not None:
                notch.scale = (1, 2, 3)
                bpy.ops.object.transform_apply(scale=True)
                markers.append(notch)
    
    if markers:
        boolean_batch_difference(base, markers)


def build_complete_test_kit(
    config: DerivedConfig,
) -> dict:
    """
    Build complete calibration test kit.
    
    Returns dict with all test pieces:
    - rail_test: Rail clearance test (3 levels)
    - snap_test: Snap-fit test (3 stiffnesses)
    - magnet_test: Magnet pressfit test (3 diameters)
    - whiskers: Spring whisker set (6 variants)
    
    Total print time: ~45 minutes
    
    Args:
        config: DerivedConfig
    
    Returns:
        Dict of test piece objects
    """
    kit = {
        "rail_test": build_rail_clearance_test(config),
        "snap_test": build_snap_fit_test(config),
        "magnet_test": build_magnet_pressfit_test(config),
        "whiskers": build_whisker_test_kit(config),
    }
    
    return kit
