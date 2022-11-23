bl_info = {
    # required
    'name': 'CAD Helper',
    'blender': (3, 1, 0),
    'category': 'Object',
    # optional
    'version': (0, 0, 1),
    'author': 'Achim Ammon',
    'description': 'Adds additional object selection and deletion functionality.',
}

import bpy

def delete_and_reconnect(object):
    
    parent = object.parent
    
    if parent is not None:
        # executes only if object has a parent
        children = object.children
        for child in children:
            child.parent = parent
    
    object.delete()
            


class OBJECT_MT_DeleteAndReparentChildren(bpy.types.Operator):
    '''
    Reconnects all the children of an object to it's parent (if available) before deleting the object.
    '''
    bl_idname = 'object.DeleteAndReparentChildren'
    bl_label = 'Delete and reparent children'
    
    
    def execute(self):
        for object in bpy.context.selected_objects:
            delete_and_reconnect(object)
            
        return {'FINISHED'}


def menu_func(self, context):
    '''
    Add menu item
    '''
    self.layout.operator(OBJECT_MT_DeleteAndReparentChildren.bl_idname)


#####################################################################################
# Add-On Handling
#####################################################################################

__classes__ = (
    OBJECT_MT_DeleteAndReparentChildren,
)
    

def register():
    # register classes
    for c in __classes__:
        bpy.utils.register_class(c)

    # add menu items
    bpy.types.VIEW3D_MT_object.append(menu_func)
    
    print('registered')



def unregister():
    # unregister classes
    for c  in __classes__:
        bpy.utils.unregister_class(c)
        
    #remove menu items
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    
    
    print('unregistered')
        
if __name__ == '__main__':
    register()