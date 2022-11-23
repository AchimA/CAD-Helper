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
        
        #object.delete()
    
    


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