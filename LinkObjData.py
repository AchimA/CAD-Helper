# GPL-3.0 license

import bpy
import re

from . import shared_functions



##############################################################################
# Helper Functions
##############################################################################
# Metric calculation function for binning

def get_object_metrics(ob):
    if ob.type != 'MESH':
        return None
    mesh = ob.data
    v_count = len(mesh.vertices)
    bbox = ob.bound_box
    xs = [v[0] for v in bbox]
    ys = [v[1] for v in bbox]
    zs = [v[2] for v in bbox]
    x_len = max(xs) - min(xs)
    y_len = max(ys) - min(ys)
    z_len = max(zs) - min(zs)
    volume = x_len * y_len * z_len
    surface = sum(f.area for f in mesh.polygons)
    return {
        'vertex_count': v_count,
        'x_len': x_len,
        'y_len': y_len,
        'z_len': z_len,
        'volume': volume,
        'surface': surface
    }

def summarize_and_bin_objects(objects, scene):
    import statistics
    wm = bpy.context.window_manager
    total = len(objects)
    wm.progress_begin(0, total)
    metrics = []
    for idx, ob in enumerate(objects):
        wm.progress_update(idx)
        m = get_object_metrics(ob)
        if m:
            metrics.append(m)
    wm.progress_end()
    # Binning
    tol_vertex = scene.cad_bin_tol_vertex / 100.0
    tol_axes = scene.cad_bin_tol_axes / 100.0
    tol_surface = scene.cad_bin_tol_surface / 100.0
    tol_volume = scene.cad_bin_tol_volume / 100.0
    bins = []
    for ob, metrics in zip(objects, metrics):
        found_bin = None
        for b in bins:
            avg = b['avg']
            if (
                abs(metrics['vertex_count'] - avg['vertex_count']) <= tol_vertex * avg['vertex_count'] and
                abs(metrics['x_len'] - avg['x_len']) <= tol_axes * avg['x_len'] and
                abs(metrics['y_len'] - avg['y_len']) <= tol_axes * avg['y_len'] and
                abs(metrics['z_len'] - avg['z_len']) <= tol_axes * avg['z_len'] and
                abs(metrics['surface'] - avg['surface']) <= tol_surface * avg['surface'] and
                abs(metrics['volume'] - avg['volume']) <= tol_volume * avg['volume']
            ):
                found_bin = b
                break
        if found_bin:
            found_bin['objects'].append(ob)
            n = len(found_bin['objects'])
            for k in avg:
                avg[k] = (avg[k] * (n-1) + metrics[k]) / n
        else:
            bins.append({'objects': [ob], 'avg': metrics.copy()})
    bins = [b for b in bins if len(b['objects']) > 1]
    bins.sort(key=lambda b: len(b['objects']), reverse=True)
    # Populate linkable_collections with bins
    scene.linkable_collections.clear()
    for i, b in enumerate(bins):
        item = scene.linkable_collections.add()
        item.name = f"Bin {i+1}"
        for obj in b['objects']:
            ob_item = item.objects.add()
            ob_item.name = obj.name
        item.N_objects = len(b['objects'])
##############################################################################


# Assign linkable collection.
class LinkableCollectionItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Items Name', default='Unknown')
    objects: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup, name='Linkable Objects')
    N_objects: bpy.props.IntProperty(name='Number of Objects', default=0)

def ListIndexCallback(self, value):
    # bpy.ops.generate_markers.change_marker() #other class function
    try:
        bpy.ops.object.list_select_collection()
    except:
        pass

class LIST_OT_SelectCollection(bpy.types.Operator):
    bl_idname = "object.list_select_collection"
    bl_label = "Select Collection"

    @classmethod
    def poll(cls, context):
        return context.scene.linkable_collections
    
    def execute(self, context):
        linkable_collections = context.scene.linkable_collections
        index = context.scene.lin_col_idx

        name = linkable_collections[index].name
        objects = [bpy.data.objects[o.name] for o in list(linkable_collections[index].objects)]

        bpy.ops.object.select_all(action='DESELECT')
        # context.view_layer.objects.active = None
        for obj in objects:
            obj.select_set(True)
            context.view_layer.objects.active = obj

        return{'FINISHED'}
    
