"""
Divider System for Storage Box.

Removable dividers with snap and lock modes.
"""

from typing import Optional, Tuple

try:
    import bpy
    import bmesh
    HAS_BPY = True
except ImportError:
    HAS_BPY = False

from ..config.derived_config import DerivedConfig
from ..config.enums import DividerMode


def ensure_bpy():
    """Check if bpy is available."""
    if not HAS_BPY:
        raise RuntimeError("Blender Python API (bpy) not available")


def build_divider(
    length: float,
    height: float,
    thickness: float = 1.6,
    mode: DividerMode = DividerMode.SNAP,
    has_tab: bool = True,
    tab_position: str = "center",
    name: str = "Divider",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Create a single divider piece.
    
    Divider features:
    - Tab at bottom for slot engagement
    - SNAP mode: rounded tab edges for easy removal
    - LOCK mode: locking tab with catch
    - Optional grid label position
    
    Args:
        length: Divider length
        height: Divider height (above slot)
        thickness: Divider thickness
        mode: SNAP (easy remove) or LOCK (secure)
        has_tab: Include bottom tab for slot
        tab_position: "center", "left", "right", or "full"
        name: Object name
        location: Object location
    
    Returns:
        Blender object
    """
    ensure_bpy()
    
    bm = bmesh.new()
    
    half_len = length / 2
    half_thick = thickness / 2
    
    # Slot dimensions
    slot_depth = 3.0
    slot_width = 2.4
    
    # Main divider body
    verts_front = [
        bm.verts.new((-half_len, -half_thick, 0)),
        bm.verts.new((half_len, -half_thick, 0)),
        bm.verts.new((half_len, -half_thick, height)),
        bm.verts.new((-half_len, -half_thick, height)),
    ]
    
    verts_back = [
        bm.verts.new((-half_len, half_thick, 0)),
        bm.verts.new((half_len, half_thick, 0)),
        bm.verts.new((half_len, half_thick, height)),
        bm.verts.new((-half_len, half_thick, height)),
    ]
    
    # Create main body faces
    bm.faces.new(verts_front)
    bm.faces.new(list(reversed(verts_back)))
    for i in range(4):
        next_i = (i + 1) % 4
        bm.faces.new([verts_front[i], verts_front[next_i],
                      verts_back[next_i], verts_back[i]])
    
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    
    # Add tab if requested
    if has_tab:
        tab = _build_divider_tab(
            length if tab_position == "full" else length * 0.4,
            slot_depth,
            slot_width - 0.2,  # Clearance
            mode,
        )
        if tab:
            # Position tab at center-bottom
            if tab_position == "left":
                tab.location = (-half_len * 0.6, 0, -slot_depth / 2)
            elif tab_position == "right":
                tab.location = (half_len * 0.6, 0, -slot_depth / 2)
            else:
                tab.location = (0, 0, -slot_depth / 2)
            
            from ..geometry.boolean_ops import boolean_union
            boolean_union(obj, tab)
    
    return obj


def _build_divider_tab(
    length: float,
    depth: float,
    width: float,
    mode: DividerMode,
) -> Optional["bpy.types.Object"]:
    """
    Create tab for slot engagement.
    
    SNAP: Rounded edges for easy insertion/removal
    LOCK: Has catch that clicks into keyhole
    """
    ensure_bpy()
    
    bm = bmesh.new()
    
    half_len = length / 2
    half_w = width / 2
    
    if mode == DividerMode.SNAP:
        # Simple rounded tab
        verts = [
            bm.verts.new((-half_len + 1, -half_w, 0)),
            bm.verts.new((-half_len, -half_w, -depth * 0.3)),
            bm.verts.new((-half_len, -half_w, -depth)),
            bm.verts.new((half_len, -half_w, -depth)),
            bm.verts.new((half_len, -half_w, -depth * 0.3)),
            bm.verts.new((half_len - 1, -half_w, 0)),
        ]
        verts_back = [
            bm.verts.new((v.co.x, half_w, v.co.z)) for v in verts
        ]
        
        bm.faces.new(verts)
        bm.faces.new(list(reversed(verts_back)))
        for i in range(len(verts)):
            next_i = (i + 1) % len(verts)
            bm.faces.new([verts[i], verts[next_i],
                          verts_back[next_i], verts_back[i]])
    
    else:  # LOCK mode
        # Tab with locking catch
        catch_height = 0.8
        verts = [
            bm.verts.new((-half_len, -half_w, 0)),
            bm.verts.new((-half_len, -half_w, -depth + catch_height)),
            bm.verts.new((-half_len - 0.5, -half_w, -depth)),
            bm.verts.new((half_len + 0.5, -half_w, -depth)),
            bm.verts.new((half_len, -half_w, -depth + catch_height)),
            bm.verts.new((half_len, -half_w, 0)),
        ]
        verts_back = [
            bm.verts.new((v.co.x, half_w, v.co.z)) for v in verts
        ]
        
        bm.faces.new(verts)
        bm.faces.new(list(reversed(verts_back)))
        for i in range(len(verts)):
            next_i = (i + 1) % len(verts)
            bm.faces.new([verts[i], verts[next_i],
                          verts_back[next_i], verts_back[i]])
    
    mesh = bpy.data.meshes.new("DividerTab")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("DividerTab", mesh)
    bpy.context.collection.objects.link(obj)
    
    return obj


def build_divider_set(
    config: DerivedConfig,
) -> list:
    """
    Build complete set of dividers for drawer.
    
    Args:
        config: DerivedConfig with divider settings
    
    Returns:
        List of divider objects
    """
    cols, rows = config.divider_count
    if cols == 0 and rows == 0:
        return []
    
    width = config.drawer_width - 2 * config.wall_thickness
    depth = config.drawer_depth - 2 * config.wall_thickness
    height = config.drawer_inner_depth - 2
    
    mode = config.config.divider_mode
    
    dividers: list = []
    
    # Column dividers (run along Y)
    for i in range(cols):
        div = build_divider(
            length=depth - 5,
            height=height,
            mode=mode,
            name=f"ColDivider_{i}",
        )
        if div:
            dividers.append(div)
    
    # Row dividers (run along X)
    for i in range(rows):
        div = build_divider(
            length=width - 5,
            height=height,
            mode=mode,
            name=f"RowDivider_{i}",
        )
        if div:
            # Rotate 90 degrees for row orientation
            div.rotation_euler = (0, 0, 1.5708)  # 90 degrees
            dividers.append(div)
    
    return dividers


def build_insert(
    width: float,
    depth: float,
    insert_type: str = "flat",
    name: str = "Insert",
    location: Tuple[float, float, float] = (0, 0, 0),
) -> Optional["bpy.types.Object"]:
    """
    Create modular bottom insert for drawer cell.
    
    Insert types:
    - flat: Plain bottom
    - honeycomb: Hex grid for round items
    - cable_waves: Wavy channels for cables
    - bit_holder: Holes for drill bits
    - pencil_grooves: Parallel grooves for pens
    
    Args:
        width: Insert width
        depth: Insert depth
        insert_type: Type of insert pattern
        name: Object name
        location: Object location
    
    Returns:
        Blender object
    """
    ensure_bpy()
    
    thickness = 1.4
    
    # Base plate
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=location
    )
    insert = bpy.context.active_object
    if insert is None:
        return None
    
    insert.name = name
    insert.scale = (width, depth, thickness)
    bpy.ops.object.transform_apply(scale=True)
    
    if insert_type == "honeycomb":
        _add_honeycomb_pattern(insert, width, depth)
    elif insert_type == "cable_waves":
        _add_cable_waves(insert, width, depth)
    elif insert_type == "pencil_grooves":
        _add_pencil_grooves(insert, width, depth)
    
    return insert


def _add_honeycomb_pattern(
    insert: "bpy.types.Object",
    width: float,
    depth: float,
) -> None:
    """Add honeycomb depressions for round items."""
    from ..geometry.boolean_ops import boolean_batch_difference
    
    cell_size = 15.0
    cell_depth = 0.8
    
    cols = int(width / cell_size)
    rows = int(depth / cell_size)
    
    cells: list["bpy.types.Object"] = []
    
    for row in range(rows):
        offset = cell_size / 2 if row % 2 else 0
        for col in range(cols):
            x = -width / 2 + col * cell_size + cell_size / 2 + offset
            y = -depth / 2 + row * cell_size * 0.866 + cell_size / 2
            
            if abs(x) < width / 2 - 5 and abs(y) < depth / 2 - 5:
                bpy.ops.mesh.primitive_cylinder_add(
                    vertices=6,
                    radius=cell_size / 2 - 1,
                    depth=cell_depth,
                    location=(x, y, cell_depth / 2)
                )
                cell = bpy.context.active_object
                if cell is not None:
                    cells.append(cell)
    
    if cells:
        boolean_batch_difference(insert, cells)


def _add_cable_waves(
    insert: "bpy.types.Object",
    width: float,
    depth: float,
) -> None:
    """Add wavy grooves for cable organization."""
    from ..geometry.boolean_ops import boolean_batch_difference
    
    num_grooves = 4
    groove_depth = 0.6
    groove_width = 8.0
    
    grooves: list["bpy.types.Object"] = []
    
    for i in range(num_grooves):
        y = -depth / 2 + (i + 1) * depth / (num_grooves + 1)
        
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=16,
            radius=groove_width / 2,
            depth=width - 10,
            location=(0, y, groove_depth / 2)
        )
        groove = bpy.context.active_object
        if groove is not None:
            groove.rotation_euler = (0, 1.5708, 0)
            grooves.append(groove)
    
    if grooves:
        boolean_batch_difference(insert, grooves)


def _add_pencil_grooves(
    insert: "bpy.types.Object",
    width: float,
    depth: float,
) -> None:
    """Add parallel grooves for pens/pencils."""
    from ..geometry.boolean_ops import boolean_batch_difference
    
    num_grooves = int(width / 12)
    groove_depth = 0.8
    groove_dia = 10.0
    
    grooves: list["bpy.types.Object"] = []
    
    for i in range(num_grooves):
        x = -width / 2 + (i + 1) * width / (num_grooves + 1)
        
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=16,
            radius=groove_dia / 2,
            depth=depth - 10,
            location=(x, 0, groove_depth / 2)
        )
        groove = bpy.context.active_object
        if groove is not None:
            groove.rotation_euler = (1.5708, 0, 0)
            grooves.append(groove)
    
    if grooves:
        boolean_batch_difference(insert, grooves)
