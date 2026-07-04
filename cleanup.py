# GPL-3.0 license
import bpy
import bmesh
import mathutils
import math
import time
from . import shared_functions

##############################################################################
# Panel
##############################################################################

class CAD_CLEAN_HELPER_PT_Panel(bpy.types.Panel):
    '''Various clean-up operations for CAD assemblies and meshes.'''
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
    # bl_options = {'DEFAULT_CLOSED'}

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
    # bl_options = {'DEFAULT_CLOSED'}

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
    # bl_options = {'DEFAULT_CLOSED'}

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
    '''Reconnects all the children of an object to it's
    parent (if available) before deleting the object.
    This allows to keep the hierarchy when
    deleting objects from a structured assebly.'''
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
    '''Under selected root objects; recursivley
    deletes all empties that do not have any chlidren.'''
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
    '''Flattens hierarchy, so that all of the childrend
    below a selected node(s) are on the same level.'''
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
    '''Flattens hierarchy and join all of the child mesh objects,
    so that all of the children below a selected object(s)
    are on the same level.
    All modifiers are applied before joining.'''
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
    '''Normalizes the Empty Display Size of all
    selected empties to a user-defined value.'''
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
    '''Center Empties to Children.
    This moves the assembly origin to an average
    position of all the parts in the assembly.'''
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
    '''Runs mesh clean-up operations on selected mesh objects.'''
    bl_idname = 'object.cleanup_selected_meshes'
    bl_label = 'Clean Selected Meshes'
    bl_options = {'REGISTER', 'UNDO'}

    _init_selection = None
    _init_active = None
    _init_mode = None
    _all_mesh_objects = None
    _mesh_instances_map = None
    _selected_mesh_total = 0
    _mesh_objects = None
    _index = 0
    _total = 0
    _processed = 0
    _shared_skipped = 0
    _disabled_weighted_count = 0
    _op_clear = True
    _op_merge = False
    _op_recalc = False
    _op_smooth = False
    _smooth_angle = 0.0
    _merge_dist = 0.0
    _timer = None
    _wm_progress_open = False
    _cursor_wait_set = False
    _cursor_modal_set = False
    _report_interval = 10
    _last_reported_index = 0
    _weighted_normals_disabled_objects = None
    _batch_size = 10
    _batch_min = 5
    _batch_max = 15
    _batch_target_seconds = 1.0
    _current_active_obj = None
    _cleared_normals_mesh_keys = None
    _smoothed_mesh_keys = None

    @classmethod
    def poll(cls, context):
        return any(obj.type == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        self._init_selection = list(context.selected_objects)
        self._init_active = context.view_layer.objects.active
        self._init_mode = context.mode

        self._all_mesh_objects = [obj for obj in self._init_selection if obj.type == 'MESH']
        if not self._all_mesh_objects:
            self.report({'INFO'}, 'No mesh objects selected')
            return {'CANCELLED'}
        self._selected_mesh_total = len(self._all_mesh_objects)

        # Deduplicate by mesh datablock so linked instances are not reprocessed.
        unique_mesh_objects = []
        self._mesh_instances_map = {}
        seen_mesh_data = set()
        for obj in self._all_mesh_objects:
            mesh = getattr(obj, 'data', None)
            if mesh is None:
                continue
            mesh_key = mesh.as_pointer()
            self._mesh_instances_map.setdefault(mesh_key, []).append(obj)
            if mesh_key in seen_mesh_data:
                continue
            seen_mesh_data.add(mesh_key)
            unique_mesh_objects.append(obj)

        self._mesh_objects = unique_mesh_objects
        self._shared_skipped = max(0, len(self._all_mesh_objects) - len(self._mesh_objects))

        settings = context.scene
        self._op_clear = settings.cad_cleanup_use_clear_split_normals
        self._op_merge = settings.cad_cleanup_use_merge_by_distance
        self._op_recalc = settings.cad_cleanup_use_recalc_normals
        self._op_smooth = settings.cad_cleanup_use_shade_smooth
        self._smooth_angle = settings.cad_cleanup_auto_smooth_angle
        self._merge_dist = settings.cad_cleanup_merge_distance

        # Always clear split normals in auto-smooth strategy to avoid stale custom data.
        effective_clear = True

        if not (effective_clear or self._op_merge or self._op_recalc or self._op_smooth):
            self.report({'INFO'}, 'No mesh cleanup operations enabled')
            return {'CANCELLED'}

        self._index = 0
        self._total = len(self._mesh_objects)
        self._processed = 0
        self._shared_skipped = max(0, len(self._all_mesh_objects) - self._total)
        self._disabled_weighted_count = 0
        self._last_reported_index = 0
        self._weighted_normals_disabled_objects = []
        self._batch_size = 5
        self._current_active_obj = None
        self._cleared_normals_mesh_keys = set()
        self._smoothed_mesh_keys = set()

        # Start from object mode to avoid mode conflicts while switching objects.
        try:
            if context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass

        # Deselect once so per-object activation can switch targets cheaply.
        try:
            bpy.ops.object.select_all(action='DESELECT')
        except Exception:
            for scene_obj in context.view_layer.objects:
                scene_obj.select_set(False)

        # Disable weighted normal modifiers on all selected mesh objects once.
        for obj in self._all_mesh_objects:
            disabled_count = self._set_weighted_normal_modifiers_enabled(obj, enabled=False)
            self._disabled_weighted_count += disabled_count
            if disabled_count > 0:
                self._weighted_normals_disabled_objects.append(obj)

        if self._op_clear:
            self._batch_clear_custom_split_normals(context)

        wm = context.window_manager
        wm.progress_begin(0, self._total)
        self._wm_progress_open = True
        if context.window is None:
            # Fallback for non-UI execution contexts where modal timers are unavailable.
            try:
                while self._index < self._total:
                    obj = self._mesh_objects[self._index]
                    if self._process_one(context, obj):
                        self._processed += 1
                    self._index += 1
                    wm.progress_update(self._index)
            except Exception as exc:
                self._finish(context, cancelled=True)
                self.report({'ERROR'}, f'Mesh cleanup failed: {exc}')
                return {'CANCELLED'}

            self._finish(context, cancelled=False)
            return {'FINISHED'}

        # Slightly lower tick rate keeps UI responsive and reduces cursor jitter.
        self._timer = wm.event_timer_add(0.05, window=context.window)
        self._set_wait_cursor(context)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            self._finish(context, cancelled=True)
            self.report({'WARNING'}, 'Mesh cleanup cancelled')
            return {'CANCELLED'}

        if event.type != 'TIMER':
            return {'PASS_THROUGH'}

        if self._index >= self._total:
            self._finish(context, cancelled=False)
            return {'FINISHED'}

        tick_start = time.perf_counter()
        batch_processed = 0
        current_batch_size = self._batch_size

        while self._index < self._total and batch_processed < current_batch_size:
            try:
                obj = self._mesh_objects[self._index]
                if self._process_one(context, obj):
                    self._processed += 1
            except Exception as exc:
                self._finish(context, cancelled=True)
                self.report({'ERROR'}, f'Mesh cleanup failed: {exc}')
                return {'CANCELLED'}

            self._index += 1
            batch_processed += 1

            elapsed = time.perf_counter() - tick_start
            if batch_processed >= self._batch_min and elapsed >= self._batch_target_seconds:
                break

        elapsed = time.perf_counter() - tick_start
        if elapsed < (self._batch_target_seconds * 0.7) and batch_processed >= current_batch_size:
            self._batch_size = min(self._batch_max, self._batch_size + 1)
        elif elapsed > (self._batch_target_seconds * 1.3):
            self._batch_size = max(self._batch_min, self._batch_size - 1)

        if self._wm_progress_open:
            context.window_manager.progress_update(self._index)
        if self._report_interval > 0 and (self._index - self._last_reported_index) >= self._report_interval:
            self.report({'INFO'}, f'Cleaning meshes: {self._index}/{self._total}')
            self._last_reported_index = self._index
            self._tag_view3d_redraw(context)

        return {'RUNNING_MODAL'}

    def _process_one(self, context, obj):
        if obj.name not in context.view_layer.objects:
            return False

        mesh = getattr(obj, 'data', None)
        if mesh is None:
            return False
        mesh_key = mesh.as_pointer()

        # Clearing custom split normals still requires mesh edit operator behavior.
        if (
            self._op_clear
            and mesh_key not in self._cleared_normals_mesh_keys
            and getattr(mesh, 'has_custom_normals', False)
        ):
            self._clear_custom_split_normals(context, obj)

        # Merge/recalculate via bmesh to avoid repeated edit-mode operator overhead.
        if self._op_merge or self._op_recalc:
            bm = bmesh.new()
            try:
                bm.from_mesh(mesh)
                if self._op_merge:
                    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=self._merge_dist)
                if self._op_recalc:
                    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
                bm.to_mesh(mesh)
                mesh.update()
            finally:
                bm.free()

        if self._op_smooth:
            instances = self._mesh_instances_map.get(mesh_key, [obj]) if mesh_key is not None else [obj]
            self._apply_shade_smooth_instances(context, instances, self._smooth_angle)

        return True

    def _apply_shade_smooth_instances(self, context, instances, angle):
        # Apply object-level smooth settings to each instance that shares mesh data.
        for inst in instances:
            if inst.name not in context.view_layer.objects:
                continue
            self._apply_shade_smooth(context, inst, angle)

    def _clear_custom_split_normals(self, context, obj):
        self._activate_only(context, obj)
        bpy.ops.object.mode_set(mode='EDIT')
        try:
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
        finally:
            bpy.ops.object.mode_set(mode='OBJECT')
        self._mark_mesh_normals_cleared(obj)

    def _batch_clear_custom_split_normals(self, context):
        targets = []
        for obj in self._mesh_objects:
            if obj.name not in context.view_layer.objects:
                continue
            mesh = getattr(obj, 'data', None)
            if mesh is None:
                continue
            if not getattr(mesh, 'has_custom_normals', False):
                continue
            targets.append(obj)

        if not targets:
            return

        for obj in targets:
            obj.select_set(True)

        context.view_layer.objects.active = targets[0]
        self._current_active_obj = targets[0]

        try:
            bpy.ops.object.mode_set(mode='EDIT')
            try:
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.customdata_custom_splitnormals_clear()
            finally:
                bpy.ops.object.mode_set(mode='OBJECT')

            for obj in targets:
                self._mark_mesh_normals_cleared(obj)
        except Exception:
            for obj in targets:
                if obj.name not in context.view_layer.objects:
                    continue
                mesh = getattr(obj, 'data', None)
                if mesh is None:
                    continue
                if not getattr(mesh, 'has_custom_normals', False):
                    continue
                self._clear_custom_split_normals(context, obj)

        try:
            bpy.ops.object.select_all(action='DESELECT')
        except Exception:
            for scene_obj in context.view_layer.objects:
                scene_obj.select_set(False)
        self._current_active_obj = None

    def _mark_mesh_normals_cleared(self, obj):
        mesh = getattr(obj, 'data', None)
        if mesh is None:
            return
        self._cleared_normals_mesh_keys.add(mesh.as_pointer())

    def _set_wait_cursor(self, context):
        if context.window is None:
            return
        try:
            context.window.cursor_modal_set('WAIT')
            self._cursor_modal_set = True
            self._cursor_wait_set = True
        except Exception:
            try:
                context.window.cursor_set('WAIT')
                self._cursor_wait_set = True
            except Exception:
                pass

    def _finish(self, context, cancelled):
        if self._wm_progress_open:
            context.window_manager.progress_end()
            self._wm_progress_open = False

        if self._timer is not None:
            try:
                context.window_manager.event_timer_remove(self._timer)
            except Exception:
                pass
            self._timer = None

        if self._cursor_wait_set and context.window is not None:
            try:
                if self._cursor_modal_set:
                    context.window.cursor_modal_restore()
                else:
                    context.window.cursor_set('DEFAULT')
            except Exception:
                pass
            self._cursor_wait_set = False
            self._cursor_modal_set = False

        if cancelled:
            for obj in self._weighted_normals_disabled_objects or []:
                if obj is None:
                    continue
                self._set_weighted_normal_modifiers_enabled(obj, enabled=True)

        self._restore_context(context, self._init_selection, self._init_active, self._init_mode)

        if cancelled:
            return

        ops_enabled = ['clear split normals']
        if self._op_merge:
            ops_enabled.append('merge by distance')
        if self._op_recalc:
            ops_enabled.append('recalculate outside')
        if self._op_smooth:
            ops_enabled.append('shade smooth + auto smooth')
        if self._disabled_weighted_count > 0:
            ops_enabled.append(f'disabled {self._disabled_weighted_count} weighted normal modifiers')
        if self._shared_skipped > 0:
            ops_enabled.append(f'skipped {self._shared_skipped} linked instances')
        if not self._op_clear:
            ops_enabled.append('forced split-normal clear for auto smooth')

        self.report({'INFO'}, f'Cleaned {self._processed} unique mesh data-blocks from {self._selected_mesh_total} mesh objects [auto smooth] ({", ".join(ops_enabled)})')

    def _activate_only(self, context, obj):
        prev_obj = self._current_active_obj
        if prev_obj is not None and prev_obj != obj and prev_obj.name in context.view_layer.objects:
            prev_obj.select_set(False)

        obj.select_set(True)
        context.view_layer.objects.active = obj
        self._current_active_obj = obj

    def _apply_shade_smooth(self, context, obj, angle):
        # Prefer data API for performance; fallback to operators only if needed.
        mesh = getattr(obj, 'data', None)
        mesh_key = mesh.as_pointer() if mesh is not None else None

        smooth_ok = True
        if mesh_key is None or mesh_key not in self._smoothed_mesh_keys:
            smooth_ok = self._set_smooth_faces_data(mesh)
            if smooth_ok and mesh_key is not None:
                self._smoothed_mesh_keys.add(mesh_key)

        auto_ok = self._set_auto_smooth_data(obj, mesh, angle)

        if smooth_ok and auto_ok:
            return

        self._activate_only(context, obj)
        if not smooth_ok:
            try:
                bpy.ops.object.shade_smooth()
                smooth_ok = True
                if mesh_key is not None:
                    self._smoothed_mesh_keys.add(mesh_key)
            except Exception:
                pass

        if not auto_ok:
            try:
                bpy.ops.object.shade_auto_smooth(angle=angle)
            except Exception:
                pass

    def _set_smooth_faces_data(self, mesh):
        if mesh is None or not hasattr(mesh, 'polygons'):
            return False

        poly_count = len(mesh.polygons)
        if poly_count == 0:
            return True

        try:
            mesh.polygons.foreach_set('use_smooth', [True] * poly_count)
            mesh.update()
            return True
        except Exception:
            return False

    def _set_auto_smooth_data(self, obj, mesh, angle):
        changed = False

        if self._set_attr_if_present(obj, 'use_auto_smooth', True):
            changed = True
        if self._set_attr_if_present(obj, 'auto_smooth_angle', angle):
            changed = True

        if mesh is not None:
            if self._set_attr_if_present(mesh, 'use_auto_smooth', True):
                changed = True
            if self._set_attr_if_present(mesh, 'auto_smooth_angle', angle):
                changed = True

        return changed

    def _set_attr_if_present(self, target, attr_name, value):
        if target is None or not hasattr(target, attr_name):
            return False

        try:
            setattr(target, attr_name, value)
            return True
        except Exception:
            return False

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

    def _tag_view3d_redraw(self, context):
        screen = getattr(context, 'screen', None)
        if screen is None:
            return

        for area in screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

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
