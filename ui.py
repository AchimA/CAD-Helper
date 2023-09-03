# GPL-3.0 license

import bpy
from . import bl_info

global linkable_objects
linkable_objects = {}

##############################################################################
# Panels
##############################################################################

# addon_info = bpy.context.preferences.addons['CAD-Helper'].bl_info

class CAD_INFO_PT_Panel(bpy.types.Panel):
    bl_idname = 'CAD_INFO_PT_Panel'
    bl_label = 'CAD Helper Info'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CAD Helper'
    bl_context = 'objectmode'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text='Add-On Version: {}.{}.{}'.format(bl_info['version'][0], bl_info['version'][1], bl_info['version'][2]))
        op = self.layout.operator(
            'wm.url_open',
            text='GitHub Page',
            icon='URL'
            )
        op.url = 'github.com/AchimA/CAD-Helper'


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
            'object.clear_materials',
            icon='X'
            )
        box.operator(
            'object.cleanup_duplicate_materials',
            icon='MATERIAL'
            )


class CAD_OBJ_DATA_LINKER_PT_Panel(bpy.types.Panel):
    bl_idname = 'LINK_OBJ_DATA_PT_PANEL'
    bl_label = 'CAD Object Data Helper'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CAD Helper'
    bl_context = 'objectmode'

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text='Link Object Data (EXPERIMENTAL)')

        box.operator_context = "INVOKE_DEFAULT"
        box.operator(
            'object.link_obj_data',
            icon='LINKED'
            )

# class LINKABLE_OBJECTS_PT_Panel(bpy.types.Panel):
#     bl_idname = 'Linkable_Objects_PT_Panel'
#     bl_label = 'CAD Object Data Helper'
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'UI'
#     bl_category = 'CAD Object Linker'
#     bl_context = 'objectmode'

#     global linkable_objects

#     def draw(self, context):
#         layout = self.layout
#         # layout.use_property_split = True
#         layout.label(text='Linkable collections:')
#         layout.operator('object.refresh_linkable_collection')
#         # layout.operator('object.update_linkable_collection', text='Refresh', icon='FILE_REFRESH')
#         for key, data in linkable_objects.items():
#             # print(key)
#             # print(data)
#             # row = col.row()
#             # row.label(text=key)
            
#             box = layout.box()
            
#             row_outer = box.row()
            
#             box = row_outer.box()
#             box.label(text='Thumbnail')
#             # icon_id = render_object_thumbnail(obj)
#             # row_outer.template_icon(icon_value=icon_id, scale=3.0)

#             box = row_outer.box()

#             box.label(text=f'[{len(data)}x] {key}', icon='OBJECT_DATA')
            
#             row = box.row()
            
#             row.operator(SelectCollections.bl_idname, text='Select', icon='RESTRICT_SELECT_OFF').collection_name = key
#             # op.custom_prop = key
#             # row.label(text='Select Objects', icon='RESTRICT_SELECT_OFF')
#             row.label(text='Link Object Data', icon='LINKED')
   

##############################################################################
# Add-On Handling
##############################################################################
__classes__ = (
    CAD_INFO_PT_Panel,
    CAD_SEL_HELPER_PT_Panel,
    CAD_CLEAN_HELPER_PT_Panel,
    CAD_MAT_HELPER_PT_Panel,
    CAD_OBJ_DATA_LINKER_PT_Panel,
    # LINKABLE_OBJECTS_PT_Panel,
)


def register():
    # register classes
    for c in __classes__:
        bpy.utils.register_class(c)
        print(f'registered {c}')


def unregister():
    # unregister classes
    for c in __classes__:
        bpy.utils.unregister_class(c)
        print(f'unregistered {c}')
