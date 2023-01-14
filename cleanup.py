# GPL-3.0 license

import bpy
import mathutils
from . import shared_functions


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
        if len(bpy.context.selected_objects) == 0:
            self.report({'INFO'}, 'No objects were selected. Nothing done...')
            return {'CANCELLED'}

        for object in bpy.context.selected_objects:
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
    bl_label = 'Delete Child Empies with no Children'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        init_selection = bpy.context.selected_objects

        # exit function if no objects have been selected
        if len(init_selection) == 0:
            self.report({'INFO'}, 'No objects were selected. Nothing done...')
            return {'CANCELLED'}

        # make a list of all the leaf children of type empty
        sel = []
        for obj in init_selection:
            children = obj.children_recursive
            for child in children:
                if len(child.children) == 0 and child.type == 'EMPTY' and child not in sel:
                    sel.append(child)
                    # self.report({'INFO'}, 'Found {} objects for removal'.format(len(sel)))

        print(sel)

        # iterate through list of leafes
        # (as long as elements are in the sel list)
        counter = 0
        while sel:
            # extract first object of the list
            obj = sel.pop(0)
            # check if obj has parent of type empy,
            # if True then add that parent to sel list
            # print(obj.parent.type, obj.parent)
            # if obj.parent.type == 'EMPTY':
            #     sel.append(obj.parent)
            # remove obj form init_selection if it was in there
            while obj in init_selection:
                init_selection.remove(obj)
            # delete obj
            bpy.data.objects.remove(obj)
            counter += 1
            # continue as long as some elements are in the list...

        # restore selection as of before
        bpy.ops.object.select_all(action='DESELECT')
        [obj.select_set(True) for obj in init_selection]


        self.report({'INFO'}, 'Removed {} objects'.format(counter))
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
        init_selection = bpy.context.selected_objects

        for root in init_selection:
            for child in root.children_recursive:
                location = child.matrix_world
                child.parent = root
                child.matrix_world = location

        # restore selection as of before
        bpy.ops.object.select_all(action='DESELECT')
        [obj.select_set(True) for obj in init_selection]

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
        init_selection = bpy.context.selected_objects

        for root in init_selection:
            all_children = root.children_recursive
            for child in all_children:
                location = child.matrix_world
                child.parent = root
                child.matrix_world = location
            shared_functions.apply_modifiers_and_join(all_children)

        # restore selection as of before
        bpy.ops.object.select_all(action='DESELECT')
        [obj.select_set(True) for obj in init_selection]

        return {'FINISHED'}


class SetObjOrigin(bpy.types.Operator):
    '''
    Set object origin to bounding box center of all the selected objects.
    '''
    bl_idname = 'object.set_obj_origin'
    bl_label = 'Set Object Origin to Bounding Box Center'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        init_selection = bpy.context.selected_objects

        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

        # restore selection as of before
        bpy.ops.object.select_all(action='DESELECT')
        [obj.select_set(True) for obj in init_selection]

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
        init_selection = bpy.context.selected_objects

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
        for obj in bpy.context.selected_objects:
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
        init_selection = bpy.context.selected_objects

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
                    if child.type != 'EMPTY':
                        x += child.location[0]
                        y += child.location[1]
                        z += child.location[2]
                        n += 1
                        # child.parent = root
                        # child.matrix_world = location
                x = x/n
                y = y/n
                z = z/n
                # print(x, y, z)

                # Create a new transformation matrix with the desired position
                matrix = mathutils.Matrix()
                matrix[0][3] = x  # Set the x position
                matrix[1][3] = y  # Set the y position
                matrix[2][3] = z  # Set the z position

                # Set the object's matrix_world attribute to the new matrix
                root.matrix_world = matrix

                # reset the children's position to the previously saved location
                for chld in root.children:
                    chld.matrix_world = pos[chld]
            

        # restore selection as of before
        bpy.ops.object.select_all(action='DESELECT')
        [obj.select_set(True) for obj in init_selection]

        return {'FINISHED'}


##############################################################################
# Add-On Handling
##############################################################################
__classes__ = (
    DeleteAndReparentChildren,
    DeleteEmpiesWithoutChildren,
    FlattenHierarchy,
    FlattenJoinHierarchy,
    SetObjOrigin,
    NormEmptySize,
    CenterEmptiesToChildren,
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
