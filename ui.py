import bpy
# from . import __init__

# side panel:
class CAD_HELPER_PT_Panel(bpy.types.Panel):
    bl_idname = 'CAD_HELPER_PT_Panel'
    bl_label = 'CAD Helper'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CAD Helper'
    bl_context = 'objectmode'

    def draw(self, context):

        layout = self.layout

        row = layout.row()
        row.label(text='CAD Helper Addon by Achim Ammon')

        row = layout.row()
        row.operator('object.select_all_children', icon = 'OUTLINER')
        row = layout.row()
        row.operator('object.delete_and_reparent_children', icon = 'SNAP_PEEL_OBJECT')
        row = layout.row()
        row.operator('object.delete_child_empties_without_children', icon='CON_CHILDOF')
        row = layout.row()
        row.operator('object.filter_selection_by_size', icon='FILTER')

        row = layout.row()
        row.label(text='ToDo:')
        row = layout.row()
        row.label(text='- Select all children')
        row = layout.row()
        row.label(text='- Transfer Viewport Display -> Material Nodes')
        row = layout.row()
        row.label(text='- Material Nodes -> Transfer Viewport Display')
        row = layout.row()
        row.label(text='- Filter by obj type & name')
        row = layout.row()
        row.label(text='- Import / Export: STEP via OpenCascade')
        


#####################################################################################
# Add-On Handling
#####################################################################################
__classes__ = (
    CAD_HELPER_PT_Panel,
)
    

def register():
    # register classes
    for c in __classes__:
        bpy.utils.register_class(c)
    
    print('registered ')

def unregister():
    # unregister classes
    for c  in __classes__:
        bpy.utils.unregister_class(c)
    
    print('unregistered ')