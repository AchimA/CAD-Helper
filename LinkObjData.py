# GPL-3.0 license

import bpy
import re

from . import shared_functions

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
    bl_label = "[Exp.] CAD Object Data Helper"
    bl_idname = "PANEL_PT_linkable_collection"
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

class RefreshLinkableCollection(bpy.types.Operator):
    '''
    Refresh the colletion of linkable objects
    '''
    bl_idname = 'object.refresh_linkable_collection'
    bl_label = 'Refresh Linkable Collection'
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        objects = context.selected_objects
        prop_types = ['MESH','CURVE','SURFACE','META','FONT','VOLUME']
        objects = [ob for ob in objects if ob.type in prop_types]

        p = re.compile('^(.*?)(?=\.\d*$|$)')

        unique_names = []
        for ob in objects:
            match = p.match(ob.name)
            match = match.group()
            if match not in unique_names:
                unique_names.append(match)
        
        context.scene.linkable_collections.clear()
        for u_name in unique_names:
            u_objects = []
            for ob in objects:
                # add object to list if if it has the same name
                if u_name == p.match(ob.name).group():
                    u_objects.append(ob)
            if len(u_objects) > 1:
                item = context.scene.linkable_collections.add()
                item.name = u_name
                for obj in u_objects:
                    ob = item.objects.add()
                    ob.name = obj.name
                item.N_objects = len(u_objects)
                # ToDo:
                # Create Icon here...

        return {'FINISHED'}

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


def unregister():
    # unregister classes
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
        print(f'unregistered {c}')

    del bpy.types.Scene.linkable_collections
    del bpy.types.Scene.lin_col_idx