class LIST_OT_LinkCollection(bpy.types.Operator):
    bl_idname = "object.list_link_collection"
    bl_label = "Link Collection"

    @classmethod
    def poll(cls, context):
        return context.scene.linkable_collections
    
    def invoke(self, context, event):
        # use the event parameter so invoke_confirm shows
        return context.window_manager.invoke_confirm(
            self,
            event,
            title='Proceed and link selected collection?',
            message='Warning: This will overwrite mesh data of target objects.',
            confirm_text='Link',
            icon='WARNING',
            )
    
    def execute(self, context):
        # invoke the link operator so the confirm dialog appears
        bpy.ops.object.link_collections('INVOKE_DEFAULT')
        return{'FINISHED'}


class LIST_OT_LinkALLCollections(bpy.types.Operator):
    bl_idname = "object.link_all_collections"
    bl_label = "Link All Collections"

    @classmethod
    def poll(cls, context):
        return context.scene.linkable_collections
    
    def invoke(self, context, event):
        # use the event parameter so invoke_confirm shows
        return context.window_manager.invoke_confirm(
            self,
            event,
            title='Proceed and link selected collection?',
            message='Warning: This will overwrite mesh data of target objects.',
            confirm_text='Link',
            icon='WARNING',
            )
    
    def execute(self, context):
        linkable_collections = context.scene.linkable_collections
        context.scene.lin_col_idx = 0
        num_coll = len(linkable_collections)

        # run the link operator in EXEC mode (no confirm) for batch processing
        while linkable_collections:
            bpy.ops.object.link_collections()
            # the link operator now removes the current collection itself
            context.scene.lin_col_idx = min(max(0, context.scene.lin_col_idx-1), len(linkable_collections)-1)
        
        self.report({'INFO'}, f'Linked {num_coll} collections')
        return {'FINISHED'}

class LINKABLE_COLLECTION_UL_LIST(bpy.types.UIList):
    """
    LINKABLE_COLLECTION_UL_LIST
    """

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        # Set Icon
        custom_icon = 'COLLECTION_COLOR_02'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=f'{item.N_objects:4d}x   {item.name}', icon = custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = custom_icon)

class UIListPanelLinkableCollection(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Instance Detection & Linking"
    bl_idname = "PANEL_PT_instance_detection_linking"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CAD Helper'
    bl_context = 'objectmode'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object

        row = layout.row()
        row.operator(
            'object.refresh_linkable_collection',
            text=f'Rescan Selection',
            icon='FILE_REFRESH'
            )

        layout.template_list('LINKABLE_COLLECTION_UL_LIST', 'a list', scene, 'linkable_collections', scene, 'lin_col_idx')
        row = layout.row()
        row.operator(
            'object.list_link_collection',
            text='Link Collection',
            icon='LINKED'
            )
        row.operator(
            'object.link_all_collections',
            text=f'Link all {len(context.scene.linkable_collections)} collections',
            icon='LINKED'
            )

class InstanceDetectionTolerancesPanel(bpy.types.Panel):
    bl_label = "Instance Detection Tolerances"
    bl_idname = "PANEL_PT_instance_detection_tolerances"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CAD Helper'
    bl_context = 'objectmode'
    bl_parent_id = "PANEL_PT_instance_detection_linking"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        grid = layout.grid_flow(row_major=True, columns=2, even_columns=True, even_rows=True, align=True)
        grid.prop(scene, 'cad_bin_tol_vertex', text="Vertex Count (%)")
        grid.prop(scene, 'cad_bin_tol_axes', text="Axes (%)")
        grid.prop(scene, 'cad_bin_tol_surface', text="Surface (%)")
        grid.prop(scene, 'cad_bin_tol_volume', text="Volume (%)")

class RefreshLinkableCollection(bpy.types.Operator):
    '''
    Refresh the collection for Instance Detection & Linking
    '''
    bl_idname = 'object.refresh_linkable_collection'
    bl_label = 'Refresh Instance Detection & Linking'
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        objects = context.selected_objects
        prop_types = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'VOLUME']
        objects = [ob for ob in objects if ob.type in prop_types]

        # Single efficient summary and binning
        summarize_and_bin_objects(objects, context.scene)
        
        return {'FINISHED'}

