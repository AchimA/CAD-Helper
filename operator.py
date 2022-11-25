import bpy
import mathutils

#####################################################################################
# Operators
#####################################################################################
class SelectAllChildren(bpy.types.Operator):
    '''
    Recursivley expands selection to include all of its children
    '''
    bl_idname = 'object.select_all_children'
    bl_label = 'Select All Children Recusivley'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = __doc__
    
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        # exit function if no parents / roots have been selected
        if len(bpy.context.selected_objects) == 0:
            self.report({'INFO'}, 'No objects were selected. Nothing done...')
            return {'CANCELLED'}
        
        select_hierarchy()
        
        return {'FINISHED'}

class DeleteAndReparentChildren(bpy.types.Operator):
    '''
    Reconnects all the children of an object to it's parent (if available) before deleting the object.
    '''
    bl_idname = 'object.delete_and_reparent_children'
    bl_label = 'Delete and re-parent children'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = __doc__
    
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        # exit function if no parents / roots have been selected
        if len(bpy.context.selected_objects) == 0:
            self.report({'INFO'}, 'No objects were selected. Nothing done...')
            return {'CANCELLED'}

        for object in bpy.context.selected_objects:
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
    Under selected root objects; recursivley deletes all empties that do not have any chlidren parented to it.
    '''
    bl_idname = 'object.delete_child_empties_without_children'
    bl_label = 'Delete child Empies with no children'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = __doc__
        
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        init_selection = bpy.context.selected_objects
        
        # exit function if no parents / roots have been selected
        if len(init_selection) == 0:
            self.report({'INFO'}, 'No objects were selected. Nothing done...')
            return {'CANCELLED'}
        
        select_hierarchy()
        
        sel = bpy.context.selected_objects
        
        # keep only type=empty
        sel = [n for n in sel if n.type == 'EMPTY']
        # keep only leafs (objects without children)
        sel = [n for n in sel if len(n.children)==0]
        
        # iterate through list of leafes
        while sel:
            # extract first object of the list
            obj = sel.pop(0)
            # check if obj has parent of type empy, if True then add that parent to sel list
            if obj.parent.type == 'EMPTY' and not obj.parent in init_selection:
                sel.append(obj.parent)
            # delete obj
            bpy.data.objects.remove(obj)
            #continue as long as some elements are in the list
        
        # restore selection as of before
        bpy.ops.object.select_all(action='DESELECT')
        [obj.select_set(True) for obj in init_selection]

        return {'FINISHED'}

        
class FilterSelectionBySize(bpy.types.Operator):
    '''
    Filter all the selected objects by the size of their bouning box (diagonal).
    '''
    bl_idname = 'object.filter_selection_by_size'
    bl_label = 'Filter Selection by Bounding Box Size'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = __doc__
    
    flag_prop: bpy.props.BoolProperty(name = "Use Int")
    dependent_prop: bpy.props.IntProperty(name = "My Property")


    # update function, which makes sure min is never lager than max and max is never smaller than min
    def update_min_func(self, context):
        if self.prop_max < self.prop_min:
            self.prop_max = self.prop_min
    def update_max_func(self, context):
        if self.prop_min > self.prop_max:
            self.prop_min = self.prop_max
    
    prop_min: bpy.props.FloatProperty(name='Min Size (%)', update=update_min_func, default=0, soft_min=0, soft_max=100, description="%")
    prop_max: bpy.props.FloatProperty(name='Max Size (%)', update=update_max_func, default=100, soft_min=0, soft_max=100)

    # TODO: ersetzen mit EnumProperties? https://blender.stackexchange.com/questions/200879/dynamic-props-dialog-into-operator
    prop_types: bpy.props.EnumProperty(
        name = 'Include Types:',
        description = "My enum description",
        items = [
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


    def execute(self, context):
        self.init_selection = bpy.context.selected_objects
        # exit function if no objects have been selected
        if len(self.init_selection) == 0:
            self.report({'INFO'}, 'No objects were selected. Nothing done...')
            return {'CANCELLED'}
        
        bpy.ops.object.select_all(action='DESELECT')

        # do the filtering of the selection here...
        biggest_size = max([obj.dimensions.length for obj in self.init_selection])
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
            ]
        
        self.report({'INFO'}, '{0} of {1} are currently selected'.format(len(bpy.context.selected_objects), len(self.init_selection)))

        return {'FINISHED'}
    
    def draw(self, context):
        self.layout.use_property_split = True
        col = self.layout.column(heading="Include Types")
        sub = col.column(align=True)
        sub.prop(self, "prop_types", toggle=True)

        row = self.layout.row(heading="Select filter size")
        row = self.layout.row()
        row.prop(self, 'prop_min', slider=True)
        row = self.layout.row()
        row.prop(self, 'prop_max', slider=True)
        
        row = self.layout.row(align=True)

#####################################################################################
# Functions
#####################################################################################

def select_hierarchy():
    # select all the children recursively
    n = len(bpy.context.selected_objects)
    dn = 1
    while dn > 0:
        bpy.ops.object.select_hierarchy(direction='CHILD', extend=True)
        dn = len(bpy.context.selected_objects) - n
        n = len(bpy.context.selected_objects)


#####################################################################################
# Add-On Handling
#####################################################################################
__classes__ = (
    SelectAllChildren,
    DeleteAndReparentChildren,
    DeleteEmpiesWithoutChildren,
    FilterSelectionBySize,
)

def register():
    # register classes
    for c in __classes__:
        bpy.utils.register_class(c)
    
    print('registered ')

def unregister():
    # unregister classes
    for c  in __classes__:
        bpy.utils.unregister_class(c)
    
    print('unregistered ')