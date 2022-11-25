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
        
        # select all the children recursively
        # n = len(bpy.context.selected_objects)
        # dn = 1
        # while dn > 0:
        #     bpy.ops.object.select_hierarchy(direction='CHILD', extend=True)
        #     dn = len(bpy.context.selected_objects) - n
        #     n = len(bpy.context.selected_objects)
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
        
    # @classmethod
    # def poll(cls, context):
    #     return context.active_object is not None
    
    # def execute(self, context):
    #     # exit function if no objects have been selected
    #     if len(bpy.context.selected_objects) == 0:
    #         self.report({'INFO'}, 'No objects were selected. Nothing done...')
    #         return {'CANCELLED'}
        
    #     print([[obj.type, obj.name, obj.dimensions.length] for obj in bpy.context.selected_objects])
        
    #     return {'FINISHED'}

    dynamic_min = bpy.props.IntProperty(
        name='dynamic_min',
        default=0
    )
    dynamic_max = bpy.props.IntProperty(
        name='dynamic_max',
        default=1
    )
    
    flag_prop: bpy.props.BoolProperty(name = "Use Int")
    dependent_prop: bpy.props.IntProperty(name = "My Property")

    prop_mesh: bpy.props.BoolProperty(name='Mesh', default=True)
    prop_curve: bpy.props.BoolProperty(name='Curve', default=True)
    prop_text: bpy.props.BoolProperty(name='Text', default=True)
    prop_empty: bpy.props.BoolProperty(name='Empty', default=False)

    prop_min: bpy.props.FloatProperty(name='min size', default=0, soft_min=0, soft_max=10)
    prop_max: bpy.props.FloatProperty(name='max size', default=5, soft_min=0, soft_max=10)

    def execute(self, context):
        init_selection = bpy.context.selected_objects
        
        dynamic_min = min([obj.dimensions.length for obj in init_selection])
        dynamic_max = max([obj.dimensions.length for obj in init_selection])
        # self.prop_min.soft_min = self.min
        print(dynamic_min)

        # exit function if no objects have been selected
        if len(bpy.context.selected_objects) == 0:
            self.report({'INFO'}, 'No objects were selected. Nothing done...')
            return {'CANCELLED'}
        
        bpy.ops.object.select_all(action='DESELECT')
        [obj.select_set(True) for obj in init_selection if self.prop_min < obj.dimensions.length < self.prop_max]

        return {'FINISHED'}
    
    def draw(self, context):
        self.layout.use_property_split = True

        # row = self.layout.row()
        # row.prop(self, "flag_prop")
        
        # sub = row.row()
        # sub.enabled = self.flag_prop
        # sub.prop(self, "dependent_prop", text="")

        row = self.layout.row(heading="Select filter size")
        row = self.layout.row()
        row.prop(self, 'prop_min', slider=True)
        row = self.layout.row()
        row.prop(self, 'prop_max', slider=True)

        row = self.layout.row(heading="Include Types")
        sub = row.row(align=True)
        sub.prop(self, "prop_mesh", toggle=True)
        sub.prop(self, "prop_curve", toggle=True)
        sub.prop(self, "prop_text", toggle=True)
        sub.prop(self, "prop_empty", toggle=True)
        
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