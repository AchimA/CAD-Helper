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
    bl_label = 'Delete and re-parent children'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = __doc__

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
    bl_label = 'Delete child Empies with no children'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = __doc__

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        init_selection = bpy.context.selected_objects

        # exit function if no parents / roots have been selected
        if len(init_selection) == 0:
            self.report({'INFO'}, 'No objects were selected. Nothing done...')
            return {'CANCELLED'}

        shared_functions.select_hierarchy()

        sel = bpy.context.selected_objects

        # keep only type=empty
        sel = [n for n in sel if n.type == 'EMPTY']
        # keep only leafs (objects without children)
        sel = [n for n in sel if len(n.children) == 0]

        # iterate through list of leafes
        while sel:
            # extract first object of the list
            obj = sel.pop(0)
            # check if obj has parent of type empy,
            # if True then add that parent to sel list
            if obj.parent.type == 'EMPTY' and obj.parent not in init_selection:
                sel.append(obj.parent)
            # delete obj
            bpy.data.objects.remove(obj)
            # continue as long as some elements are in the list

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
