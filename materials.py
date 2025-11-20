# GPL-3.0 license
import bpy
from . import shared_functions

##############################################################################
# Panel
##############################################################################

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
# Operators
##############################################################################

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
                node = getattr(mat, 'node_tree', None)
                if node is None or node.nodes.get('Principled BSDF') is None:
                    raise KeyError('Principled BSDF node missing')
                bsdf = node.nodes['Principled BSDF']
                shared_functions.report_info(self, f'Processing: {mat.name}')
                bsdf.inputs[0].default_value = mat.diffuse_color
                bsdf.inputs[6].default_value = mat.metallic
                bsdf.inputs[9].default_value = mat.roughness
                ok += 1
            except (AttributeError, KeyError, IndexError, TypeError) as e:
                shared_functions.report_warning(self, f"Skipping {mat.name} ({e})")
                err += 1
        shared_functions.report_info(self, f'Processed Materials ({ok} OK, {err} skipped)')

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
                node = getattr(mat, 'node_tree', None)
                if node is None or node.nodes.get('Principled BSDF') is None:
                    raise KeyError('Principled BSDF node missing')
                bsdf = node.nodes['Principled BSDF']
                shared_functions.report_info(self, f'Processing: {mat.name}')
                mat.diffuse_color = bsdf.inputs[0].default_value
                mat.metallic = bsdf.inputs[6].default_value
                mat.roughness = bsdf.inputs[9].default_value
                ok += 1
            except (AttributeError, KeyError, IndexError, TypeError) as e:
                shared_functions.report_warning(self, f"Skipping {mat.name} ({e})")
                err += 1
        shared_functions.report_info(self, f'Processed Materials ({ok} OK, {err} skipped)')

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
            shared_functions.report_info(self, f'Clearing Viewport: {mat.name}')
            mat.diffuse_color = (0.8, 0.8, 0.8, 1)
            mat.metallic = 0
            mat.roughness = 0.4

        return {'FINISHED'}


class CleanupMaterialsOperator(bpy.types.Operator):
    """Deletes duplicated materials and relinks material slots\
    for ALL the materials in the scene."""
    bl_idname = "object.cleanup_duplicate_materials"
    bl_label = "Cleanup Duplicate Materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create a dictionary to store unique materials
        unique_materials = {}

        # Iterate through all the materials in the scene
        for material in bpy.data.materials:
            # Get the Principled BSDF node for the material
            try:
                principled_node = material.node_tree.nodes.get("Principled BSDF")

                # Create a key for the material by concatenating its RGBA, roughness, and metallic values
                key = f"{principled_node.inputs['Base Color'].default_value[0]}{principled_node.inputs['Base Color'].default_value[1]}{principled_node.inputs['Base Color'].default_value[2]}{principled_node.inputs['Alpha'].default_value}{principled_node.inputs['Roughness'].default_value}{principled_node.inputs['Metallic'].default_value}"

                # If the material is not in the dictionary, add it
                if key not in unique_materials:
                    unique_materials[key] = material
            except (AttributeError, KeyError):
                continue

        # Iterate through all the objects in the scene
        for obj in bpy.data.objects:
            # Iterate through all the material slots in the object
            for i, slot in enumerate(obj.material_slots):
                # Get the Principled BSDF node for the material in the slot
                try:
                    principled_node = slot.material.node_tree.nodes.get("Principled BSDF")

                    this_key = f"{principled_node.inputs['Base Color'].default_value[0]}{principled_node.inputs['Base Color'].default_value[1]}{principled_node.inputs['Base Color'].default_value[2]}{principled_node.inputs['Alpha'].default_value}{principled_node.inputs['Roughness'].default_value}{principled_node.inputs['Metallic'].default_value}"

                    # If the material in the slot is a duplicated material, replace it with the unique material
                    if this_key in unique_materials and slot.material not in unique_materials.values():
                        shared_functions.report_info(self, f'Replacing {slot.material.name_full} -> {unique_materials[this_key].name_full}')
                        obj.active_material_index = i
                        obj.active_material = unique_materials[this_key]
                    # if principled_node.inputs['Base Color'].default_value[0] == unique_materials[key].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value[0] and principled_node.inputs['Base Color'].default_value[1] == unique_materials[key].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value[1] and principled_node.inputs['Base Color'].default_value[2] == unique_materials[key].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value[2] and principled_node.inputs['Alpha'].default_value == unique_materials[key].node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value and principled_node.inputs['Roughness'].default_value == unique_materials and principled_node.inputs['Metallic'].default_value == unique_materials[key].node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value:
                    #     obj.active_material_index = i
                    #     obj.active_material = unique_materials[key]
                except (AttributeError, KeyError):
                    continue

        # Iterate through all the materials in the scene again
        for material in bpy.data.materials:
            # Get the Principled BSDF node for the material
            try:
                principled_node = material.node_tree.nodes.get("Principled BSDF")

                # If the material is not in the dictionary of unique materials, delete it
                if material not in unique_materials.values():
                    bpy.data.materials.remove(material)
            except (AttributeError, KeyError):
                continue

        return {'FINISHED'}

##############################################################################
# Add-On Handling
##############################################################################
classes = (
    CAD_MAT_HELPER_PT_Panel,
    Transfer_VP_to_Nodes,
    Transfer_Nodes_to_VP,
    Clear_Viewport_Display_Settings,
    CleanupMaterialsOperator,
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
