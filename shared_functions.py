# GPL-3.0 license
import bpy


def get_material_list(context):
    material_list = []
    for obj in context.selected_objects:
        for mat in obj.material_slots:
            if mat.material is not None and mat.material not in material_list:
                material_list.append(mat.material)
    return material_list


def select_hierarchy():
    # select all the children recursively
    n = len(bpy.context.selected_objects)
    dn = 1
    while dn > 0:
        bpy.ops.object.select_hierarchy(direction='CHILD', extend=True)
        dn = len(bpy.context.selected_objects) - n
        n = len(bpy.context.selected_objects)
