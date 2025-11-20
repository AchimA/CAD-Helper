# GPL-3.0 license
import bpy
import importlib


module_names = (
    'selections',
    'cleanup',
    'filtering',
    'LinkObjData',
    'materials',
    'visualization',
    # ObjectPreview,
        )

# This list will be filled with the actual module objects at registration
__modules = []

def register():
    # Clear the list on a re-register (e.g., F8)
    __modules.clear()
    
    for name in module_names:
        try:
            # Dynamically import the module.
            # The f".{name}" and __package__ are crucial for relative imports
            module = importlib.import_module(f".{name}", __package__)
            module.register()
            __modules.append(module)
            print(f"Registered module: {name}")
        except ImportError:
            print(f"Error: Could not import module {name}")
        except Exception as e:
            print(f"Error registering module {name}: {e}")
    
def unregister():
    # Unregister in the reverse order to avoid dependency issues
    for module in reversed(__modules):
        try:
            module.unregister()
            print(f"Unregistered module: {module.__name__}")
        except Exception as e:
            print(f"Error unregistering module {module.__name__}: {e}")
            
    # Clear the list
    __modules.clear()

if __name__ == "__main__":
    register()
