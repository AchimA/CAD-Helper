# GPL-3.0 license
import bpy


def get_material_list(context):
    material_list = []
    for obj in context.selected_objects:
        for mat in obj.material_slots:
            if mat.material is not None and mat.material not in material_list:
                material_list.append(mat.material)
    return material_list


# Centralized reporting utilities for consistent message formatting
_REPORT_PREFIX = "CAD Helper: "

def report(op, level: str, message: str):
    """Generic reporting helper.
    level: 'INFO' | 'WARNING' | 'ERROR'
    Adds a common prefix to all messages.
    """
    op.report({level}, _REPORT_PREFIX + message)

def report_info(op, message: str):
    report(op, 'INFO', message)

def report_warning(op, message: str):
    report(op, 'WARNING', message)

def report_error(op, message: str):
    report(op, 'ERROR', message)


def apply_modifiers_and_join(context, objects_list):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects_list:
        obj.select_set(True)
        if obj.type == 'MESH':
            context.view_layer.objects.active = obj
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

