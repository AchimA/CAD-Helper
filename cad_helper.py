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
            


class DeleteAndReparentChildren_Operator(bpy.types.Operator):
    '''
    Reconnects all the children of an object to it's parent (if available) before deleting the object.
    '''
    bl_idname = 'object.DeleteAndReparentChildren'
    bl_label = 'Delete and reparent children'
    
    
    def execute(self):
        for object in bpy.context.selected_objects:
            delete_and_reconnect(object)
            
        return {'FINISHED'}



CLASSES = [
    ]
    

def register():
    print('registered')
    for klass in CLASSES:
        bpy.utils.register_class(klass)

    bpy.types.VIEW3D_MT_object.append(DeleteAndReparentChildren_Operator.bl_idname)
        



def unregister():
    print('unregistered')
    for klass in CLASSES:
        bpy.utils.unregister_class(klass)
    bpy.types.VIEW3D_MT_object.remove(DeleteAndReparentChildren_Operator.bl_idname)
        
if __name__ == '__main__':
    register()