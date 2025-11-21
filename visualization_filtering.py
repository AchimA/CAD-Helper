# GPL-3.0 license
import bpy
import os
import json
from . import shared_functions

##############################################################################
# Panel
##############################################################################

class CAD_VIS_HELPER_PT_Panel(bpy.types.Panel):
    bl_idname = 'CAD_VIS_HELPER_PT_Panel'
    bl_label = 'Visualization & Filtering'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CAD Helper'
    bl_context = 'objectmode'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        active_metric = context.scene.cad_vis_active_metric
        # Visualization buttons
        row = layout.row(align=True)
        row.operator('object.cad_color_by_polycount', text='Poly', icon='MESH_DATA', depress=(active_metric == 'poly'))
        row.operator('object.cad_color_by_depth', text='Depth', icon='GROUP', depress=(active_metric == 'depth'))
        row.operator('object.cad_color_by_bbox', text='BBox', icon='CUBE', depress=(active_metric == 'bbox'))
        row.operator('object.cad_restore_colors', text='Restore', icon='LOOP_BACK', emboss=True)
        row = layout.row(align=True)
        row.prop(context.scene, 'cad_vis_scope', text='Scope')

        # Filter Range panel
        filter_box = layout.box()
        row = filter_box.row()
        row.label(text='Filter Range', icon='FILTER')
        row = filter_box.row()
        row.prop(context.scene, 'do_filter', text='Filter', toggle=True)
        row.prop(context.scene, 'do_highlight', text='Highlight', toggle=True)
        slider_row = filter_box.column()
        slider_row.enabled = context.scene.do_filter or context.scene.do_highlight
        slider_row.prop(context.scene, 'cad_vis_filter_min', text='Min', slider=True)
        slider_row.prop(context.scene, 'cad_vis_filter_max', text='Max', slider=True)
        filter_box.enabled = any(_METRIC_T_KEY in o for o in bpy.data.objects)


class CAD_VIS_HELPER_PT_Options(bpy.types.Panel):
    bl_idname = 'CAD_VIS_HELPER_PT_Options'
    bl_label = 'Options'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CAD Helper'
    bl_parent_id = 'CAD_VIS_HELPER_PT_Panel'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, 'cad_vis_scale_mode', text='Scale')
        layout.prop(context.scene, 'cad_vis_colormap', text='Colormap')
        row = layout.row(align=True)
        row.prop(context.scene, 'cad_vis_alpha_min', text='Alpha Min', slider=True)
        row.prop(context.scene, 'cad_vis_alpha_max', text='Max', slider=True)
        # Highlight color picker
        layout.prop(context.scene, 'cad_vis_highlight_color', text='Highlight Color')

##############################################################################
# Utilities
##############################################################################

_BACKUP_KEY = '__cad_orig_color'
_METRIC_T_KEY = '__cad_metric_t'

_DEF_SCOPE_ITEMS = [
    ('SELECTION', 'Selection', 'Use the current selection only'),
    ('SCENE', 'Scene', 'Use all objects in the scene'),
]

_DEF_SCALE_ITEMS = [
    ('RANKED', 'Ranked', 'Percentile-based (even distribution)'),
    ('LINEAR', 'Linear', 'Absolute value scaling'),
]

_ALGO_COLORMAPS = {'jet', 'turbo', 'cubehelix'}
_COLORMAP_CACHE = None

