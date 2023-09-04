# GPL-3.0 license

import bpy
import re

from bpy.types import Context
from . import shared_functions
import tempfile
import os


# Assign linkable collection.
class LinkableCollectionItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Items Name', default='Unknown')
    objects: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup, name='Linkable Objects')
    N_objects: bpy.props.IntProperty(name='Eumber of Objects', default=0)

def ListIndexCallback(self, value):
    # bpy.ops.generate_markers.change_marker() #other class function
    
    bpy.ops.object.list_select_collection()

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
        # bpy.context.view_layer.objects.active = None
        for obj in objects:
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

        return{'FINISHED'}
    
class LIST_OT_LinkCollection(bpy.types.Operator):
    bl_idname = "object.list_link_collection"
    bl_label = "Link Collection"

    @classmethod
    def poll(cls, context):
        return context.scene.linkable_collections
    
    def execute(self, context):
        linkable_collections = context.scene.linkable_collections
        index = context.scene.lin_col_idx

        name = linkable_collections[index].name
        bpy.ops.object.link_collections()
        
        context.scene.linkable_collections.remove(index)
        context.scene.lin_col_idx = min(max(0, index-1), len(linkable_collections)-1)

        return{'FINISHED'}


class LIST_OT_LinkALLCollections(bpy.types.Operator):
    bl_idname = "object.link_all_collections"
    bl_label = "Link All Collections"

    @classmethod
    def poll(cls, context):
        return context.scene.linkable_collections

    def execute(self, context):
        self.report({'INFO'}, "Liniking all collections'")
        
        linkable_collections = context.scene.linkable_collections
        index = 0

        while linkable_collections:
            bpy.ops.object.link_collections()
            
            context.scene.linkable_collections.remove(index)
            context.scene.lin_col_idx = min(max(0, index-1), len(linkable_collections)-1)

        return {'FINISHED'}

class LinkableCollection_UL_List(bpy.types.UIList):
    """Demo UIList."""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        # We could write some code to decide which icon to use here...
        custom_icon = 'COLLECTION_COLOR_02'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=f'{item.N_objects:4d}x   {item.name}', icon = custom_icon)
            

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = custom_icon)

class UIListPanelLinkableCollection(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "CAD Object Data Helper"
    bl_idname = "panel_linkable_collection"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CAD Obj.Dat. Helper'
    bl_context = 'objectmode'

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
        
        layout.template_list('LinkableCollection_UL_List', 'a list', scene, 'linkable_collections', scene, 'lin_col_idx')
        
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
        objects = bpy.context.selected_objects
        prop_types = ['MESH','CURVE','SURFACE','META','FONT','VOLUME']
        objects = [ob for ob in objects if ob.type in prop_types]

        p = re.compile('^(.*?)(?=\.\d*$|$)')

        unique_names = []
        for ob in objects:
            print(ob.name)
            match = p.match(ob.name)
            match = match.group()
            if match not in unique_names:
                unique_names.append(match)
        
        bpy.context.scene.linkable_collections.clear()
        for u_name in unique_names:
            u_objects = []
            for ob in objects:
                # add object to list if another object with the same data is not already in the list
                if u_name == p.match(ob.name).group():
                    if ob.data not in [u.data for u in u_objects]:
                        u_objects.append(ob)
            if len(u_objects) > 1:
                item = bpy.context.scene.linkable_collections.add()
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
        
        self.report({'INFO'}, f"Liniking: '{linkable_collections[index].name}'")
        
        objects = [bpy.data.objects[o.name] for o in list(linkable_collections[index].objects)]

        first_object = objects.pop(0)
        
        for obj in objects:
            # print(f'{first_object.data} -> {obj.data}')
            obj.data = first_object.data
        
        return {'FINISHED'}


##############################################################################
# Add-On Handling
##############################################################################
__classes__ = (
    RefreshLinkableCollection,
    LinkableCollectionItem,
    LinkableCollection_UL_List,
    UIListPanelLinkableCollection,
    LinkCollections,
    LIST_OT_LinkALLCollections,
    LIST_OT_SelectCollection,
    LIST_OT_LinkCollection,
)

def register():
    # register classes
    for c in __classes__:
        bpy.utils.register_class(c)
        print(f'registered {c}')
    
    bpy.types.Scene.linkable_collections = bpy.props.CollectionProperty(type=LinkableCollectionItem)
    # bpy.types.Scene.lin_col_idx = bpy.props.IntProperty(name='Index')
    bpy.types.Scene.lin_col_idx = bpy.props.IntProperty(name='Index', update=ListIndexCallback)


def unregister():
    # unregister classes
    for c in __classes__:
        bpy.utils.unregister_class(c)
        print(f'unregistered {c}')
    del bpy.types.Scene.linkable_collections
    del bpy.types.Scene.lin_col_idx