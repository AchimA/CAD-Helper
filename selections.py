# GPL-3.0 license
import bpy

##############################################################################
# Panel
##############################################################################

class CAD_SEL_HELPER_PT_Panel(bpy.types.Panel):
    bl_idname = 'CAD_SEL_HELPER_PT_Panel'
    bl_label = 'CAD Selection Helper'
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
            text='Extend Selection to Parents',
            icon='TRIA_UP_BAR'
            )
        op.direction='PARENT'
        op.extend=True
        op = grid.operator(
            'object.select_hierarchy',
            text='Extend Selection to Chilren',
            icon='TRIA_DOWN_BAR'
            )
        op.direction='CHILD'
        op.extend=True
        op = grid.operator(
            'object.select_hierarchy',
            text='Select Parent',
            icon='TRIA_UP'
            )
        op.direction='PARENT'
        op.extend=False
        op = grid.operator(
            'object.select_hierarchy',
            text='Select Children',
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
        box.operator(
            'object.filter_by_vertex_count',
            icon='VERTEXSEL'
            )

        # Moved options to collapsible child panel below

class CAD_SEL_HELPER_PT_Options(bpy.types.Panel):
    bl_idname = 'CAD_SEL_HELPER_PT_Options'
    bl_label = 'Options'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CAD Helper'
    bl_parent_id = 'CAD_SEL_HELPER_PT_Panel'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, 'cad_sync_outliner')

##############################################################################
# Operators
##############################################################################

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
    CAD_SEL_HELPER_PT_Panel,
    CAD_SEL_HELPER_PT_Options,
    SelectAllChildren,
)

# Internal state tracker for last active object to avoid redundant focusing
_last_active_obj_name = None

def _sync_outliner_handler(scene):
    """Depsgraph update handler to sync Outliner focus to active object.
    Only runs when the scene property is enabled and active object changed.
    """
    if not getattr(scene, 'cad_sync_outliner', False):
        return

    # Active object reference
    active = bpy.context.view_layer.objects.active
    if active is None:
        # No active object: do nothing (multi-select without active is rare)
        return

    global _last_active_obj_name
    if _last_active_obj_name == active.name:
        return  # unchanged, skip
    _last_active_obj_name = active.name

    # Find an Outliner area and focus it on active
    try:
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'OUTLINER':
                    with bpy.context.temp_override(window=window, area=area, region=area.regions[-1]):
                        bpy.ops.outliner.show_active()
                    return
    except Exception:
        pass

def register():
    # register classes
    for c in classes:
        bpy.utils.register_class(c)
        print(f'registered {c}')

    # Add scene property for syncing
    bpy.types.Scene.cad_sync_outliner = bpy.props.BoolProperty(
        name='Sync Outliner to Selection',
        description='When enabled, Outliner scrolls to the active object whenever selection changes',
        default=True
    )
    # Register handler
    if _sync_outliner_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(_sync_outliner_handler)


def unregister():
    # unregister classes
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
        print(f'unregistered {c}')

    # Remove handler
    if _sync_outliner_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(_sync_outliner_handler)
    # Remove property
    if hasattr(bpy.types.Scene, 'cad_sync_outliner'):
        del bpy.types.Scene.cad_sync_outliner
