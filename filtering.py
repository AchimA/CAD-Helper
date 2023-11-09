# GPL-3.0 license

import bpy
import re


class FilterSelection(bpy.types.Operator):
    '''
    Filter all the selected objects by:
        - Object Name
        - Object Type
        - Bounding Box Dimensions (diagonaly)
    '''
    bl_idname = 'object.filter_selection'
    bl_label = 'Filter Selection '
    bl_options = {"REGISTER", "UNDO"}

    
    @classmethod
    def poll(cls, context):
        return context.selected_objects

    # update function, which makes sure min is never
    # lager than max and max is never smaller than min
    def update_BB_min_func(self, context):
        if self.prop_BB_max < self.prop_BB_min:
            self.prop_BB_max = self.prop_BB_min

    def update_BB_max_func(self, context):
        if self.prop_BB_min > self.prop_BB_max:
            self.prop_BB_min = self.prop_BB_max

    prop_use_regex: bpy.props.BoolProperty(
        name='Use Regex',
        default=False
        )
    prop_namefilter: bpy.props.StringProperty(
        name='Name Filter',
        default='*',
        options={'TEXTEDIT_UPDATE'}
        )

    prop_BB_min: bpy.props.FloatProperty(
        name='Min Size (%)',
        update=update_BB_min_func,
        default=0,
        soft_min=0,
        soft_max=100
        )
    prop_BB_max: bpy.props.FloatProperty(
        name='Max Size (%)',
        update=update_BB_max_func,
        default=100,
        soft_min=0,
        soft_max=100
        )

    prop_types: bpy.props.EnumProperty(
        name='Include Types:',
        description="My enum description",
        items=[
            # identifier    name       description   number
            ('MESH', "Mesh", "Active Button"),
            ('CURVE', "Curve", "Show a Slider"),
            ('SURFACE', "Surface", "Show a Slider"),
            ('META', "Metaball", "Show a Slider"),
            ('FONT', "Text", "Show a Slider"),
            ('VOLUME', "Volue", "Show a Slider"),
            ('EMPTY', "Empty", "Show a Slider")
            ],
            options = {"ENUM_FLAG"}
    )

    def invoke(self, context, event):
        # set default object types:
        self.prop_types = {
            'MESH',
            'CURVE',
            'SURFACE',
            'META',
            'FONT',
            'VOLUME'
            }
        self.prop_BB_min = 0
        self.prop_BB_max = 100

        return self.execute(context)

    def execute(self, context):
        self.init_selection = bpy.context.selected_objects

        bpy.ops.object.select_all(action='DESELECT')

        # prepair name filtering regex:
        if self.prop_use_regex:
            try:
                pattern = re.compile(self.prop_namefilter)
            except:
                self.report({'INFO'}, 'Regex failed, no matches returned.')
                pattern = re.compile('a^')
        else:
            p_string = self.prop_namefilter
            # match any character 1 or more times
            p_string = p_string.replace('*', '.*')
            # match any character 1 or more times
            p_string = p_string.replace('%', '.*')
            # match single character
            p_string = p_string.replace('?', '.{1}')
            p_string = '(?i)' + p_string
            pattern = re.compile(p_string)

        # do the filtering of the selection here...
        self.biggest_BB_size = max(
            [
                obj.dimensions.length
                for obj
                in self.init_selection
                ]
            )
        [
            obj.select_set(True)
            for
                obj
            in
                self.init_selection
            if
                self.prop_BB_min <= obj.dimensions.length/self.biggest_BB_size*100 <= self.prop_BB_max
            and
                obj.type in self.prop_types
            and
                re.match(pattern, obj.name)
            ]

        self.report(
            {'INFO'},
            '{0} of {1} are currently selected'.format(
                len(bpy.context.selected_objects),
                len(self.init_selection)
                )
            )

        return {'FINISHED'}

    def draw(self, context):

        layout = self.layout
        layout.use_property_split = True

        box = layout.box()
        box.label(text='Filter by Object Name', icon='GREASEPENCIL')
        box.prop(self, 'prop_use_regex')
        box.prop(self, 'prop_namefilter')

        layout.separator(factor=1)

        box = layout.box()
        box.label(text='Filter by Object Type', icon='OBJECT_DATA')
        box.prop(self, "prop_types", toggle=True)

        layout.separator(factor=1)

        box = layout.box()
        box.label(text='Filter by Bounding Box Size', icon='FIXED_SIZE')
        
        row = box.row()
        row.label(text=f'min: {self.prop_BB_min/100*self.biggest_BB_size:.2f}')
        row.separator()
        row.label(text=f'max: {self.prop_BB_max/100*self.biggest_BB_size:.2f}')

        box.prop(self, 'prop_BB_min', slider=True)
        box.prop(self, 'prop_BB_max', slider=True)


