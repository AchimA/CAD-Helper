# GPL-3.0 license
import bpy


def get_material_list(context):
    material_list = []
    for obj in context.selected_objects:
        for mat in obj.material_slots:
            if mat.material is not None and mat.material not in material_list:
                material_list.append(mat.material)
    return material_list

    return 0


def select_hierarchy():
    # select all the children recursively
    n = len(bpy.context.selected_objects)
    dn = 1
    while dn > 0:
        bpy.ops.object.select_hierarchy(direction='CHILD', extend=True)
        dn = len(bpy.context.selected_objects) - n
        n = len(bpy.context.selected_objects)

    return 0


def apply_modifiers_and_join(objects_list):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects_list:
        obj.select_set(True)
        if obj.type == 'MESH':
            bpy.context.view_layer.objects.active = obj
    bpy.ops.object.make_single_user(
        type='SELECTED_OBJECTS',
        object=True,
        obdata=True
    )
    try:
        bpy.ops.object.convert(target='MESH')
    except:
        pass
    bpy.ops.object.modifier_apply(modifier="ALL")
    bpy.ops.object.join()

    return 0
