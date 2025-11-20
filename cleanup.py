# GPL-3.0 license
import bpy
import mathutils
from . import shared_functions

##############################################################################
# Panel
##############################################################################

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

##############################################################################
# Operators
##############################################################################

class DeleteAndReparentChildren(bpy.types.Operator):
    '''
    Reconnects all the children of an object to it's
    parent (if available) before deleting the object.
    This allows to keep the hierarchy when
    deleting objects from a structured assebly.
    '''
    bl_idname = 'object.delete_and_reparent_children'
    bl_label = 'Delete and re-parent Children'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        # exit function if no parents / roots have been selected
        if len(context.selected_objects) == 0:
            self.report({'INFO'}, 'No objects were selected. Nothing done...')
            return {'CANCELLED'}

        for object in context.selected_objects:
            self.delete_and_reconnect(object)

        return {'FINISHED'}

    def delete_and_reconnect(self, object):
        parent = object.parent

        if parent is not None:
            # executes only if object has a parent
            children = object.children
            for child in children:
                location = child.matrix_world
                child.parent = parent
                child.matrix_world = location

        bpy.data.objects.remove(object)


class DeleteEmpiesWithoutChildren(bpy.types.Operator):
    '''
    Under selected root objects; recursivley
    deletes all empties that do not have any chlidren.
    '''
    bl_idname = 'object.delete_child_empties_without_children'
    bl_label = 'Delete Child Empties Without Children'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        init_selection = list(context.selected_objects)  # snapshot
        # preserve current active object
        _active = context.view_layer.objects.active

        if not init_selection:
            self.report({'INFO'}, 'No objects selected')
            return {'CANCELLED'}

        # collect leaf empty children
        sel = []
        for obj in init_selection:
            for child in obj.children_recursive:
                if child.type == 'EMPTY' and len(child.children) == 0 and child not in sel:
                    sel.append(child)

        counter = 0
        while sel:
            obj = sel.pop(0)
            if obj in init_selection:
                init_selection.remove(obj)
            # remove object from data
            bpy.data.objects.remove(obj)
            counter += 1

        # restore selection (avoid bpy.ops)
        for o in context.view_layer.objects:
            o.select_set(False)
        for obj in init_selection:
            obj.select_set(True)

        # restore active object
        context.view_layer.objects.active = _active

        self.report({'INFO'}, f'Removed {counter} objects')
        return {'FINISHED'}


class FlattenHierarchy(bpy.types.Operator):
    '''
    Flattens hierarch, so that all of the childrend
    below a selected node(s) are on the same level.
    '''
    bl_idname = 'object.flatten_hierarchy'
    bl_label = 'Flatten Hierarchy'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        init_selection = context.selected_objects

        for root in init_selection:
            for child in root.children_recursive:
                location = child.matrix_world
                child.parent = root
                child.matrix_world = location

        return {'FINISHED'}


class FlattenJoinHierarchy(bpy.types.Operator):
    '''
    Flattens hierarchy and join all of the child mesh objects,
    so that all of the children below a selected object(s)
    are on the same level.
    All modifiers are applied before joining.
    '''
    bl_idname = 'object.flatten_and_join_hierarchy'
    bl_label = 'Flatten and Join Hierarchy'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        init_selection = context.selected_objects

        for root in init_selection:
            all_children = root.children_recursive
            for child in all_children:
                location = child.matrix_world
                child.parent = root
                child.matrix_world = location
            shared_functions.apply_modifiers_and_join(context, all_children)

        return {'FINISHED'}


class NormEmptySize(bpy.types.Operator):
    '''
    Normaliaes the Empty Display Size
    '''
    bl_idname = 'object.norm_empty_size'
    bl_label = 'Normalise Empty Size'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    empty_size: bpy.props.FloatProperty(
        name='New Empty Size',
        default=0.1,
        soft_min=0,
        soft_max=1
        )

    def invoke(self, context, event):
        init_selection = context.selected_objects

        # reduce selection to empties only
        bpy.ops.object.select_all(action='DESELECT')
        [
            obj.select_set(True)
            for obj
            in init_selection
            if obj.type == 'EMPTY'
            ]

    #     # apply scale for the empties
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        return self.execute(context)

    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type == 'EMPTY':
                
                # obj.transform_apply(location=False, rotation=False, scale=True)
                obj.empty_display_size = self.empty_size

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text='Filter by Size', icon='FIXED_SIZE')
        box.prop(self, 'empty_size', slider=True)


class CenterEmptiesToChildren(bpy.types.Operator):
    '''
    Center Empties to Children.
    This moves the assembly origin to an average
    position of all the parts in the assembly.
    '''
    bl_idname = 'object.center_empties_to_children'
    bl_label = 'Center Empties to Children'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        init_selection = context.selected_objects

        for root in init_selection:
            if root.type == 'EMPTY' and root.children_recursive:
                # save the location of the direct children
                pos = {}
                for chld in root.children:
                    pos[chld] = chld.matrix_world

                # calculate the root average location based on all of the children
                all_children = root.children_recursive
                x = 0
                y = 0
                z = 0
                n = 0
                for child in all_children:
                    x += child.matrix_world.translation[0]
                    y += child.matrix_world.translation[1]
                    z += child.matrix_world.translation[2]
                    n += 1
                # calculate average position
                x = x/n
                y = y/n
                z = z/n

                # Set the object's matrix_world attribute to the new matrix
                root.matrix_world.translation = mathutils.Vector((x,y,z))

                # reset the children's position to the previously saved location
                for chld in root.children:
                    chld.matrix_world = pos[chld]

        return {'FINISHED'}


##############################################################################
# Add-On Handling
##############################################################################
classes = (
    CAD_CLEAN_HELPER_PT_Panel,
    DeleteAndReparentChildren,
    DeleteEmpiesWithoutChildren,
    FlattenHierarchy,
    FlattenJoinHierarchy,
    NormEmptySize,
    CenterEmptiesToChildren,
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
