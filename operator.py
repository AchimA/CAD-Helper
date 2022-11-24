import bpy
# from . import __init__

class DeleteAndReparentChildren(bpy.types.Operator):
    '''
    Reconnects all the children of an object to it's parent (if available) before deleting the object.
    '''
    bl_idname = 'object.delete_and_reparent_children'
    bl_label = 'Delete and re-parent children'
    bl_options = {"REGISTER", "UNDO"}
    
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
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
    Under selected root objects; recursivley deletes all empties that do not have any chlidren parented to it.
    '''
    bl_idname = 'object.delete_child_empties_without_children'
    bl_label = 'Delete child Empies with no children'
    bl_options = {"REGISTER", "UNDO"}
    bl_info = ''
    
    # list of objects marked for deletion:
    del_list = []
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        init_selection = bpy.context.selected_objects
        
        # exit function if no parents / roots have been selected
        if len(init_selection) == 0:
            self.report({'INFO'}, 'No objects were selected. Nothing done...')
            return {'CANCELLED'}
        
        # select all the children
        n = len(bpy.context.selected_objects)
        dn = 1
        while dn > 0:
            bpy.ops.object.select_hierarchy(direction='CHILD', extend=True)
            dn = len(bpy.context.selected_objects) - n
            n = len(bpy.context.selected_objects)
        sel = bpy.context.selected_objects
        
        # keep only type=empty
        sel = [n for n in sel if n.type == 'EMPTY']
        # keep only leafs (objects without children)
        sel = [n for n in sel if len(n.children)==0]
        
        # iterate through list of leafes
        while sel:
            # extract first object of the list
            obj = sel.pop(0)
            # check if obj has parent of type empy, if True then add that parent to sel list
            if obj.parent.type == 'EMPTY' and not obj.parent in init_selection:
                sel.append(obj.parent)
            # delete obj
            bpy.data.objects.remove(obj)
            #continue as long as some elements are in the list
        
        # restore selection as of before
        bpy.ops.object.select_all(action='DESELECT')
        print(init_selection)
        [obj.select_set(True) for obj in init_selection]

        return {'FINISHED'}

#####################################################################################
# Add-On Handling
#####################################################################################
__classes__ = (
    DeleteAndReparentChildren,
    DeleteEmpiesWithoutChildren,
)

def register():
    # register classes
    for c in __classes__:
        bpy.utils.register_class(c)
    
    print('registered ' + bl_info['name'] + ' Addon')

def unregister():
    # unregister classes
    for c  in __classes__:
        bpy.utils.unregister_class(c)
    
    print('unregistered ' + bl_info['name'] + ' Addon')