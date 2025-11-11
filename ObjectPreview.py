import bpy
import tempfile


# Assign linkable collection.
class ObjectRenderInfo(bpy.types.PropertyGroup):
    obj_name: bpy.props.StringProperty(name='Object Name', default='Unknown')
    projection_type: bpy.props.StringProperty(name='Projection Type', default='isometric')

def render_isometric_image(object, position):
  """
  Renders an isometric image of the given object.

  Args:
    object: The object to render.
    position: The position of the camera, one of 'isometric', 'dimeric', or 'trimetric'.

  Returns:
    The filepath of the rendered image.
  """

  # Create a temporary scene with transparent background
  scene = bpy.data.scenes.new("TempScene")
  scene.render.alpha_mode = "TRANSPARENT"

  # Add world lightning to the scene
  bpy.ops.wm.create_empty(type="WORLD")

  # Add the object to the scene
  bpy.context.scene.objects.link(object)

  # Add an orthographic camera to the scene
  camera = bpy.data.cameras.new("TempCamera")
  camera.orthogonal_projection_type = "ORTHOGRAPHIC"
  scene.objects.link(camera)

  # Place the camera in the desired position
  if position == "isometric":
    camera.rotation_euler = (60, 0, 45)
  elif position == "dimeric":
    camera.rotation_euler = (60, 30, 45)
  elif position == "trimetric":
    camera.rotation_euler = (60, 60, 45)

  # Place the object so that it is in full frame of the camera view
  bpy.ops.view3d.view_selected()

  # Render the image to the temp folder
  with tempfile.NamedTemporaryFile(suffix=".png") as temp_file:
    filepath = temp_file.name
    bpy.ops.render.render(filepath=filepath)

  return filepath


##############################################################################
# Add-On Handling
##############################################################################
classes = (
    ObjectRenderInfo,
)

def register():
    # register classes
    for c in classes:
        bpy.utils.register_class(c)
        print(f'registered {c}')

    bpy.types.Property.render_info = bpy.props.CollectionProperty(type=ObjectRenderInfo)


def unregister():
    # unregister classes
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
        print(f'unregistered {c}')
        
    del bpy.types.Property.render_info
