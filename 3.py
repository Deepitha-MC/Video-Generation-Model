import bpy
import random
import math
from mathutils import Vector

bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'

# Set output render properties
bpy.context.scene.render.image_settings.file_format = 'PNG'

def connect_base_color():
    random_camera_around_object()
    # Get the active object and material
    obj = bpy.context.active_object
    if not obj or not obj.active_material:
        raise Exception("No active object or material selected!")
    
    material = obj.active_material
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # Find critical nodes
    principled_node = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
    material_output = nodes.get("Material Output")

    if not principled_node or not material_output:
        raise Exception("Missing Principled BSDF or Material Output node!")

    # Disconnect existing connections to Material Output's Surface
    if material_output.inputs['Surface'].is_linked:
        links.remove(material_output.inputs['Surface'].links[0])

    # Create Emission shader to visualize Base Color
    emission_node = nodes.new(type='ShaderNodeEmission')
    emission_node.location = (principled_node.location.x + 300, principled_node.location.y)

    # Connect Base Color to Emission
    if principled_node.inputs['Base Color'].is_linked:
        # Use existing Base Color connection
        base_color_source = principled_node.inputs['Base Color'].links[0].from_socket
    else:
        # Create RGB node with static Base Color value
        base_color = principled_node.inputs['Base Color'].default_value
        rgb_node = nodes.new(type='ShaderNodeRGB')
        rgb_node.outputs[0].default_value = base_color
        base_color_source = rgb_node.outputs[0]

    links.new(base_color_source, emission_node.inputs['Color'])
    links.new(emission_node.outputs['Emission'], material_output.inputs['Surface'])
    
    bpy.context.scene.render.filepath = "/Users/deepithamc/Documents/LLM assignment/base_color.png"
    bpy.ops.render.render(write_still=True)
    
def connect_metallicity():
    random_camera_around_object()
    # Get active object and material
    obj = bpy.context.active_object
    if not obj or not obj.active_material:
        raise Exception("No active object or material selected!")
    
    material = obj.active_material
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # Find critical nodes
    principled_node = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
    material_output = nodes.get("Material Output")

    if not principled_node or not material_output:
        raise Exception("Missing Principled BSDF or Material Output node!")

    # Disconnect existing Material Output connections
    if material_output.inputs['Surface'].is_linked:
        links.remove(material_output.inputs['Surface'].links[0])

    # Create Emission shader for visualization
    emission_node = nodes.new(type='ShaderNodeEmission')
    emission_node.location = (principled_node.location.x + 400, principled_node.location.y)
    emission_node.inputs['Color'].default_value = (1, 1, 1, 1)  # White emission color

    # Get metallic input source
    metallic_input = principled_node.inputs['Metallic']
    
    if metallic_input.is_linked:
        # Use existing metallic connection (texture/value node)
        metallic_source = metallic_input.links[0].from_socket
    else:
        # Use static metallic value
        metallic_value = metallic_input.default_value
        value_node = nodes.new(type='ShaderNodeValue')
        value_node.outputs[0].default_value = metallic_value
        metallic_source = value_node.outputs[0]

    # Connect metallicity to emission strength
    links.new(metallic_source, emission_node.inputs['Strength'])
    links.new(emission_node.outputs['Emission'], material_output.inputs['Surface'])
    
    bpy.context.scene.render.filepath = "/Users/deepithamc/Documents/LLM assignment/metallicity.png"
    bpy.ops.render.render(write_still=True)
    
def connect_roughness():
    random_camera_around_object()
    # Get active object and material
    obj = bpy.context.active_object
    if not obj or not obj.active_material:
        raise Exception("No active object or material selected!")
    
    material = obj.active_material
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # Find critical nodes
    principled_node = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
    material_output = nodes.get("Material Output")

    if not principled_node or not material_output:
        raise Exception("Missing Principled BSDF or Material Output node!")

    # Disconnect existing Material Output connections
    if material_output.inputs['Surface'].is_linked:
        links.remove(material_output.inputs['Surface'].links[0])

    # Create Emission shader for visualization
    emission_node = nodes.new(type='ShaderNodeEmission')
    emission_node.location = (principled_node.location.x + 400, principled_node.location.y)
    emission_node.inputs['Color'].default_value = (1, 1, 1, 1)  # White emission color

    # Get roughness input source
    roughness_input = principled_node.inputs['Roughness']
    
    if roughness_input.is_linked:
        # Use existing roughness connection (texture/value node)
        roughness_source = roughness_input.links[0].from_socket
    else:
        # Use static roughness value
        roughness_value = roughness_input.default_value
        value_node = nodes.new(type='ShaderNodeValue')
        value_node.outputs[0].default_value = roughness_value
        roughness_source = value_node.outputs[0]

    # Connect roughness to emission strength
    links.new(roughness_source, emission_node.inputs['Strength'])
    links.new(emission_node.outputs['Emission'], material_output.inputs['Surface'])
    
    bpy.context.scene.render.filepath = "/Users/deepithamc/Documents/LLM assignment/rough_ness.png"
    bpy.ops.render.render(write_still=True)
    
    
