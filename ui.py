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

        layout.label(text='CAD Helper Addon by Achim Ammon')

        layout.operator('object.select_all_children', icon = 'OUTLINER')
        layout.operator('object.delete_and_reparent_children', icon = 'SNAP_PEEL_OBJECT')
        layout.operator('object.delete_child_empties_without_children', icon='CON_CHILDOF')
        layout.operator('object.filter_selection', icon='FILTER')
        layout.operator('object.list_materials', icon='FILTER')

        box = layout.box()
        box.label(text='ToDo:')
        box.label(text='- Transfer: Viewport Display -> Material Nodes')
        box.label(text='- Transfer: Material Nodes -> Viewport Display')
        box.label(text='- Import / Export: STEP via OpenCascade')
        


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