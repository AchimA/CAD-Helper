# GPL-3.0 license

import bpy
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


##############################################################################
# Add-On Handling
##############################################################################
__classes__ = (
    DeleteAndReparentChildren,
    DeleteEmpiesWithoutChildren,
    FlattenHierarchy,
    FlattenJoinHierarchy,
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
