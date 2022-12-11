# GPL-3.0 license

import bpy
from . import shared_functions


class Transfer_VP_to_Nodes(bpy.types.Operator):
    """Transfer: Viewport Display -> Material Nodes"""
    bl_idname = "object.transfer_vp_to_nodes"
    bl_label = "Transfer: Viewport Display -> Material Nodes"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        material_list = shared_functions.get_material_list(context)
        ok = 0
        err = 0
        for mat in material_list:
            try:
                self.report({'INFO'}, 'Processing:\t{}'.format(mat.name))
                mat.node_tree.nodes['Principled BSDF'].inputs[0].default_value = mat.diffuse_color
                mat.node_tree.nodes['Principled BSDF'].inputs[6].default_value = mat.metallic
                mat.node_tree.nodes['Principled BSDF'].inputs[9].default_value = mat.roughness
                ok += 1
            except:
                # Errror Handling, falls etwas schief läuft....
                self.report(
                    {'INFO'},
                    'WARNING!:\tThere has been an error processing \'{}\''.format(mat.name)
                    )
                err += 1
        self.report(
            {'INFO'},
            'Processing Matterial ({} OK, {} errors)'.format(ok, err)
            )

        return {'FINISHED'}


class Transfer_Nodes_to_VP(bpy.types.Operator):
    """Transfer: Material Nodes -> Viewport Display"""
    bl_idname = "object.transfer_nodes_to_vp"
    bl_label = "Transfer: Material Nodes -> Viewport Display"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        material_list = shared_functions.get_material_list(context)
        ok = 0
        err = 0
        for mat in material_list:
            try:
                self.report({'INFO'}, 'Processing:\t{}'.format(mat.name))
                mat.diffuse_color = mat.node_tree.nodes['Principled BSDF'].inputs[0].default_value
                mat.metallic = mat.node_tree.nodes['Principled BSDF'].inputs[6].default_value
                mat.roughness = mat.node_tree.nodes['Principled BSDF'].inputs[9].default_value
                ok += 1
            except:
                # Errror Handling, falls etwas schief läuft....
                self.report(
                    {'INFO'},
                    'WARNING!:\tThere has been an error processing \'{}\''.format(mat.name)
                    )
                err += 1
        self.report(
            {'INFO'},
            'Processing Matterial ({} OK, {} errors)'.format(ok, err)
            )

        return {'FINISHED'}


class Clear_Materials(bpy.types.Operator):
    '''
    Removes all material slots form the selected objects.
    '''
    bl_idname = "object.clear_materials"
    bl_label = "Clear all Materials"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        sel = bpy.context.selected_objects

        for obj in sel:
            obj.data.materials.clear()

        return {'FINISHED'}


class Clear_Viewport_Display_Settings(bpy.types.Operator):
    '''
    Clears the Viewport Display settings (color, metallic and roughness) for the selected objects.
    '''
    bl_idname = "object.clear_vp_display"
    bl_label = "Clear Viewport Display Settings"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        material_list = shared_functions.get_material_list(context)
        for mat in material_list:
            self.report({'INFO'}, 'Processing:\t{}'.format(mat.name))
            mat.diffuse_color = (0.8, 0.8, 0.8, 1)
            mat.metallic = 0
            mat.roughness = 0.4

        return {'FINISHED'}


##############################################################################
# Add-On Handling
##############################################################################
__classes__ = (
    Transfer_VP_to_Nodes,
    Transfer_Nodes_to_VP,
    Clear_Materials,
    Clear_Viewport_Display_Settings,
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
