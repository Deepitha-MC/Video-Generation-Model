import bpy
import random
import os

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import the Cone fbx file
fbx_filepath = "/Users/deepithamc/Documents/LLM assignment/ReflectiveConeCollars.fbx"
bpy.ops.import_scene.fbx(filepath=fbx_filepath)

# Select all imported objects
for obj in bpy.context.selected_objects:
    obj.scale = (0.5, 0.5, 0.5)  # Adjust scale factor as needed

# Apply the scale transformation
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Add a plane as a ground
#bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))

# Add a camera
bpy.ops.object.camera_add(location=(6.7, -6.4, 5))
camera = bpy.context.object
bpy.context.object.rotation_euler = (1.2, 0, 0.8)
bpy.context.scene.camera = camera  # Set the camera as active

def add_point_light(location, energy=1000, color=(1, 1, 1)):
    bpy.ops.object.light_add(type='POINT', location=location)
    light = bpy.context.object
    light.data.energy = energy
    light.data.color = color
    return light

# Add a single point light
add_point_light(location=(2, 2, 4), energy=1200)

# Add multiple random point lights
for _ in range(3):
    x, y, z = [random.uniform(-3, 3) for _ in range(3)]
    color = (random.random(), random.random(), random.random())
    add_point_light(location=(x, y, z), energy=random.uniform(800, 1500), color=color)
    
    
# Load a random environment map
hdri_folder = "/Users/deepithamc/Downloads/Deep/HDRI"
if os.path.exists(hdri_folder):
     hdri_files = [f for f in os.listdir(hdri_folder) if f.endswith((".hdr", ".exr"))]
     if hdri_files:
         chosen_hdri = random.choice(hdri_files)
         world = bpy.context.scene.world
         world.use_nodes = True
         nodes = world.node_tree.nodes
         links = world.node_tree.links

         # Remove existing background node
         for node in nodes:
             if node.type == 'BACKGROUND':
                 nodes.remove(node)

         # Add an environment texture node
         env_texture = nodes.new(type="ShaderNodeTexEnvironment")
         env_texture.image = bpy.data.images.load(os.path.join(hdri_folder, chosen_hdri))

         background = nodes.new(type="ShaderNodeBackground")
         output = nodes.get("World Output")

         links.new(env_texture.outputs["Color"], background.inputs["Color"])
         links.new(background.outputs["Background"], output.inputs["Surface"])
        
# Set render engine to Cycles for realistic lighting
bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'

print("Scene setup complete with random lighting and HDRI!")

# Set output render properties
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.filepath = "/Users/deepithamc/Documents/LLM assignment/render_output(2).png"

# Render the scene
bpy.ops.render.render(write_still=True)

print("Rendering complete! The image is saved as 'render_output.png' in the current Blender project directory.")