def debug_object_metrics(objects):
    print("--- CAD Helper Object Metrics Debug (Summary) ---")
    metrics = []
    wm = bpy.context.window_manager
    total = len(objects)
    wm.progress_begin(0, total)
    for idx, ob in enumerate(objects):
        wm.progress_update(idx)
        if ob.type != 'MESH':
            continue
        mesh = ob.data
        v_count = len(mesh.vertices)
        bbox = ob.bound_box
        xs = [v[0] for v in bbox]
        ys = [v[1] for v in bbox]
        zs = [v[2] for v in bbox]
        x_len = max(xs) - min(xs)
        y_len = max(ys) - min(ys)
        z_len = max(zs) - min(zs)
        volume = x_len * y_len * z_len
        surface = sum(f.area for f in mesh.polygons)
        metrics.append((v_count, x_len, y_len, z_len, volume, surface))
        percent = int((idx + 1) / total * 100) if total else 100
        print(f"Progress: {percent}%", end='\r')
    wm.progress_end()
    print()
    if not metrics:
        print("No mesh objects found.")
        return
    import statistics
    v_counts = [m[0] for m in metrics]
    x_lens = [m[1] for m in metrics]
    y_lens = [m[2] for m in metrics]
    z_lens = [m[3] for m in metrics]
    volumes = [m[4] for m in metrics]
    surfaces = [m[5] for m in metrics]
    print(f"Total mesh objects: {len(metrics)}")
    print(f"Vertex count: min={min(v_counts)}, max={max(v_counts)}, mean={statistics.mean(v_counts):.2f}, stdev={statistics.stdev(v_counts):.2f}")
    print(f"X axis: min={min(x_lens):.4f}, max={max(x_lens):.4f}, mean={statistics.mean(x_lens):.4f}, stdev={statistics.stdev(x_lens):.4f}")
    print(f"Y axis: min={min(y_lens):.4f}, max={max(y_lens):.4f}, mean={statistics.mean(y_lens):.4f}, stdev={statistics.stdev(y_lens):.4f}")
    print(f"Z axis: min={min(z_lens):.4f}, max={max(z_lens):.4f}, mean={statistics.mean(z_lens):.4f}, stdev={statistics.stdev(z_lens):.4f}")
    print(f"Bounding box volume: min={min(volumes):.4f}, max={max(volumes):.4f}, mean={statistics.mean(volumes):.4f}, stdev={statistics.stdev(volumes):.4f}")
    print(f"Face surface area: min={min(surfaces):.4f}, max={max(surfaces):.4f}, mean={statistics.mean(surfaces):.4f}, stdev={statistics.stdev(surfaces):.4f}")
    print("--- End Debug Summary ---")

class LinkCollections(bpy.types.Operator):
    bl_idname = "object.link_collections"
    bl_label = "Link Collections"

    def execute(self, context):
        linkable_collections = context.scene.linkable_collections
        index = context.scene.lin_col_idx

        self.report({'INFO'}, f"Linking... '{linkable_collections[index].name}'")

        objects = [bpy.data.objects[o.name] for o in list(linkable_collections[index].objects)]

        first_object = objects.pop(0)

        for obj in objects:
            obj.data = first_object.data

        # remove the linked collection now that linking is complete
        context.scene.linkable_collections.remove(index)
        context.scene.lin_col_idx = min(max(0, index-1), len(context.scene.linkable_collections)-1)

        return {'FINISHED'}
    
##############################################################################
# Add-On Handling
##############################################################################
classes = (
    RefreshLinkableCollection,
    LinkableCollectionItem,
    LINKABLE_COLLECTION_UL_LIST,
    UIListPanelLinkableCollection,
    InstanceDetectionTolerancesPanel,
    LinkCollections,
    LIST_OT_LinkALLCollections,
    LIST_OT_SelectCollection,
    LIST_OT_LinkCollection,
)

