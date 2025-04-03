import bpy
import random

# Clear existing objects (optional)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

fbx_filepath = "/Users/deepithamc/Documents/LLM assignment/ReflectiveConeCollars.fbx"
bpy.ops.import_scene.fbx(filepath=fbx_filepath)

# Select all imported objects
for obj in bpy.context.selected_objects:
    obj.scale = (0.5, 0.5, 0.5)  # Adjust scale factor as needed

# Apply the scale transformation
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Add a camera
bpy.ops.object.camera_add(location=(6.7, -6.4, 5))
camera = bpy.context.object
bpy.context.object.rotation_euler = (1.2, 0, 0.8)
bpy.context.scene.camera = camera  # Set the camera as active

# Create a new Plane (Floor)
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
floor = bpy.context.object
floor.name = "Floor"

# Enable shadow reception
floor.cycles.is_shadow_catcher = True  # For Cycles Render
bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'

# Add a Random Light
x, y, z = random.uniform(-5, 5), random.uniform(-5, 5), random.uniform(3, 10)
bpy.ops.object.light_add(type='SUN', location=(x, y, z))
light = bpy.context.object
bpy.context.object.rotation_euler = (-1.2, 0, -0.8)
light.data.energy = random.uniform(5, 15)  # Random light intensity

# Ensure shadow casting
light.data.use_shadow = True
light.data.shadow_soft_size = 0.5  # Soft shadow effect

# Render settings
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.filepath = "/Users/deepithamc/Documents/LLM assignment/render_output(4).png"

# Render the scene
bpy.ops.render.render(write_still=True)

print(f"Light added at: {x}, {y}, {z}")
