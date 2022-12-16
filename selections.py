# GPL-3.0 license

import bpy


class SelectParentsExtend(bpy.types.Operator):
    '''
    Extends the selection to the parent of all the selected objects
    '''
    bl_idname = 'object.extend_selection_to_parents'
    bl_label = 'Extend Sel. to Parents'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        bpy.ops.object.select_hierarchy(direction='PARENT', extend=True)
        return {'FINISHED'}


class SelectParent(bpy.types.Operator):
    '''
    Selects the immidiate parent of all the selected objects
    '''
    bl_idname = 'object.select_parent'
    bl_label = 'Select Parent'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        bpy.ops.object.select_hierarchy(direction='PARENT', extend=False)
        return {'FINISHED'}


class SelectChildren(bpy.types.Operator):
    '''
    Selects the immidiate child of all the selected objects
    '''
    bl_idname = 'object.select_children'
    bl_label = 'Select Children'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        bpy.ops.object.select_hierarchy(direction='CHILD', extend=False)
        return {'FINISHED'}


class SelectChildrenExtend(bpy.types.Operator):
    '''
    Extends the selection to the child of all the selected objects
    '''
    bl_idname = 'object.extend_selection_to_children'
    bl_label = 'Extend Sel. to Children'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        bpy.ops.object.select_hierarchy(direction='CHILD', extend=True)
        return {'FINISHED'}


class SelectAllChildren(bpy.types.Operator):
    '''
    Recursivley expands selection to include
    all the children of an initial selection.
    '''
    bl_idname = 'object.select_all_children'
    bl_label = 'Select All Children Recusivley'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        # exit function if no parents / roots have been selected
        if len(bpy.context.selected_objects) == 0:
            self.report({'INFO'}, 'No objects were selected. Nothing done...')
            return {'CANCELLED'}

        init_selection = bpy.context.selected_objects

        sel = []
        for obj in init_selection:
            sel += obj.children_recursive

        bpy.ops.object.select_all(action='DESELECT')
        [obj.select_set(True) for obj in sel]

        return {'FINISHED'}


##############################################################################
# Add-On Handling
##############################################################################
__classes__ = (
    SelectAllChildren,
    SelectParentsExtend,
    SelectParent,
    SelectChildren,
    SelectChildrenExtend,
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