def _load_colormap_file():
    global _COLORMAP_CACHE
    if _COLORMAP_CACHE is not None:
        return _COLORMAP_CACHE
    path = os.path.join(os.path.dirname(__file__), 'colormaps.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Convert lists to tuples for stops
            cleaned = {}
            for name, stops in data.items():
                if isinstance(stops, list):
                    cleaned[name] = [(s[0], (s[1], s[2], s[3])) for s in stops]
            _COLORMAP_CACHE = cleaned
    except Exception:
        _COLORMAP_CACHE = {}
    return _COLORMAP_CACHE

def _interp_color(stops, t):
    if t <= stops[0][0]:
        return stops[0][1]
    if t >= stops[-1][0]:
        return stops[-1][1]
    for i in range(1, len(stops)):
        p0, c0 = stops[i-1]
        p1, c1 = stops[i]
        if t <= p1:
            span = (t - p0) / (p1 - p0) if p1 > p0 else 0.0
            r = c0[0] + (c1[0] - c0[0]) * span
            g = c0[1] + (c1[1] - c0[1]) * span
            b = c0[2] + (c1[2] - c0[2]) * span
            return (r, g, b)
    return stops[-1][1]

def _turbo(t):
    t = max(0.0, min(1.0, t))
    r = 0.13572138 + 4.61539260*t - 42.66032258*t*t + 132.13108234*t*t*t - 152.94239396*t*t*t*t + 59.28637943*t*t*t*t*t
    g = 0.09140261 + 2.19418839*t + 4.84296658*t*t - 14.18503333*t*t*t + 4.27729857*t*t*t*t + 2.82956604*t*t*t*t*t
    b = 0.10667330 + 12.64194608*t - 60.58204836*t*t + 145.20411400*t*t*t - 162.10672131*t*t*t*t + 61.65521006*t*t*t*t*t
    return (max(0.0,min(1.0,r)), max(0.0,min(1.0,g)), max(0.0,min(1.0,b)))

def _cubehelix(t):
    import math
    t = max(0.0, min(1.0, t))
    angle = 2.0 * math.pi * (0.5 + t)
    fract = t
    amp = 0.5 * (1.0 - 0.5 + 0.5 * fract)
    r = fract + amp * (-0.14861 * math.cos(angle) + 1.78277 * math.sin(angle))
    g = fract + amp * (-0.29227 * math.cos(angle) - 0.90649 * math.sin(angle))
    b = fract + amp * (1.97294 * math.cos(angle))
    return (max(0.0,min(1.0,r)), max(0.0,min(1.0,g)), max(0.0,min(1.0,b)))

def get_colormap_color(name: str, t: float):
    name = name or 'jet'
    if name == 'jet':
        r, g, b, _ = jet(t); return (r, g, b)
    if name == 'turbo':
        return _turbo(t)
    if name == 'cubehelix':
        return _cubehelix(t)
    stops_dict = _load_colormap_file()
    stops = stops_dict.get(name)
    if stops:
        return _interp_color(stops, t)
    import colorsys
    r, g, b = colorsys.hsv_to_rgb(t, 1.0, 1.0)
    return (r, g, b)

def ensure_object_color_viewports():
    """Switch all 3D viewports to OBJECT color mode so Object.color shows."""
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.color_type = 'OBJECT'


def jet(t: float):
    """Jet colormap (blue -> cyan -> green -> yellow -> red)."""
    t = max(0.0, min(1.0, t))
    if t < 0.25:  # blue -> cyan
        r = 0.0
        g = 4.0 * t
        b = 1.0
    elif t < 0.5:  # cyan -> green
        r = 0.0
        g = 1.0
        b = 1.0 - 4.0 * (t - 0.25)
    elif t < 0.75:  # green -> yellow
        r = 4.0 * (t - 0.5)
        g = 1.0
        b = 0.0
    else:  # yellow -> red
        r = 1.0
        g = 1.0 - 4.0 * (t - 0.75)
        b = 0.0
    return (r, g, b, 1.0)


def backup_color(obj):
    if _BACKUP_KEY not in obj and hasattr(obj, 'color'):
        obj[_BACKUP_KEY] = list(obj.color)


def apply_metric_colors(objects, values):
    if not objects:
        return 0
    
    scale_mode = getattr(bpy.context.scene, 'cad_vis_scale_mode', 'RANKED')
    colormap = getattr(bpy.context.scene, 'cad_vis_colormap', 'jet')
    alpha_min = getattr(bpy.context.scene, 'cad_vis_alpha_min', 1.0)
    alpha_max = getattr(bpy.context.scene, 'cad_vis_alpha_max', 1.0)
    
    # Compute normalized t values based on scale mode
    if scale_mode == 'RANKED':
        # Percentile-based: sort by value and assign rank
        sorted_objs = sorted(objects, key=lambda o: values.get(o, 0.0))
        count = len(sorted_objs)
        t_map = {}
        for i, obj in enumerate(sorted_objs):
            t_map[obj] = i / (count - 1) if count > 1 else 0.0
    else:
        # Linear: normalize by max value
        max_val = max(values.values()) if values else 0
        t_map = {obj: (values.get(obj, 0.0) / max_val if max_val else 0.0) for obj in objects}
    
    # Apply colors
    for obj in objects:
        backup_color(obj)
        t = t_map[obj]
        obj[_METRIC_T_KEY] = t
        r, g, b = get_colormap_color(colormap, t)
        alpha = alpha_min + t * (alpha_max - alpha_min)
        obj.color = (r, g, b, alpha)
    return len(objects)


def hierarchy_depth(obj):
    d = 0
    p = obj.parent
    while p:
        d += 1
        p = p.parent
    return d

##############################################################################
# Operators
##############################################################################

class CAD_ColorByDepth(bpy.types.Operator):
    """Color objects by hierarchy depth (root -> deep)."""
    bl_idname = 'object.cad_color_by_depth'
    bl_label = 'Color by Depth'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.scene is None:
            return False
        scope = getattr(context.scene, 'cad_vis_scope', 'SELECTION')
        if scope == 'SELECTION':
            return bool(context.selected_objects)
        return bool(bpy.data.objects)

    def execute(self, context):
        context.scene.cad_vis_active_metric = 'depth'
        # Reset alpha defaults each visualization
        context.scene.cad_vis_alpha_min = 0.25
        context.scene.cad_vis_alpha_max = 0.25
        # Reset filter range
        context.scene.cad_vis_filter_min = 0.0
        context.scene.cad_vis_filter_max = 100.0
        scope = context.scene.cad_vis_scope
        if scope == 'SELECTION':
            objs = list(context.selected_objects)
        else:
            objs = list(bpy.data.objects)
        if not objs:
            shared_functions.report_info(self, 'No objects for depth metric')
            return {'CANCELLED'}
        depths = {o: hierarchy_depth(o) for o in objs}
        count = apply_metric_colors(objs, depths)
        ensure_object_color_viewports()
        shared_functions.report_info(self, f'Colored {count} objects by depth')
        return {'FINISHED'}


class CAD_ColorByPolycount(bpy.types.Operator):
    """Color mesh objects by face count (low -> high)."""
    bl_idname = 'object.cad_color_by_polycount'
    bl_label = 'Color by Polycount'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.scene is None:
            return False
        scope = getattr(context.scene, 'cad_vis_scope', 'SELECTION')
        if scope == 'SELECTION':
            return any(o.type == 'MESH' for o in context.selected_objects)
        return any(o.type == 'MESH' for o in bpy.data.objects)

    def execute(self, context):
        context.scene.cad_vis_active_metric = 'poly'
        context.scene.cad_vis_alpha_min = 0.25
        context.scene.cad_vis_alpha_max = 0.25
        context.scene.cad_vis_filter_min = 0.0
        context.scene.cad_vis_filter_max = 100.0
        scope = context.scene.cad_vis_scope
        if scope == 'SELECTION':
            objs = [o for o in context.selected_objects if o.type == 'MESH']
        else:
            objs = [o for o in bpy.data.objects if o.type == 'MESH']
        if not objs:
            shared_functions.report_info(self, 'No mesh objects for polycount metric')
            return {'CANCELLED'}
        polycounts = {o: len(o.data.polygons) for o in objs}
        count = apply_metric_colors(objs, polycounts)
        ensure_object_color_viewports()
        shared_functions.report_info(self, f'Colored {count} mesh objects by polycount')
        return {'FINISHED'}


class CAD_ColorByBBox(bpy.types.Operator):
    """Color objects by bounding box volume (small -> large)."""
    bl_idname = 'object.cad_color_by_bbox'
    bl_label = 'Color by BBox Volume'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.scene is None:
            return False
        scope = getattr(context.scene, 'cad_vis_scope', 'SELECTION')
        if scope == 'SELECTION':
            return bool(context.selected_objects)
        return bool(bpy.data.objects)

    def execute(self, context):
        context.scene.cad_vis_active_metric = 'bbox'
        context.scene.cad_vis_alpha_min = 0.5
        context.scene.cad_vis_alpha_max = 0.5
        context.scene.cad_vis_filter_min = 0.0
        context.scene.cad_vis_filter_max = 100.0
        scope = context.scene.cad_vis_scope
        if scope == 'SELECTION':
            objs = list(context.selected_objects)
        else:
            objs = list(bpy.data.objects)
        if not objs:
            shared_functions.report_info(self, 'No objects for bounding box metric')
            return {'CANCELLED'}
        # Use bounding box volume for metric
        bbox_vals = {o: o.dimensions.x * o.dimensions.y * o.dimensions.z for o in objs}
        count = apply_metric_colors(objs, bbox_vals)
        ensure_object_color_viewports()
        shared_functions.report_info(self, f'Colored {count} objects by bounding box volume')
        return {'FINISHED'}


class CAD_RestoreColors(bpy.types.Operator):
    """Restore original object colors after temporary visualization."""
    bl_idname = 'object.cad_restore_colors'
    bl_label = 'Restore Colors'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.scene is None:
            return False
        return any(_BACKUP_KEY in o for o in bpy.data.objects)

    def execute(self, context):
        context.scene.cad_vis_active_metric = ''
        restored = 0
        for o in bpy.data.objects:
            if _BACKUP_KEY in o:
                try:
                    o.color = o[_BACKUP_KEY]
                except Exception:
                    pass
                del o[_BACKUP_KEY]
                restored += 1
            if _METRIC_T_KEY in o:
                del o[_METRIC_T_KEY]
        shared_functions.report_info(self, f'Restored {restored} objects')
        return {'FINISHED'}


def _update_do_highlight(self, context):
    # When highlight is toggled, re-apply filter selection to update colors
    _apply_filter_selection(context)

##############################################################################
# Registration
##############################################################################

classes = (
    CAD_VIS_HELPER_PT_Panel,
    CAD_VIS_HELPER_PT_Options,
    CAD_ColorByDepth,
    CAD_ColorByPolycount,
    CAD_ColorByBBox,
    CAD_RestoreColors,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)
        print(f'registered {c}')
    bpy.types.Scene.cad_vis_scope = bpy.props.EnumProperty(
        name='Scope',
        items=_DEF_SCOPE_ITEMS,
        default='SELECTION'
    )
    def _update_scale_mode(self, context):
        # Switching scale mode requires full recomputation - just store for next operator run
        # Cannot recolor here as we don't have the original values dict
        pass
    bpy.types.Scene.cad_vis_scale_mode = bpy.props.EnumProperty(
        name='Scale Mode',
        items=_DEF_SCALE_ITEMS,
        default='RANKED',
        description='Ranked distributes colors evenly; Linear uses absolute values',
        update=_update_scale_mode
    )
    def _update_alpha_range(self, context):
        alpha_min = context.scene.cad_vis_alpha_min
        alpha_max = context.scene.cad_vis_alpha_max
        for o in bpy.data.objects:
            if _METRIC_T_KEY in o and _BACKUP_KEY in o:
                t = o[_METRIC_T_KEY]
                cm = context.scene.cad_vis_colormap
                r, g, b = get_colormap_color(cm, t)
                alpha = alpha_min + t * (alpha_max - alpha_min)
                o.color = (r, g, b, alpha)
    bpy.types.Scene.cad_vis_alpha_min = bpy.props.FloatProperty(
        name='Alpha Min',
        description='Alpha at t=0',
        default=0.5,
        min=0.0,
        max=1.0,
        precision=2,
        step=1,
        update=_update_alpha_range
    )
    bpy.types.Scene.cad_vis_alpha_max = bpy.props.FloatProperty(
        name='Alpha Max',
        description='Alpha at t=1',
        default=0.5,
        min=0.0,
        max=1.0,
        precision=2,
        step=1,
        update=_update_alpha_range
    )
    
    def _update_filter_min(self, context):
        # Constrain min to not exceed max
        if context.scene.cad_vis_filter_min > context.scene.cad_vis_filter_max:
            context.scene.cad_vis_filter_max = context.scene.cad_vis_filter_min
        _apply_filter_selection(context)
    
    def _update_filter_max(self, context):
        # Constrain max to not go below min
        if context.scene.cad_vis_filter_max < context.scene.cad_vis_filter_min:
            context.scene.cad_vis_filter_min = context.scene.cad_vis_filter_max
        _apply_filter_selection(context)
    
    bpy.types.Scene.cad_vis_filter_min = bpy.props.FloatProperty(
        name='Filter Min',
        description='Minimum percentile to select',
        default=0.0,
        min=0.0,
        max=100.0,
        subtype='PERCENTAGE',
        update=_update_filter_min
    )
    bpy.types.Scene.cad_vis_filter_max = bpy.props.FloatProperty(
        name='Filter Max',
        description='Maximum percentile to select',
        default=100.0,
        min=0.0,
        max=100.0,
        subtype='PERCENTAGE',
        update=_update_filter_max
    )
    bpy.types.Scene.do_filter = bpy.props.BoolProperty(
        name='Filter',
        description='Enable filter range selection',
        default=False
    )
    bpy.types.Scene.do_highlight = bpy.props.BoolProperty(
        name='Highlight',
        description='Highlight filtered objects with custom color',
        default=False,
        update=_update_do_highlight
    )
    bpy.types.Scene.cad_vis_highlight_color = bpy.props.FloatVectorProperty(
        name='Highlight Color',
        description='Highlight color RGBA',
        default=(1.0, 0.5, 0.0, 0.9),
        min=0.0,
        max=1.0,
        size=4,
        subtype='COLOR',
        options={'ANIMATABLE'}
    )
    bpy.types.Scene.cad_vis_active_metric = bpy.props.StringProperty(
        name='Active Metric',
        description='Currently displayed metric',
        default=''
    )

    def _update_colormap(self, context):
        cm = context.scene.cad_vis_colormap
        alpha_min = context.scene.cad_vis_alpha_min
        alpha_max = context.scene.cad_vis_alpha_max
        for o in bpy.data.objects:
            if _METRIC_T_KEY in o and _BACKUP_KEY in o:
                t = o[_METRIC_T_KEY]
                r, g, b = get_colormap_color(cm, t)
                alpha = alpha_min + t * (alpha_max - alpha_min)
                o.color = (r, g, b, alpha)
    # Build enum items dynamically from JSON + algorithmic set
    file_names = sorted(_load_colormap_file().keys())
    all_names = sorted(set(file_names + list(_ALGO_COLORMAPS)))
    enum_items = [(n, n, f'Colormap {n}') for n in all_names]
    bpy.types.Scene.cad_vis_colormap = bpy.props.EnumProperty(
        name='Colormap',
        items=enum_items,
        default='jet',
        description='Color mapping applied to metric values',
        update=_update_colormap,
    )

def _apply_filter_selection(context):
    """Apply selection filter based on stored metric_t values."""
    if not (getattr(context.scene, 'do_filter', False) or getattr(context.scene, 'do_highlight', False)):
        return
    min_t = context.scene.cad_vis_filter_min / 100.0
    max_t = context.scene.cad_vis_filter_max / 100.0
    allowed_types = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'VOLUME'}
    visualized = [o for o in bpy.data.objects if _METRIC_T_KEY in o and o.type in allowed_types and hasattr(o, 'dimensions') and (o.dimensions.x * o.dimensions.y * o.dimensions.z) > 0]
    if not visualized:
        return
    # Only clear selections if filter is active
    do_filter = getattr(context.scene, 'do_filter', False)
    highlight = getattr(context.scene, 'do_highlight', False)
    highlight_color = getattr(context.scene, 'cad_vis_highlight_color', (1.0, 0.5, 0.0, 0.9))
    colormap = getattr(context.scene, 'cad_vis_colormap', 'jet')
    alpha_min = getattr(context.scene, 'cad_vis_alpha_min', 1.0)
    alpha_max = getattr(context.scene, 'cad_vis_alpha_max', 1.0)
    if do_filter:
        # Clear all selections first
        for o in context.view_layer.objects:
            o.select_set(False)
    for o in visualized:
        t = o[_METRIC_T_KEY]
        in_range = min_t <= t <= max_t
        if do_filter and in_range:
            try:
                o.select_set(True)
                if hasattr(o, 'color'):
                    if highlight:
                        o.color = highlight_color
                    else:
                        r, g, b = get_colormap_color(colormap, t)
                        alpha = alpha_min + t * (alpha_max - alpha_min)
                        o.color = (r, g, b, alpha)
            except Exception:
                pass
        elif highlight and in_range and not do_filter:
            try:
                # Only change color, do not select
                if hasattr(o, 'color'):
                    o.color = highlight_color
            except Exception:
                pass
        else:
            # Restore colormap color for objects outside filter/highlight
            if hasattr(o, 'color'):
                r, g, b = get_colormap_color(colormap, t)
                alpha = alpha_min + t * (alpha_max - alpha_min)
                o.color = (r, g, b, alpha)

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
        print(f'unregistered {c}')
    if hasattr(bpy.types.Scene, 'cad_vis_scope'):
        del bpy.types.Scene.cad_vis_scope
    if hasattr(bpy.types.Scene, 'cad_vis_scale_mode'):
        del bpy.types.Scene.cad_vis_scale_mode
    if hasattr(bpy.types.Scene, 'cad_vis_alpha_min'):
        del bpy.types.Scene.cad_vis_alpha_min
    if hasattr(bpy.types.Scene, 'cad_vis_alpha_max'):
        del bpy.types.Scene.cad_vis_alpha_max
    if hasattr(bpy.types.Scene, 'cad_vis_filter_min'):
        del bpy.types.Scene.cad_vis_filter_min
    if hasattr(bpy.types.Scene, 'cad_vis_filter_max'):
        del bpy.types.Scene.cad_vis_filter_max
    if hasattr(bpy.types.Scene, 'cad_vis_colormap'):
        del bpy.types.Scene.cad_vis_colormap
    if hasattr(bpy.types.Scene, 'do_filter'):
        del bpy.types.Scene.do_filter
    if hasattr(bpy.types.Scene, 'cad_vis_active_metric'):
        del bpy.types.Scene.cad_vis_active_metric
