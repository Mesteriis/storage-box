#!/usr/bin/env python3
"""
Test script for Storage Box geometry.
Run step by step in Blender to verify each component.

Usage in Blender:
1. Open Blender
2. Switch to Scripting workspace  
3. Open this file
4. Run with: exec(open('test_geometry.py').read())
"""

import bpy
import bmesh


# ============================================================
# CONFIG
# ============================================================

WIDTH = 200.0   # mm
DEPTH = 220.0   # mm  
HEIGHT = 80.0   # mm
WALL = 2.0      # mm
FLOOR = 2.0     # mm
RAIL_WIDTH = 5.0
RAIL_HEIGHT = 8.0
TOLERANCE = 0.3  # mm (for PLA)


# ============================================================
# HELPERS
# ============================================================

def clear_scene():
    """Clear all objects."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for m in bpy.data.meshes:
        if m.users == 0:
            bpy.data.meshes.remove(m)


def set_material(obj, name, color):
    """Set object material."""
    mat = bpy.data.materials.new(name=name)
    mat.diffuse_color = (*color, 1.0)
    obj.data.materials.append(mat)


# ============================================================
# TEST 1: Basic Shell (П-shape, open front)
# ============================================================

def test_shell_basic():
    """
    Create shell with front opening.
    
    Shell is П-shaped when viewed from above:
    - Back wall: full height
    - Side walls: full height  
    - Front: OPEN for drawer
    - Bottom: floor
    """
    print("=== TEST 1: Basic Shell ===")
    clear_scene()
    
    # Start with solid box
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, HEIGHT/2))
    shell = bpy.context.active_object
    shell.name = "Shell"
    shell.scale = (WIDTH, DEPTH, HEIGHT)
    bpy.ops.object.transform_apply(scale=True)
    
    # Cut inner cavity (but leave walls and floor)
    inner_w = WIDTH - 2 * WALL
    inner_d = DEPTH - 2 * WALL  
    inner_h = HEIGHT - FLOOR
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, HEIGHT/2 + FLOOR/2))
    cavity = bpy.context.active_object
    cavity.name = "_cavity"
    cavity.scale = (inner_w, inner_d, inner_h)
    bpy.ops.object.transform_apply(scale=True)
    
    # Boolean: shell - cavity
    mod = shell.modifiers.new("Hollow", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cavity
    mod.solver = 'EXACT'
    bpy.context.view_layer.objects.active = shell
    bpy.ops.object.modifier_apply(modifier="Hollow")
    bpy.data.objects.remove(cavity, do_unlink=True)
    
    # CUT FRONT OPENING for drawer
    # Opening height = inner height (drawer can slide)
    # Opening width = inner width (full width between side walls)
    front_cut_w = inner_w
    front_cut_h = inner_h - 5  # Leave small lip at top
    front_cut_d = WALL * 2  # Cut through front wall
    
    bpy.ops.mesh.primitive_cube_add(
        size=1, 
        location=(0, -DEPTH/2 + WALL/2, HEIGHT/2 + 5)
    )
    front_cut = bpy.context.active_object
    front_cut.name = "_front_cut"
    front_cut.scale = (front_cut_w, front_cut_d, front_cut_h)
    bpy.ops.object.transform_apply(scale=True)
    
    mod = shell.modifiers.new("FrontOpen", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = front_cut
    mod.solver = 'EXACT'
    bpy.context.view_layer.objects.active = shell
    bpy.ops.object.modifier_apply(modifier="FrontOpen")
    bpy.data.objects.remove(front_cut, do_unlink=True)
    
    set_material(shell, "Shell_Mat", (0.6, 0.6, 0.65))
    
    print(f"  Shell created: {WIDTH}x{DEPTH}x{HEIGHT}mm")
    print(f"  Wall: {WALL}mm, Floor: {FLOOR}mm")
    print(f"  Front opening: {front_cut_w}x{front_cut_h}mm")
    
    return shell


# ============================================================
# TEST 2: Side Ledges (drawer slides on them)
# ============================================================

def test_ledges():
    """
    Create horizontal ledges on shell side walls.
    
    Drawer rests on these ledges and slides freely.
    Simple and effective.
    """
    print("\n=== TEST 2: Side Ledges ===")
    
    # First create shell
    shell = test_shell_basic()
    
    # Ledge parameters
    ledge_depth = DEPTH - 2 * WALL - 5  # Almost full depth
    ledge_width = RAIL_WIDTH  # How far ledge sticks out from wall
    ledge_thick = 3.0  # Ledge thickness
    ledge_z = FLOOR + 15  # Height above floor
    
    ledges = []
    for name, x_sign in [("Ledge_Left", -1), ("Ledge_Right", 1)]:
        # Create ledge as a box
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
        ledge = bpy.context.active_object
        ledge.name = name
        ledge.scale = (ledge_width, ledge_depth, ledge_thick)
        bpy.ops.object.transform_apply(scale=True)
        
        # Position on side wall
        x_pos = x_sign * (WIDTH/2 - WALL - ledge_width/2)
        ledge.location = (x_pos, 0, ledge_z)
        
        set_material(ledge, f"{name}_Mat", (0.4, 0.4, 0.45))
        ledges.append(ledge)
    
    # Calculate inner edge positions (where drawer sits)
    ledge_inner_left = -WIDTH/2 + WALL + ledge_width
    ledge_inner_right = WIDTH/2 - WALL - ledge_width
    
    print(f"  Ledges: {ledge_width:.1f}mm wide, {ledge_thick:.1f}mm thick")
    print(f"  At height Z = {ledge_z:.1f}mm")
    print(f"  Inner edges at X = {ledge_inner_left:.1f} and {ledge_inner_right:.1f}")
    
    return shell, ledges[0], ledges[1], ledge_inner_left, ledge_inner_right, ledge_z


# ============================================================
# TEST 3: Drawer (sits on ledges, slides freely)
# ============================================================

def test_drawer():
    """
    Create drawer that rests on side ledges.
    
    Drawer has simple flat bottom - just sits on the ledges
    and slides in/out through the front opening.
    """
    print("\n=== TEST 3: Drawer ===")
    
    # Create shell + ledges
    shell, ledge_l, ledge_r, edge_left, edge_right, ledge_z = test_ledges()
    
    # Drawer width: fits between ledge inner edges with tolerance
    drawer_w = (edge_right - edge_left) - 2 * TOLERANCE
    drawer_d = DEPTH - 2 * WALL - 10  # Room to slide
    drawer_h = HEIGHT - ledge_z - 5  # Above ledges to top
    drawer_wall = WALL * 0.75
    drawer_floor = WALL
    
    # Create drawer body
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, drawer_h/2))
    drawer = bpy.context.active_object
    drawer.name = "Drawer"
    drawer.scale = (drawer_w, drawer_d, drawer_h)
    bpy.ops.object.transform_apply(scale=True)
    
    # Hollow out
    inner_w = drawer_w - 2 * drawer_wall
    inner_d = drawer_d - 2 * drawer_wall
    inner_h = drawer_h - drawer_floor
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, drawer_h/2 + drawer_floor/2)
    )
    inner = bpy.context.active_object
    inner.scale = (inner_w, inner_d, inner_h)
    bpy.ops.object.transform_apply(scale=True)
    
    mod = drawer.modifiers.new("Hollow", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = inner
    mod.solver = 'EXACT'
    bpy.context.view_layer.objects.active = drawer
    bpy.ops.object.modifier_apply(modifier="Hollow")
    bpy.data.objects.remove(inner, do_unlink=True)
    
    # Add FLANGES on bottom sides to rest on ledges
    flange_w = RAIL_WIDTH + 2
    flange_d = drawer_d
    flange_h = 3  # Same as ledge thickness
    
    for name, x_sign in [("Flange_L", -1), ("Flange_R", 1)]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
        flange = bpy.context.active_object
        flange.name = name
        flange.scale = (flange_w, flange_d, flange_h)
        bpy.ops.object.transform_apply(scale=True)
        
        # Position: hanging from drawer bottom, extending outward
        x_pos = x_sign * (drawer_w/2 + flange_w/2 - 1)
        flange.location = (x_pos, 0, -flange_h/2)
        
        # Join to drawer
        bpy.ops.object.select_all(action='DESELECT')
        drawer.select_set(True)
        flange.select_set(True)
        bpy.context.view_layer.objects.active = drawer
        bpy.ops.object.join()
    
    # Finger pull
    pull_w = drawer_w * 0.35
    pull_h = drawer_h * 0.25
    pull_d = drawer_wall * 3
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, -drawer_d/2 + pull_d/2, drawer_h - pull_h/2)
    )
    pull = bpy.context.active_object
    pull.scale = (pull_w, pull_d, pull_h)
    bpy.ops.object.transform_apply(scale=True)
    
    mod = drawer.modifiers.new("Pull", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = pull
    mod.solver = 'EXACT'
    bpy.context.view_layer.objects.active = drawer
    bpy.ops.object.modifier_apply(modifier="Pull")
    bpy.data.objects.remove(pull, do_unlink=True)
    
    # Position drawer on ledges
    drawer.location = (0, 0, ledge_z + 3 + 0.2)  # On top of ledges
    
    set_material(drawer, "Drawer_Mat", (0.7, 0.7, 0.72))
    
    total_w = drawer_w + 2 * (flange_w - 1)
    print(f"  Drawer body: {drawer_w:.1f}x{drawer_d:.1f}x{drawer_h:.1f}mm")
    print(f"  With flanges: total width {total_w:.1f}mm")
    print(f"  Flanges rest ON ledges, drawer slides freely")
    
    return drawer


# ============================================================
# MAIN
# ============================================================

def main():
    """Run all tests."""
    print("=" * 50)
    print("STORAGE BOX GEOMETRY TEST")
    print("=" * 50)
    
    test_drawer()  # This runs all tests in sequence
    
    # Zoom to fit
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    with bpy.context.temp_override(area=area, region=region):
                        bpy.ops.view3d.view_all()
    
    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)
    print("\nShell: П-shape with front opening")
    print("Rails: V-profile on sides")
    print("Drawer: Sits on rails, can slide out front")


if __name__ == "__main__":
    main()
