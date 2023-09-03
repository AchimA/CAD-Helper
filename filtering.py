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
    def update_min_func(self, context):
        if self.prop_max < self.prop_min:
            self.prop_max = self.prop_min

    def update_max_func(self, context):
        if self.prop_min > self.prop_max:
            self.prop_min = self.prop_max

    prop_use_regex: bpy.props.BoolProperty(
        name='Use Regex',
        default=False
        )
    prop_namefilter: bpy.props.StringProperty(
        name='Name Filter',
        default='*',
        options={'TEXTEDIT_UPDATE'}
        )

    prop_min: bpy.props.FloatProperty(
        name='Min Size (%)',
        update=update_min_func,
        default=0,
        soft_min=0,
        soft_max=100
        )
    prop_max: bpy.props.FloatProperty(
        name='Max Size (%)',
        update=update_max_func,
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
        biggest_size = max(
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
            self.prop_min <= obj.dimensions.length/biggest_size*100 <= self.prop_max
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
        layout.label(text='Filter Selection')

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
        box.label(text='Filter by Size', icon='FIXED_SIZE')
        box.prop(self, 'prop_min', slider=True)
        box.prop(self, 'prop_max', slider=True)


##############################################################################
# Add-On Handling
##############################################################################
__classes__ = (
    FilterSelection,
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
