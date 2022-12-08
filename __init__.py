import bpy

bl_info = {
    # required
    'name': 'CAD-Helper',
    'blender': (3, 1, 0),
    'category': 'Object',
    # optional
    'version': (0, 0, 5),
    'support' : 'TESTING ',
    'author': 'Achim Ammon',
    'description': 'Adds additional object selection and deletion functionality.',
}

from . import ui
from . import operator

#####################################################################################
# Add-On Handling
#####################################################################################

def register():
    ui.register()
    operator.register()

def unregister():
    ui.unregister()
    operator.unregister()
        
if __name__ == '__main__':
    register()