def connect_normal_map():
    random_camera_around_object()
    # Get active object and material
    obj = bpy.context.active_object
    if not obj or not obj.active_material:
        raise Exception("No active object or material selected!")
    
    material = obj.active_material
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # Find critical nodes
    principled_node = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
    material_output = nodes.get("Material Output")
    normal_map_node = next((n for n in nodes if n.type == "NORMAL_MAP"), None)

    if not principled_node or not material_output:
        raise Exception("Missing Principled BSDF or Material Output node!")

    # Disconnect existing Material Output connections
    if material_output.inputs['Surface'].is_linked:
        links.remove(material_output.inputs['Surface'].links[0])

    # Create Emission shader for visualization
    emission_node = nodes.new(type='ShaderNodeEmission')
    emission_node.location = (principled_node.location.x + 400, principled_node.location.y)

    # Get normal data source
    if principled_node.inputs['Normal'].is_linked:
        # Use existing normal connection
        normal_source = principled_node.inputs['Normal'].links[0].from_socket
    else:
        # Create default normal (if no existing normal map)
        normal_map_node = nodes.new(type='ShaderNodeNormalMap')
        normal_source = normal_map_node.outputs['Normal']

    # Convert normal vectors (range [-1,1] to [0,1] for visualization)
    add_node = nodes.new(type='ShaderNodeVectorMath')
    add_node.operation = 'ADD'
    add_node.inputs[1].default_value = (1, 1, 1)

    multiply_node = nodes.new(type='ShaderNodeVectorMath')
    multiply_node.operation = 'MULTIPLY'
    multiply_node.inputs[1].default_value = (0.5, 0.5, 0.5)

    # Link nodes
    links.new(normal_source, add_node.inputs[0])
    links.new(add_node.outputs[0], multiply_node.inputs[0])
    links.new(multiply_node.outputs[0], emission_node.inputs['Color'])
    links.new(emission_node.outputs['Emission'], material_output.inputs['Surface'])
    
    bpy.context.scene.render.filepath = "/Users/deepithamc/Documents/LLM assignment/normal_map.png"
    bpy.ops.render.render(write_still=True)
    
def random_camera_around_object(target_object=None, min_radius=3, max_radius=8):
    # Get or create camera
    cam = bpy.data.objects.get("Camera")
    if not cam:
        bpy.ops.object.camera_add()
        cam = bpy.context.object
        cam.name = "Camera"
    
    # Use active object if no target specified
    if not target_object:
        target_object = bpy.context.active_object
    
    if not target_object:
        raise Exception("No target object selected!")
    
    # Get target location
    target_location = target_object.location
    
    # Generate random spherical coordinates
    radius = random.uniform(min_radius, max_radius)
    theta = random.uniform(0, 2 * math.pi)  # Horizontal angle
    phi = random.uniform(math.pi/6, math.pi/2)  # Vertical angle (avoid top/bottom views)
    
    # Calculate camera position
    x = radius * math.sin(phi) * math.cos(theta)
    y = radius * math.sin(phi) * math.sin(theta)
    z = radius * math.cos(phi)
    cam.location = target_location + Vector((x, y, z))
    
    # Point camera at target
    direction = target_location - cam.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()

# List of render passes to generate
passes = ["Base Color", "Metallic", "Roughness", "Normal"]

for p in passes:
    # Enable the appropriate pass for this render
    if p == "Base Color":
        connect_base_color()
    elif p == "Metallic":
        connect_metallicity()
    elif p == "Normal":
        connect_normal_map()
    elif p == "Roughness":
        connect_roughness()