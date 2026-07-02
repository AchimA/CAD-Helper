# GPL-3.0 license
import bpy
import mathutils
import math
from . import shared_functions

##############################################################################
# Panel
##############################################################################

class CAD_CLEAN_HELPER_PT_Panel(bpy.types.Panel):
    bl_idname = 'CAD_CLEAN_HELPER_PT_Panel'
    bl_label = 'Clean-Up'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CAD Helper'
    bl_context = 'objectmode'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False


class CAD_CLEAN_HELPER_PT_Cleanup(bpy.types.Panel):
    bl_idname = 'CAD_CLEAN_HELPER_PT_Cleanup'
    bl_label = 'Clean-Up: Structure'
    bl_parent_id = 'CAD_CLEAN_HELPER_PT_Panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CAD Helper'
    bl_context = 'objectmode'
    bl_options = {'DEFAULT_OPEN'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False

        # Clean-Up Structure
        layout.operator(
            'object.delete_and_reparent_children',
            icon='SNAP_PEEL_OBJECT'
            )
        layout.operator(
            'object.delete_child_empties_without_children',
            icon='OUTLINER_DATA_EMPTY'
            )
        layout.operator(
            'object.flatten_hierarchy',
            icon='OUTLINER'
        )
        layout.operator(
            'object.flatten_and_join_hierarchy',
            icon='CON_CHILDOF'
        )


class CAD_CLEAN_HELPER_PT_Empties(bpy.types.Panel):
    bl_idname = 'CAD_CLEAN_HELPER_PT_Empties'
    bl_label = 'Clean-Up: Empties'
    bl_parent_id = 'CAD_CLEAN_HELPER_PT_Panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CAD Helper'
    bl_context = 'objectmode'
    bl_options = {'DEFAULT_OPEN'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False
        layout.operator(
            'object.norm_empty_size',
            icon='EMPTY_DATA'
            )
        layout.operator(
            'object.center_empties_to_children',
            icon='ANCHOR_CENTER'
            )


class CAD_CLEAN_HELPER_PT_MeshCleanup(bpy.types.Panel):
    bl_idname = 'CAD_CLEAN_HELPER_PT_MeshCleanup'
    bl_label =  'Clean-Up: Mesh Normals'
    bl_parent_id = 'CAD_CLEAN_HELPER_PT_Panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CAD Helper'
    bl_context = 'objectmode'
    bl_options = {'DEFAULT_OPEN'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False
        scene = context.scene

        col = layout.column(align=True)
        col.prop(scene, 'cad_cleanup_use_clear_split_normals')

        row = col.row(align=True)
        row.prop(scene, 'cad_cleanup_use_merge_by_distance')
        sub = row.row(align=True)
        sub.enabled = scene.cad_cleanup_use_merge_by_distance
        sub.prop(scene, 'cad_cleanup_merge_distance', text='Distance')

        col.prop(scene, 'cad_cleanup_use_recalc_normals')

        row = col.row(align=True)
        row.prop(scene, 'cad_cleanup_use_shade_smooth')
        sub = row.row(align=True)
        sub.enabled = scene.cad_cleanup_use_shade_smooth
        sub.prop(scene, 'cad_cleanup_auto_smooth_angle', text='Angle')

        layout.separator()
        layout.operator(
            'object.cleanup_selected_meshes',
            icon='MOD_NORMALEDIT'
        )

##############################################################################
# Operators
##############################################################################

class DeleteAndReparentChildren(bpy.types.Operator):
    '''
    Reconnects all the children of an object to it's
    parent (if available) before deleting the object.
    This allows to keep the hierarchy when
    deleting objects from a structured assebly.
    '''
    bl_idname = 'object.delete_and_reparent_children'
    bl_label = 'Delete and re-parent Children'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        # exit function if no parents / roots have been selected
        if len(context.selected_objects) == 0:
            self.report({'INFO'}, 'No objects were selected. Nothing done...')
            return {'CANCELLED'}

        for object in context.selected_objects:
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
    Under selected root objects; recursivley
    deletes all empties that do not have any chlidren.
    '''
    bl_idname = 'object.delete_child_empties_without_children'
    bl_label = 'Delete Child Empties Without Children'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        init_selection = list(context.selected_objects)  # snapshot
        # preserve current active object
        _active = context.view_layer.objects.active

        if not init_selection:
            self.report({'INFO'}, 'No objects selected')
            return {'CANCELLED'}

        # collect leaf empty children
        sel = []
        for obj in init_selection:
            for child in obj.children_recursive:
                if child.type == 'EMPTY' and len(child.children) == 0 and child not in sel:
                    sel.append(child)

        counter = 0
        while sel:
            obj = sel.pop(0)
            if obj in init_selection:
                init_selection.remove(obj)
            # remove object from data
            bpy.data.objects.remove(obj)
            counter += 1

        # restore selection (avoid bpy.ops)
        for o in context.view_layer.objects:
            o.select_set(False)
        for obj in init_selection:
            obj.select_set(True)

        # restore active object
        context.view_layer.objects.active = _active

        self.report({'INFO'}, f'Removed {counter} objects')
        return {'FINISHED'}


class FlattenHierarchy(bpy.types.Operator):
    '''
    Flattens hierarch, so that all of the childrend
    below a selected node(s) are on the same level.
    '''
    bl_idname = 'object.flatten_hierarchy'
    bl_label = 'Flatten Hierarchy'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        init_selection = context.selected_objects

        for root in init_selection:
            for child in root.children_recursive:
                location = child.matrix_world
                child.parent = root
                child.matrix_world = location

        return {'FINISHED'}


class FlattenJoinHierarchy(bpy.types.Operator):
    '''
    Flattens hierarchy and join all of the child mesh objects,
    so that all of the children below a selected object(s)
    are on the same level.
    All modifiers are applied before joining.
    '''
    bl_idname = 'object.flatten_and_join_hierarchy'
    bl_label = 'Flatten and Join Hierarchy'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        init_selection = context.selected_objects

        for root in init_selection:
            all_children = root.children_recursive
            for child in all_children:
                location = child.matrix_world
                child.parent = root
                child.matrix_world = location
            shared_functions.apply_modifiers_and_join(context, all_children)

        return {'FINISHED'}


class NormEmptySize(bpy.types.Operator):
    '''
    Normalizes the Empty Display Size
    '''
    bl_idname = 'object.norm_empty_size'
    bl_label = 'Normalize Empty Size'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    empty_size: bpy.props.FloatProperty(
        name='New Empty Size',
        default=0.1,
        soft_min=0,
        soft_max=1
        )

    def invoke(self, context, event):
        init_selection = context.selected_objects

        # reduce selection to empties only
        bpy.ops.object.select_all(action='DESELECT')
        [
            obj.select_set(True)
            for obj
            in init_selection
            if obj.type == 'EMPTY'
            ]

    #     # apply scale for the empties
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        return self.execute(context)

    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type == 'EMPTY':
                
                # obj.transform_apply(location=False, rotation=False, scale=True)
                obj.empty_display_size = self.empty_size

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text='Filter by Size', icon='FIXED_SIZE')
        box.prop(self, 'empty_size', slider=True)


class CenterEmptiesToChildren(bpy.types.Operator):
    '''
    Center Empties to Children.
    This moves the assembly origin to an average
    position of all the parts in the assembly.
    '''
    bl_idname = 'object.center_empties_to_children'
    bl_label = 'Center Empties to Children'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        init_selection = context.selected_objects

        for root in init_selection:
            if root.type == 'EMPTY' and root.children_recursive:
                # save the location of the direct children
                pos = {}
                for chld in root.children:
                    pos[chld] = chld.matrix_world

                # calculate the root average location based on all of the children
                all_children = root.children_recursive
                x = 0
                y = 0
                z = 0
                n = 0
                for child in all_children:
                    x += child.matrix_world.translation[0]
                    y += child.matrix_world.translation[1]
                    z += child.matrix_world.translation[2]
                    n += 1
                # calculate average position
                x = x/n
                y = y/n
                z = z/n

                # Set the object's matrix_world attribute to the new matrix
                root.matrix_world.translation = mathutils.Vector((x,y,z))

                # reset the children's position to the previously saved location
                for chld in root.children:
                    chld.matrix_world = pos[chld]

        return {'FINISHED'}


class CleanupSelectedMeshes(bpy.types.Operator):
    '''
    Runs mesh clean-up operations on selected mesh objects.
    '''
    bl_idname = 'object.cleanup_selected_meshes'
    bl_label = 'Clean Selected Meshes'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return any(obj.type == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        init_selection = list(context.selected_objects)
        init_active = context.view_layer.objects.active
        init_mode = context.mode

        mesh_objects = [obj for obj in init_selection if obj.type == 'MESH']
        if not mesh_objects:
            self.report({'INFO'}, 'No mesh objects selected')
            return {'CANCELLED'}

        settings = context.scene
        op_clear = settings.cad_cleanup_use_clear_split_normals
        op_merge = settings.cad_cleanup_use_merge_by_distance
        op_recalc = settings.cad_cleanup_use_recalc_normals
        op_smooth = settings.cad_cleanup_use_shade_smooth
        smooth_angle = settings.cad_cleanup_auto_smooth_angle
        merge_dist = settings.cad_cleanup_merge_distance

        # Always clear split normals in auto-smooth strategy to avoid stale custom data.
        effective_clear = True

        if not (effective_clear or op_merge or op_recalc or op_smooth):
            self.report({'INFO'}, 'No mesh cleanup operations enabled')
            return {'CANCELLED'}

        processed = 0
        disabled_weighted_count = 0

        # Start from object mode to avoid mode conflicts while switching objects.
        try:
            if context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass

        try:
            for obj in mesh_objects:
                if obj.name not in context.view_layer.objects:
                    continue

                self._activate_only(context, obj)

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')

                if effective_clear:
                    bpy.ops.mesh.customdata_custom_splitnormals_clear()
                if op_merge:
                    bpy.ops.mesh.remove_doubles(threshold=merge_dist)
                if op_recalc:
                    bpy.ops.mesh.normals_make_consistent(inside=False)

                bpy.ops.object.mode_set(mode='OBJECT')

                if op_smooth:
                    self._apply_shade_smooth(context, obj, smooth_angle)

                disabled_weighted_count += self._set_weighted_normal_modifiers_enabled(obj, enabled=False)

                processed += 1
        finally:
            self._restore_context(context, init_selection, init_active, init_mode)

        ops_enabled = []
        if effective_clear:
            ops_enabled.append('clear split normals')
        if op_merge:
            ops_enabled.append('merge by distance')
        if op_recalc:
            ops_enabled.append('recalculate outside')
        if op_smooth:
            ops_enabled.append('shade smooth + auto smooth')
        if disabled_weighted_count > 0:
            ops_enabled.append(f'disabled {disabled_weighted_count} weighted normal modifiers')
        if not op_clear:
            ops_enabled.append('forced split-normal clear for auto smooth')

        self.report({'INFO'}, f'Cleaned {processed} mesh objects [auto smooth] ({", ".join(ops_enabled)})')
        return {'FINISHED'}

    def _activate_only(self, context, obj):
        for scene_obj in context.view_layer.objects:
            scene_obj.select_set(False)
        obj.select_set(True)
        context.view_layer.objects.active = obj

    def _apply_shade_smooth(self, context, obj, angle):
        # Smooth faces and preserve hard edges via auto-smooth where available.
        try:
            bpy.ops.object.shade_smooth()
        except Exception:
            mesh = getattr(obj, 'data', None)
            if mesh is not None and hasattr(mesh, 'polygons'):
                for poly in mesh.polygons:
                    poly.use_smooth = True

        mesh = getattr(obj, 'data', None)
        if mesh is None:
            return

        if hasattr(mesh, 'use_auto_smooth'):
            mesh.use_auto_smooth = True
            if hasattr(mesh, 'auto_smooth_angle'):
                mesh.auto_smooth_angle = angle
            return

        # Blender versions without use_auto_smooth may expose object operator instead.
        try:
            bpy.ops.object.shade_auto_smooth(angle=angle)
        except Exception:
            pass

    def _set_weighted_normal_modifiers_enabled(self, obj, enabled):
        if obj.type != 'MESH':
            return 0

        changed = 0
        for mod in obj.modifiers:
            if mod.type != 'WEIGHTED_NORMAL':
                continue
            was_enabled = True
            if hasattr(mod, 'show_viewport'):
                was_enabled = was_enabled and mod.show_viewport
                mod.show_viewport = enabled
            if hasattr(mod, 'show_render'):
                was_enabled = was_enabled and mod.show_render
                mod.show_render = enabled
            if hasattr(mod, 'show_in_editmode'):
                mod.show_in_editmode = enabled
            if was_enabled and not enabled:
                changed += 1

        return changed

    def _restore_context(self, context, init_selection, init_active, init_mode):
        try:
            if context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass

        for scene_obj in context.view_layer.objects:
            scene_obj.select_set(False)

        for obj in init_selection:
            if obj.name in context.view_layer.objects:
                obj.select_set(True)

        if init_active and init_active.name in context.view_layer.objects:
            context.view_layer.objects.active = init_active

        mode_map = {
            'OBJECT': 'OBJECT',
            'EDIT_MESH': 'EDIT',
            'SCULPT': 'SCULPT',
            'VERTEX_PAINT': 'VERTEX_PAINT',
            'WEIGHT_PAINT': 'WEIGHT_PAINT',
            'TEXTURE_PAINT': 'TEXTURE_PAINT',
        }
        target_mode = mode_map.get(init_mode)
        if target_mode and target_mode != 'OBJECT' and context.view_layer.objects.active is not None:
            try:
                bpy.ops.object.mode_set(mode=target_mode)
            except Exception:
                pass


def _default_merge_distance():
    # Query Blender operator RNA so default tracks Blender version changes.
    try:
        return bpy.ops.mesh.remove_doubles.get_rna_type().properties['threshold'].default
    except Exception:
        return 0.0001


##############################################################################
# Add-On Handling
##############################################################################
classes = (
    CAD_CLEAN_HELPER_PT_Panel,
    CAD_CLEAN_HELPER_PT_Cleanup,
    CAD_CLEAN_HELPER_PT_Empties,
    CAD_CLEAN_HELPER_PT_MeshCleanup,
    DeleteAndReparentChildren,
    DeleteEmpiesWithoutChildren,
    FlattenHierarchy,
    FlattenJoinHierarchy,
    NormEmptySize,
    CenterEmptiesToChildren,
    CleanupSelectedMeshes,
)

def register():
    bpy.types.Scene.cad_cleanup_use_merge_by_distance = bpy.props.BoolProperty(
        name='Merge by Distance',
        description='Merge close vertices in each selected mesh',
        default=True,
    )
    bpy.types.Scene.cad_cleanup_merge_distance = bpy.props.FloatProperty(
        name='Merge Distance',
        description='Distance threshold used for merge by distance',
        default=_default_merge_distance(),
        min=0.0,
        soft_max=0.1,
        subtype='DISTANCE',
    )
    bpy.types.Scene.cad_cleanup_use_clear_split_normals = bpy.props.BoolProperty(
        name='Clear Custom Split Normals',
        description='Clear imported custom split normals before recalculation',
        default=True,
    )
    bpy.types.Scene.cad_cleanup_use_recalc_normals = bpy.props.BoolProperty(
        name='Recalculate Normals Outside',
        description='Recalculate face normals to point outside',
        default=True,
    )
    bpy.types.Scene.cad_cleanup_use_shade_smooth = bpy.props.BoolProperty(
        name='Shade Smooth',
        description='Set smooth shading and preserve hard edges with auto-smooth',
        default=True,
    )
    bpy.types.Scene.cad_cleanup_auto_smooth_angle = bpy.props.FloatProperty(
        name='Auto Smooth Angle',
        description='Edge angle threshold used to keep hard edges',
        default=math.radians(30.0),
        min=0.0,
        max=math.radians(180.0),
        subtype='ANGLE',
    )
    # register classes
    for c in classes:
        bpy.utils.register_class(c)
        print(f'registered {c}')


def unregister():
    # unregister classes
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
        print(f'unregistered {c}')

    del bpy.types.Scene.cad_cleanup_auto_smooth_angle
    del bpy.types.Scene.cad_cleanup_use_shade_smooth
    del bpy.types.Scene.cad_cleanup_use_recalc_normals
    del bpy.types.Scene.cad_cleanup_use_clear_split_normals
    del bpy.types.Scene.cad_cleanup_merge_distance
    del bpy.types.Scene.cad_cleanup_use_merge_by_distance
