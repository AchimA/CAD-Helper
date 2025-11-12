# GPL-3.0 license
import bpy

class SelectAllChildren(bpy.types.Operator):
    """Select all children recursively of the current selection"""
    bl_idname = "object.select_all_children"
    bl_label = "Select All Children Recursively"
    bl_options = {"REGISTER", "UNDO"}

    extend: bpy.props.BoolProperty(
        name="Extend",
        description="Don't deselect existing selection",
        default=False
    )

    @classmethod
    def poll(cls, context):
        return bool(context.selected_objects)

    def execute(self, context):
        roots = list(context.selected_objects)
        if not roots:
            self.report({'INFO'}, "No selection")
            return {'CANCELLED'}

        # collect children (use set to avoid duplicates)
        sel_children = set()
        for r in roots:
            sel_children.update(r.children_recursive)

        if not sel_children:
            self.report({'INFO'}, "No children found")
            return {'CANCELLED'}

        # if not extending, deselect current selection first
        if not self.extend:
            for o in list(context.selected_objects):
                o.select_set(False)

        # select all collected children and set one active
        for i, o in enumerate(sel_children):
            o.select_set(True)
            if i == 0:
                context.view_layer.objects.active = o

        return {'FINISHED'}


##############################################################################
# Add-On Handling
##############################################################################
classes = (
    SelectAllChildren,
)

def register():
    # register classes
    for c in classes:
        bpy.utils.register_class(c)
        print(f'registered {c}')


def unregister():
    # unregister classes
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
        print(f'unregistered {c}')