class FilterbyVertCount(bpy.types.Operator):
    '''
    Filter all the selected objects by vertex count.
    Works only on mesh type objects!
    '''
    bl_idname = 'object.filter_by_vertex_count'
    bl_label = 'Filter Selection by Vertex Count'
    bl_options = {"REGISTER", "UNDO"}

    
    @classmethod
    def poll(cls, context):
        return context.selected_objects

    # update function, which makes sure min is never
    # lager than max and max is never smaller than min
    
    def update_VT_min_func(self, context):
        if self.prop_VT_max < self.prop_VT_min:
            self.prop_VT_max = self.prop_VT_min

    def update_VT_max_func(self, context):
        if self.prop_VT_min > self.prop_VT_max:
            self.prop_VT_min = self.prop_VT_max

    prop_VT_min: bpy.props.FloatProperty(
        name='Min Count (%)',
        update=update_VT_min_func,
        default=0,
        soft_min=0,
        soft_max=100
        )
    prop_VT_max: bpy.props.FloatProperty(
        name='Max Count (%)',
        update=update_VT_max_func,
        default=100,
        soft_min=0,
        soft_max=100
        )

    def invoke(self, context, event):
        # set default object types:
        self.prop_types = {
            'MESH'
            # 'CURVE',
            # 'SURFACE',
            # 'META',
            # 'FONT',
            # 'VOLUME'
            }
        self.prop_VT_min = 0
        self.prop_VT_max = 100

        return self.execute(context)

    def execute(self, context):
        self.init_selection = [o for o in bpy.context.selected_objects if o.type in self.prop_types]

        bpy.ops.object.select_all(action='DESELECT')

        self.biggest_VT_size = max(
            [
                len(obj.data.vertices)
                for obj
                in self.init_selection
                ]
            )
        [
            obj.select_set(True)
            for
                obj
            in
                self.init_selection
            if
                self.prop_VT_min <= len(obj.data.vertices)/self.biggest_VT_size*100 <= self.prop_VT_max
            ]

        self.report(
            {'INFO'},
            '{0} of {1} are currently selected'.format(
                len(bpy.context.selected_objects),
                len(self.init_selection)
                )
            )

        return {'FINISHED'}

    def draw(self, context):

        layout = self.layout
        layout.use_property_split = True
        # layout.label(text='Filter Selection')

        layout.separator(factor=1)

        box = layout.box()
        box.label(text='Filter by Vertex Count', icon='VERTEXSEL')
        
        row = box.row()
        row.label(text=f'min: {int(self.prop_VT_min/100*self.biggest_VT_size)}')
        row.separator()
        row.label(text=f'max: {int(self.prop_VT_max/100*self.biggest_VT_size)}')

        box.prop(self, 'prop_VT_min', slider=True)
        box.prop(self, 'prop_VT_max', slider=True)

##############################################################################
# Add-On Handling
##############################################################################
__classes__ = (
    FilterSelection,
    FilterbyVertCount,
)


def register():
    # register classes
    for c in __classes__:
        bpy.utils.register_class(c)
        # print(f'registered {c}')


def unregister():
    # unregister classes
    for c in __classes__:
        bpy.utils.unregister_class(c)
        # print(f'unregistered {c}')
