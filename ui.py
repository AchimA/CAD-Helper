# GPL-3.0 license

import bpy

##############################################################################
# Panels
##############################################################################

class CAD_SEL_HELPER_PT_Panel(bpy.types.Panel):
    bl_idname = 'CAD_SEL_HELPER_PT_Panel'
    bl_label = 'CAD Selection Helper'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CAD Helper'
    bl_context = 'objectmode'

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text='Hierarchy Selection')
        grid = box.grid_flow(columns=2, align=True)
        grid.operator(
            'object.extend_selection_to_parents',
            icon='TRIA_UP_BAR'
            )
        grid.operator(
            'object.extend_selection_to_children',
            icon='TRIA_DOWN_BAR'
            )
        grid.operator(
            'object.select_parent',
            icon='TRIA_UP'
            )
        grid.operator(
            'object.select_children',
            icon='TRIA_DOWN'
            )
        box.operator(
            'object.select_all_children',
            icon='OUTLINER'
            )

        box = layout.box()
        box.label(text='Selection Filtering')
        box.operator(
            'object.filter_selection',
            icon='FILTER'
            )


class CAD_CLEAN_HELPER_PT_Panel(bpy.types.Panel):
    bl_idname = 'CAD_CLEAN_HELPER_PT_Panel'
    bl_label = 'CAD Clean-Up Helper'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CAD Helper'
    bl_context = 'objectmode'

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text='Clean-Up')
        box.operator(
            'object.delete_and_reparent_children',
            icon='SNAP_PEEL_OBJECT'
            )
        box.operator(
            'object.delete_child_empties_without_children',
            icon='OUTLINER_DATA_EMPTY'
            )
        box.operator(
            'object.flatten_hierarchy',
            icon='OUTLINER'
        )
        box.operator(
            'object.flatten_and_join_hierarchy',
            icon='CON_CHILDOF'
        )

        box = layout.box()
        box.label(text='Origins')
        box.operator(
            'object.set_obj_origin',
            icon='OBJECT_ORIGIN'
            )
        box = layout.box()
        box.label(text='Empties / Assembly Nodes')
        box.operator(
            'object.norm_empty_size',
            icon='EMPTY_DATA'
            )
        box.operator(
            'object.center_empties_to_children',
            icon='ANCHOR_CENTER'
            )



class CAD_MAT_HELPER_PT_Panel(bpy.types.Panel):
    bl_idname = 'CAD_MAT_HELPER_PT_Panel'
    bl_label = 'CAD Material Helper'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CAD Helper'
    bl_context = 'objectmode'

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text='Transfer Material Properties')
        box.operator(
            'object.transfer_vp_to_nodes',
            icon='TRIA_LEFT'
            )
        box.operator(
            'object.transfer_nodes_to_vp',
            icon='TRIA_RIGHT'
            )

        box = layout.box()
        box.label(text='Clean-Up Materials')
        box.operator(
            'object.clear_vp_display',
            icon='LOOP_BACK'
            )
        box.operator(
            'object.clear_materials',
            icon='X'
            )
        box.operator(
            'object.cleanup_duplicate_materials',
            icon='MATERIAL'
            )


##############################################################################
# Add-On Handling
##############################################################################
__classes__ = (
    CAD_SEL_HELPER_PT_Panel,
    CAD_CLEAN_HELPER_PT_Panel,
    CAD_MAT_HELPER_PT_Panel,
)


def register():
    # register classes
    for c in __classes__:
        bpy.utils.register_class(c)

    print('registered ')


def unregister():
    # unregister classes
    for c in __classes__:
        bpy.utils.unregister_class(c)

    print('unregistered ')
