import bpy
import mathutils
import re
import fnmatch


#####################################################################################
# Operators
#####################################################################################

class SelectParentsExtend(bpy.types.Operator):
    '''
    Extends the selection to the parent of all the selected objects
    '''
    bl_idname = 'object.extend_selection_to_parents'
    bl_label = 'Extend Selection to Parents'
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
    def execute(self, context):
        bpy.ops.object.select_hierarchy(direction='PARENT', extend=True)
        return {'FINISHED'}

class SelectParent(bpy.types.Operator):
    '''
    Selects the immidiate parent of all the selected objects
    '''
    bl_idname = 'object.select_parent'
    bl_label = 'Select Parent'
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
    def execute(self, context):
        bpy.ops.object.select_hierarchy(direction='PARENT', extend=False)
        return {'FINISHED'}

class SelectChildren(bpy.types.Operator):
    '''
    Selects the immidiate child of all the selected objects
    '''
    bl_idname = 'object.select_children'
    bl_label = 'Select Children'
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
    def execute(self, context):
        bpy.ops.object.select_hierarchy(direction='CHILD', extend=False)
        return {'FINISHED'}

class SelectChildrenExtend(bpy.types.Operator):
    '''
    Extends the selection to the child of all the selected objects
    '''
    bl_idname = 'object.extend_selection_to_children'
    bl_label = 'Extend Selection to Children'
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
    def execute(self, context):
        bpy.ops.object.select_hierarchy(direction='CHILD', extend=True)
        return {'FINISHED'}

class SelectAllChildren(bpy.types.Operator):
    '''
    Recursivley expands selection to include all the children of an initial selection.
    '''
    bl_idname = 'object.select_all_children'
    bl_label = 'Select All Children Recusivley'
    bl_options = {"REGISTER", "UNDO"}
    
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
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
    This allows to keep the hierarchy when deleting objects from a structured assebly.

    TODO:
    - Unexpected behaviour when deleting the root object with this operator
    '''
    bl_idname = 'object.delete_and_reparent_children'
    bl_label = 'Delete and re-parent children'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = __doc__
    
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
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
    Under selected root objects; recursivley deletes all empties that do not have any chlidren.
    '''
    bl_idname = 'object.delete_child_empties_without_children'
    bl_label = 'Delete child Empies with no children'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = __doc__
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
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

def select_hierarchy():
    # select all the children recursively
    n = len(bpy.context.selected_objects)
    dn = 1
    while dn > 0:
        bpy.ops.object.select_hierarchy(direction='CHILD', extend=True)
        dn = len(bpy.context.selected_objects) - n
        n = len(bpy.context.selected_objects)
        
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
    bl_description = __doc__
    
    # update function, which makes sure min is never lager than max and max is never smaller than min
    def update_min_func(self, context):
        if self.prop_max < self.prop_min:
            self.prop_max = self.prop_min
    def update_max_func(self, context):
        if self.prop_min > self.prop_max:
            self.prop_min = self.prop_max
    
    prop_use_regex: bpy.props.BoolProperty(name='Use Regex', default=False)
    prop_namefilter: bpy.props.StringProperty(name='Name Filter', default='*')

    prop_min: bpy.props.FloatProperty(name='Min Size (%)', update=update_min_func, default=0, soft_min=0, soft_max=100)
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
    
    
    # def __init__(self):
    #     pass
    

    def invoke(self, context, event):
        #set default object types:
        self.prop_types={'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'VOLUME'}
        
        return self.execute(context)

    def execute(self, context):
        self.init_selection = bpy.context.selected_objects
        # exit function if no objects have been selected
        if len(self.init_selection) == 0:
            self.report({'INFO'}, 'No objects were selected. Nothing done...')
            return {'CANCELLED'}
        
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
            p_string = p_string.replace('*', '.*') # match any character 1 or more times
            p_string = p_string.replace('%', '.*') # match any character 1 or more times
            p_string = p_string.replace('?', '.{1}') # match single character
            p_string = '(?i)' + p_string
            pattern = re.compile(p_string)

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
            and
            re.match(pattern, obj.name)
            ]
        
        self.report({'INFO'}, '{0} of {1} are currently selected'.format(len(bpy.context.selected_objects), len(self.init_selection)))

        return {'FINISHED'}
    
    def draw(self, context):

        layout = self.layout
        layout.use_property_split = True
        layout.label(text='Filter Selection')
        
        
        box = layout.box()
        row = box.row()
        row.label(text='Filter by Object Name', icon='GREASEPENCIL')
        row.prop(self, 'prop_use_regex')
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


class Transfer_VP_to_Nodes(bpy.types.Operator):
    """Transfer: Viewport Display -> Material Nodes"""
    bl_idname = "object.transfer_vp_to_nodes"
    bl_label = "Transfer: Viewport Display -> Material Nodes"

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        material_list = get_material_list(context)
        ok = 0
        err = 0
        for mat in material_list:
            try:
                self.report({'INFO'}, 'Processing:\t{}'.format(mat.name))
                mat.node_tree.nodes['Principled BSDF'].inputs[0].default_value = mat.diffuse_color
                mat.node_tree.nodes['Principled BSDF'].inputs[6].default_value = mat.metallic
                mat.node_tree.nodes['Principled BSDF'].inputs[9].default_value = mat.roughness
                ok += 1
            except:
                # Errror Handling, falls etwas schief läuft....
                self.report({'INFO'}, 'WARNING!:\tThere has been an error processing \'{}\''.format(mat.name))
                err += 1
        self.report({'INFO'}, 'Processing Matterial ({} OK, {} errors)'.format(ok, err))

        return {'FINISHED'}

class Transfer_Nodes_to_VP(bpy.types.Operator):
    """Transfer: Material Nodes -> Viewport Display"""
    bl_idname = "object.transfer_nodes_to_vp"
    bl_label = "Transfer: Material Nodes -> Viewport Display"

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):
        material_list = get_material_list(context)
        ok = 0
        err = 0
        for mat in material_list:
            try:
                self.report({'INFO'}, 'Processing:\t{}'.format(mat.name))
                mat.diffuse_color = mat.node_tree.nodes['Principled BSDF'].inputs[0].default_value
                mat.metallic = mat.node_tree.nodes['Principled BSDF'].inputs[6].default_value
                mat.roughness = mat.node_tree.nodes['Principled BSDF'].inputs[9].default_value
                ok += 1
            except:
                # Errror Handling, falls etwas schief läuft....
                self.report({'INFO'}, 'WARNING!:\tThere has been an error processing \'{}\''.format(mat.name))
                err += 1
        self.report({'INFO'}, 'Processing Matterial ({} OK, {} errors)'.format(ok, err))

        return {'FINISHED'}


def get_material_list(context):
    material_list = []
    for obj in context.selected_objects:
        for mat in obj.material_slots:
            if mat.material != None and mat.material not in material_list:
                material_list.append(mat.material)
    return material_list



#####################################################################################
# Add-On Handling
#####################################################################################
__classes__ = (
    SelectAllChildren,
    SelectParentsExtend,
    SelectParent,
    SelectChildren,
    SelectChildrenExtend,
    DeleteAndReparentChildren,
    DeleteEmpiesWithoutChildren,
    FilterSelection,
    Transfer_VP_to_Nodes,
    Transfer_Nodes_to_VP,
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