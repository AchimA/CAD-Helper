# GPL-3.0 license

import bpy

global linkable_objects
linkable_objects = {}

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
        # Selections
        op = grid.operator(
            'object.select_hierarchy',
            text='Extend Selection to Parents',
            icon='TRIA_UP_BAR'
            )
        op.direction='PARENT'
        op.extend=True
        op = grid.operator(
            'object.select_hierarchy',
            text='Extend Selection to Chilren',
            icon='TRIA_DOWN_BAR'
            )
        op.direction='CHILD'
        op.extend=True
        op = grid.operator(
            'object.select_hierarchy',
            text='Select Parent',
            icon='TRIA_UP'
            )
        op.direction='PARENT'
        op.extend=False
        op = grid.operator(
            'object.select_hierarchy',
            text='Select Children',
            icon='TRIA_DOWN'
            )
        op.direction='CHILD'
        op.extend=False
        box.operator(
            'object.select_all_children',
            icon='OUTLINER'
            )
        # Filtering
        box = layout.box()
        box.label(text='Selection Filtering')
        box.operator(
            'object.filter_selection',
            icon='FILTER'
            )
        box.operator(
            'object.filter_by_vertex_count',
            icon='VERTEXSEL'
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

        # Clean-Up
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

        # Empties
        box = layout.box()
        box.label(text='Empties')
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
    bl_label = '[Exp.] CAD Material Helper'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CAD Helper'
    bl_context = 'objectmode'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text='Transfer Material Properties')
        box.operator(
            'object.transfer_nodes_to_vp',
            icon='TRIA_RIGHT'
            )
        box.operator(
            'object.transfer_vp_to_nodes',
            icon='TRIA_LEFT'
            )

        box = layout.box()
        box.label(text='Clean-Up Materials')
        box.operator(
            'object.clear_vp_display',
            icon='LOOP_BACK'
            )
        box.operator(
            'object.cleanup_duplicate_materials',
            icon='MATERIAL'
            )


##############################################################################
# Add-On Handling
##############################################################################
classes = (
    CAD_SEL_HELPER_PT_Panel,
    CAD_CLEAN_HELPER_PT_Panel,
    CAD_MAT_HELPER_PT_Panel,
)

def register():
    # register classes
    for c in classes:
        bpy.utils.register_class(c)
        print(f'registered {c}')


def unregister():
    # unregister classes
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
        print(f'unregistered {c}')
