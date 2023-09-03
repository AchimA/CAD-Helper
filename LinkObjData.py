# GPL-3.0 license

import bpy
import re
from . import shared_functions
import tempfile
import os

linkable_objects = {}


class RefreshLinkableCollection(bpy.types.Operator):
    '''
    Links object data of objects with the same name.

    I.e. if a selection contains ['bolt_M3, bolt_M3.001, bolt_M3.002, nut_M3, nut_M3.001] then;
        - [bolt_M3, bolt_M3.001, bolt_M3.002] will be lined
        and:
        - [nut_M3, nut_M3.001] will be linked
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
            match = p.match(ob.name)
            match = match.group()
            if match not in unique_names:
                unique_names.append(match)
        
        global linkable_objects
        linkable_objects = {}

        for u_name in unique_names:
            u_objects = []
            for ob in objects:
                # print(ob.data)
                if u_name in ob.name and ob.data not in u_objects:
                    u_objects.append(ob)
            if len(u_objects) > 1:
                linkable_objects[u_name] = u_objects
        # bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}



class LinkObjData(bpy.types.Operator):
    '''
    Links object data of objects with the same name.

    I.e. if a selection contains ['bolt_M3, bolt_M3.001, bolt_M3.002, nut_M3, nut_M3.001] then;
        - [bolt_M3, bolt_M3.001, bolt_M3.002] will be lined
        and:
        - [nut_M3, nut_M3.001] will be linked
    '''
    bl_idname = 'object.link_obj_data'
    bl_label = 'Link Object Data'
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def invoke(self, context, event):
        bpy.ops.object.refresh_linkable_collection()
        return self.execute(context)

    def execute(self, context):
        
        return {'FINISHED'}
    

    def draw(self, context):
        
        layout = self.layout
        # layout.use_property_split = True
        layout.label(text='Linkable collections:')
        layout.operator(
            'object.refresh_linkable_collection',
            text=f'Refresh collections!',
            icon='FILE_REFRESH'
            )
        layout.operator(
            'object.link_all_collections',
            text=f'Link all {len(linkable_objects)} collections!',
            icon='LINKED'
            )
        # layout.operator('object.update_linkable_collection', text='Refresh', icon='FILE_REFRESH')
        for key, data in linkable_objects.items():
            box = layout.box()
            row_outer = box.row()
            # box = row_outer.box()
            # box.label(text='', icon='SNAP_FACE')
            # icon_id = render_object_thumbnail(obj)
            # row_outer.template_icon(icon_value=icon_id, scale=3.0)

            box = row_outer.box()
            box.label(text=f'[{len(data)}x] {key}', icon='OBJECT_DATA')

            row = box.row()
            row.operator(SelectCollections.bl_idname, text='Select', icon='RESTRICT_SELECT_OFF').collection_name = key
            row.operator(LinkCollections.bl_idname, text='Link', icon='LINKED').collection_name = key
            # row.label(text='Link Object Data', icon='LINKED')


class SelectCollections(bpy.types.Operator):
    bl_idname = "object.select_collections"
    bl_label = "Select Collections"

    collection_name: bpy.props.StringProperty()

    def execute(self, context):
        self.report({'INFO'}, f'Not yet implemented (sorry)')
        # self.report({'INFO'}, f"Collection is '{self.collection_name}'")
        # print(linkable_objects[self.collection_name])
        
        # bpy.ops.object.select_all(action='DESELECT')
        # bpy.context.view_layer.objects.active = None
        # for obj in linkable_objects[self.collection_name]:
        #     print(obj)
        #     obj.select_set(True)
        #     bpy.context.view_layer.objects.active = obj
        return {'FINISHED'}

class LinkCollections(bpy.types.Operator):
    bl_idname = "object.link_collections"
    bl_label = "Link Collections"

    collection_name: bpy.props.StringProperty()

    def execute(self, context):
        self.report({'INFO'}, f"Liniking: '{self.collection_name}'")

        objects = linkable_objects[self.collection_name]
        print(objects)

        first_object = objects.pop(0)
        
        for obj in objects:
            print(f'{first_object.data} -> {obj.data}')
            obj.data = first_object.data
        # remove from dict
        linkable_objects.pop(self.collection_name, None)
        return {'FINISHED'}

class LinkALLCollections(bpy.types.Operator):
    bl_idname = "object.link_all_collections"
    bl_label = "Link All Collections"

    def execute(self, context):
        self.report({'INFO'}, "Liniking all collections'")
        max_loops = 1e3
        loop = 0
        while linkable_objects and loop<max_loops:
            key = list(linkable_objects.keys())[0]
            print(key)
            bpy.ops.object.link_collections(collection_name=key)
            loop += 1
            # object.link_collections().collection_name = key
    #     objects = linkable_objects[self.collection_name]
        # print(objects)

    #     first_object = objects.pop(0)
        
    #     for obj in objects:
    #         print(f'{first_object.data} -> {obj.data}')
    #         obj.data = first_object.data
    #     # remove from dict
    #     linkable_objects.pop(self.collection_name, None)
        return {'FINISHED'}

##############################################################################
# Add-On Handling
##############################################################################
__classes__ = (
    LinkObjData,
    RefreshLinkableCollection,
    SelectCollections,
    LinkCollections,
    LinkALLCollections,
)

def register():
    # register classes
    for c in __classes__:
        bpy.utils.register_class(c)
        print(f'registered {c}')


def unregister():
    # unregister classes
    for c in __classes__:
        bpy.utils.unregister_class(c)
        print(f'unregistered {c}')