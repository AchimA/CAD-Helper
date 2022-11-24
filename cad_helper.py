bl_info = {
    # required
    'name': 'CAD Helper',
    'blender': (3, 1, 0),
    'category': 'Object',
    # optional
    'version': (0, 0, 2),
    'author': 'Achim Ammon',
    'description': 'Adds additional object selection and deletion functionality.',
}

import bpy
           


class DeleteAndReparentChildren(bpy.types.Operator):
    '''
    Reconnects all the children of an object to it's parent (if available) before deleting the object.
    '''
    bl_idname = 'object.delete_and_reparent_children'
    bl_label = 'Delete and reparent children'
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
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
    bl_idname = 'object.delete_selected_empties_without_children'
    bl_label = 'Delete selected Empies without Children'
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
            print(sel)
            # extract first object of the list
            obj = sel.pop(0)
            # check if obj has parent of type empy, if True then add that parent to sel list
            if obj.parent.type == 'EMPTY':
                sel.append(obj.parent)
            # delete obj
            bpy.data.objects.remove(obj)
            #continue as long as some elements are in the list
            
        return {'FINISHED'}


def menu_func(self, context):
    '''
    Add menu item
    '''
    self.layout.operator(DeleteAndReparentChildren.bl_idname)



#####################################################################################
# Add-On Handling
#####################################################################################

__classes__ = (
    DeleteAndReparentChildren,
    DeleteEmpiesWithoutChildren
)
    

def register():
    # register classes
    for c in __classes__:
        bpy.utils.register_class(c)

    # add menu items
    bpy.types.VIEW3D_MT_object.append(menu_func)
    
    print('registered ' + bl_info['name'] + ' Addon')



def unregister():
    # unregister classes
    for c  in __classes__:
        bpy.utils.unregister_class(c)
        
    #remove menu items
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    
    
    print('unregistered ' + bl_info['name'] + ' Addon')
        
if __name__ == '__main__':
    register()