def register():
    # register classes
    for c in classes:
        bpy.utils.register_class(c)
        print(f'registered {c}')

    bpy.types.Scene.linkable_collections = bpy.props.CollectionProperty(type=LinkableCollectionItem)
    bpy.types.Scene.lin_col_idx = bpy.props.IntProperty(name='Index', update=ListIndexCallback)
    bpy.types.Scene.cad_bin_tol_vertex = bpy.props.FloatProperty(
        name="Vertex Count Tolerance (%)", default=5.0, min=0.0, max=100.0)
    bpy.types.Scene.cad_bin_tol_axes = bpy.props.FloatProperty(
        name="Principal Axes Tolerance (%)", default=1.0, min=0.0, max=100.0)
    bpy.types.Scene.cad_bin_tol_surface = bpy.props.FloatProperty(
        name="Face Surface Tolerance (%)", default=1.0, min=0.0, max=100.0)
    bpy.types.Scene.cad_bin_tol_volume = bpy.props.FloatProperty(
        name="Bounding Box Volume Tolerance (%)", default=5.0, min=0.0, max=100.0)
    bpy.types.Scene.show_instance_tolerances = bpy.props.BoolProperty(
        name="Show Instance Detection Tolerances", default=True)

def unregister():
    # unregister classes
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
        print(f'unregistered {c}')

    del bpy.types.Scene.linkable_collections
    del bpy.types.Scene.lin_col_idx
    del bpy.types.Scene.cad_bin_tol_vertex
    del bpy.types.Scene.cad_bin_tol_axes
    del bpy.types.Scene.cad_bin_tol_surface
    del bpy.types.Scene.cad_bin_tol_volume
    del bpy.types.Scene.show_instance_tolerances


##############################################################################
# Helper Functions
##############################################################################
# Metric calculation function for binning

def get_object_metrics(ob):
    if ob.type != 'MESH':
        return None
    mesh = ob.data
    v_count = len(mesh.vertices)
    bbox = ob.bound_box
    xs = [v[0] for v in bbox]
    ys = [v[1] for v in bbox]
    zs = [v[2] for v in bbox]
    x_len = max(xs) - min(xs)
    y_len = max(ys) - min(ys)
    z_len = max(zs) - min(zs)
    volume = x_len * y_len * z_len
    surface = sum(f.area for f in mesh.polygons)
    return {
        'vertex_count': v_count,
        'x_len': x_len,
        'y_len': y_len,
        'z_len': z_len,
        'volume': volume,
        'surface': surface
    }

def summarize_and_bin_objects(objects, scene):
    import statistics
    wm = bpy.context.window_manager
    total = len(objects)
    wm.progress_begin(0, total)
    metrics = []
    for idx, ob in enumerate(objects):
        wm.progress_update(idx)
        m = get_object_metrics(ob)
        if m:
            metrics.append(m)
    wm.progress_end()
    # Binning
    tol_vertex = scene.cad_bin_tol_vertex / 100.0
    tol_axes = scene.cad_bin_tol_axes / 100.0
    tol_surface = scene.cad_bin_tol_surface / 100.0
    tol_volume = scene.cad_bin_tol_volume / 100.0
    bins = []
    for ob, metrics in zip(objects, metrics):
        found_bin = None
        for b in bins:
            avg = b['avg']
            if (
                abs(metrics['vertex_count'] - avg['vertex_count']) <= tol_vertex * avg['vertex_count'] and
                abs(metrics['x_len'] - avg['x_len']) <= tol_axes * avg['x_len'] and
                abs(metrics['y_len'] - avg['y_len']) <= tol_axes * avg['y_len'] and
                abs(metrics['z_len'] - avg['z_len']) <= tol_axes * avg['z_len'] and
                abs(metrics['surface'] - avg['surface']) <= tol_surface * avg['surface'] and
                abs(metrics['volume'] - avg['volume']) <= tol_volume * avg['volume']
            ):
                found_bin = b
                break
        if found_bin:
            found_bin['objects'].append(ob)
            n = len(found_bin['objects'])
            for k in avg:
                avg[k] = (avg[k] * (n-1) + metrics[k]) / n
        else:
            bins.append({'objects': [ob], 'avg': metrics.copy()})
    bins = [b for b in bins if len(b['objects']) > 1]
    bins.sort(key=lambda b: len(b['objects']), reverse=True)
    # Populate linkable_collections with bins
    scene.linkable_collections.clear()
    for i, b in enumerate(bins):
        item = scene.linkable_collections.add()
        item.name = f"Bin {i+1}"
        for obj in b['objects']:
            ob_item = item.objects.add()
            ob_item.name = obj.name
        item.N_objects = len(b['objects'])
