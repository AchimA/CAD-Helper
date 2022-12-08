import bpy

bl_info = {
    "name": "CAD-Helper",
    "author": "A. R. Ammon",
    "version": (0, 0, 5),
    "blender": (3, 10, 0),
    "description": "Adds additional object selection and deletion functionality for hierarchically structured assemblies.",
    "warning": "",
    "doc_url": "",
    'support' : 'COMMUNITY',
    "category": "Object",
}
    # "location": "View3D > Add > Mesh > New Object",

modulesNames = ['ui', 'operators']

import sys
import importlib

modulesFullNames = {}
for currentModuleName in modulesNames:
    modulesFullNames[currentModuleName] = ('{}.{}'.format(__name__, currentModuleName))

for currentModuleFullName in modulesFullNames.values():
    if currentModuleFullName in sys.modules:
        importlib.reload(sys.modules[currentModuleFullName])
    else:
        globals()[currentModuleFullName] = importlib.import_module(currentModuleFullName)
        setattr(globals()[currentModuleFullName], 'modulesNames', modulesFullNames)

def register():
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'register'):
                sys.modules[currentModuleName].register()

def unregister():
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'unregister'):
                sys.modules[currentModuleName].unregister()

if __name__ == "__main__":
    register()

# https://b3d.interplanety.org/en/creating-multifile-add-on-for-blender/