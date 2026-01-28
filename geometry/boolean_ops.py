"""
Boolean Operations for Storage Box geometry.

Wraps Blender's boolean modifier operations.
"""

from typing import Optional, List

try:
    import bpy
    HAS_BPY = True
except ImportError:
    HAS_BPY = False


def ensure_bpy():
    """Check if bpy is available."""
    if not HAS_BPY:
        raise RuntimeError("Blender Python API (bpy) not available")


def boolean_union(
    target: "bpy.types.Object",
    tool: "bpy.types.Object",
    apply: bool = True,
    delete_tool: bool = True,
) -> "bpy.types.Object":
    """
    Perform boolean union operation.
    
    Args:
        target: Object to modify
        tool: Object to union with
        apply: Apply modifier immediately
        delete_tool: Delete tool object after operation
    
    Returns:
        Modified target object
    """
    ensure_bpy()
    
    # Add boolean modifier
    mod = target.modifiers.new(name="Boolean_Union", type='BOOLEAN')
    mod.operation = 'UNION'
    mod.object = tool
    
    if apply:
        bpy.context.view_layer.objects.active = target
        bpy.ops.object.modifier_apply(modifier=mod.name)
    
    if delete_tool:
        bpy.data.objects.remove(tool, do_unlink=True)
    
    return target


def boolean_difference(
    target: "bpy.types.Object",
    tool: "bpy.types.Object",
    apply: bool = True,
    delete_tool: bool = True,
) -> "bpy.types.Object":
    """
    Perform boolean difference (subtraction) operation.
    
    Args:
        target: Object to modify
        tool: Object to subtract
        apply: Apply modifier immediately
        delete_tool: Delete tool object after operation
    
    Returns:
        Modified target object
    """
    ensure_bpy()
    
    mod = target.modifiers.new(name="Boolean_Diff", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = tool
    
    if apply:
        bpy.context.view_layer.objects.active = target
        bpy.ops.object.modifier_apply(modifier=mod.name)
    
    if delete_tool:
        bpy.data.objects.remove(tool, do_unlink=True)
    
    return target


def boolean_intersect(
    target: "bpy.types.Object",
    tool: "bpy.types.Object",
    apply: bool = True,
    delete_tool: bool = True,
) -> "bpy.types.Object":
    """
    Perform boolean intersection operation.
    
    Args:
        target: Object to modify
        tool: Object to intersect with
        apply: Apply modifier immediately
        delete_tool: Delete tool object after operation
    
    Returns:
        Modified target object
    """
    ensure_bpy()
    
    mod = target.modifiers.new(name="Boolean_Intersect", type='BOOLEAN')
    mod.operation = 'INTERSECT'
    mod.object = tool
    
    if apply:
        bpy.context.view_layer.objects.active = target
        bpy.ops.object.modifier_apply(modifier=mod.name)
    
    if delete_tool:
        bpy.data.objects.remove(tool, do_unlink=True)
    
    return target


def boolean_batch_difference(
    target: "bpy.types.Object",
    tools: List["bpy.types.Object"],
    apply: bool = True,
    delete_tools: bool = True,
) -> "bpy.types.Object":
    """
    Perform multiple boolean difference operations.
    
    Args:
        target: Object to modify
        tools: List of objects to subtract
        apply: Apply all modifiers immediately
        delete_tools: Delete tool objects after operation
    
    Returns:
        Modified target object
    """
    ensure_bpy()
    
    for i, tool in enumerate(tools):
        mod = target.modifiers.new(
            name=f"Boolean_Diff_{i}", 
            type='BOOLEAN'
        )
        mod.operation = 'DIFFERENCE'
        mod.object = tool
    
    if apply:
        bpy.context.view_layer.objects.active = target
        for mod in list(target.modifiers):
            if mod.type == 'BOOLEAN':
                bpy.ops.object.modifier_apply(modifier=mod.name)
    
    if delete_tools:
        for tool in tools:
            bpy.data.objects.remove(tool, do_unlink=True)
    
    return target


def join_objects(
    objects: List["bpy.types.Object"],
    name: str = "Joined",
) -> "bpy.types.Object":
    """
    Join multiple objects into one mesh.
    
    Args:
        objects: List of objects to join
        name: Name for joined object
    
    Returns:
        Joined object
    """
    ensure_bpy()
    
    if not objects:
        raise ValueError("No objects to join")
    
    # Deselect all
    bpy.ops.object.select_all(action='DESELECT')
    
    # Select all objects to join
    for obj in objects:
        obj.select_set(True)
    
    # Set first as active
    bpy.context.view_layer.objects.active = objects[0]
    
    # Join
    bpy.ops.object.join()
    
    result = bpy.context.active_object
    result.name = name
    
    return result
