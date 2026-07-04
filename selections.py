# GPL-3.0 license
import bpy
from . import shared_functions

##############################################################################
# Panel
##############################################################################

class CAD_SEL_HELPER_PT_Panel(bpy.types.Panel):
    bl_idname = 'CAD_SEL_HELPER_PT_Panel'
    bl_label = 'Selection'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CAD Helper'
    bl_context = 'objectmode'

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text='Hierarchy Selection')
        grid = box.grid_flow(columns=2, align=True)
        # Selections
        op = grid.operator(
            'object.select_hierarchy',
            text='Extend Selection to Parents.',
            icon='TRIA_UP_BAR'
            )
        op.direction='PARENT'
        op.extend=True
        op = grid.operator(
            'object.select_hierarchy',
            text='Extend Selection to Children.',
            icon='TRIA_DOWN_BAR'
            )
        op.direction='CHILD'
        op.extend=True
        op = grid.operator(
            'object.select_hierarchy',
            text='Select Parent.',
            icon='TRIA_UP'
            )
        op.direction='PARENT'
        op.extend=False
        op = grid.operator(
            'object.select_hierarchy',
            text='Select Children.',
            icon='TRIA_DOWN'
            )
        op.direction='CHILD'
        op.extend=False
        box.operator(
            'object.select_all_children',
            icon='OUTLINER'
            )
        # Filtering
        box = layout.box()
        box.label(text='Selection Filtering')
        box.operator(
            'object.filter_selection',
            icon='FILTER'
            )

##############################################################################
# Operators
##############################################################################

class SelectAllChildren(bpy.types.Operator):
    """Select all children recursively of the current selection."""
    bl_idname = "object.select_all_children"
    bl_label = "Select All Children Recursively"
    bl_options = {"REGISTER", "UNDO"}

    # Use Blender's recommended annotation style so the property is registered correctly
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
            shared_functions.report_info(self, "No selection")
            return {'CANCELLED'}

        # collect children (use set to avoid duplicates)
        sel_children = set()
        for r in roots:
            sel_children.update(r.children_recursive)

        if not sel_children:
            shared_functions.report_info(self, "No children found")
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
    CAD_SEL_HELPER_PT_Panel,
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
