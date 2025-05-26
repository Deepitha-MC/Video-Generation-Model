import bpy
import os
import math
import random
import mathutils

# --- Configuration ---
OBJECTS_DIR = "/Users/deepithamc/Documents/LLM assignment/Models/fbx_files"
MATERIALS_DIR = "/Users/deepithamc/Documents/LLM assignment/PBR"
ENVIRONMENT_MAP = "/Users/deepithamc/Documents/LLM assignment/rogland_clear_night_4k.exr"
RENDER_OUTPUT_DIR = "/Users/deepithamc/Documents/LLM assignment/renders"

SCENE_COUNT = 10
OBJECTS_MIN = 3
OBJECTS_MAX = 7 
FLOOR_SIZE = 10
SCALE_MIN = 0.5
SCALE_MAX = 1.5

# --- Utility Functions ---

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def add_floor():
    bpy.ops.mesh.primitive_plane_add(size=FLOOR_SIZE, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Floor"
    return floor

def create_material_from_folder(material_folder_path):
    texture_folder = os.path.join(material_folder_path, "textures")

    if not os.path.isdir(texture_folder):
        print(f"No textures found in: {texture_folder}")
        return None

    mat = bpy.data.materials.new(name=os.path.basename(material_folder_path))
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    for node in nodes:
        nodes.remove(node)

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)

    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    links.new(bsdf.outputs[0], output.inputs[0])

    # Updated keywords to match your files: "diff", "rough", "nor"
    tex_map = {
        "diff": ("Base Color", False),
        "albedo": ("Base Color", False),
        "basecolor": ("Base Color", False),
        "color": ("Base Color", False),
        "rough": ("Roughness", False),
        "metallic": ("Metallic", False),
        "nor": ("Normal", True),
        "normal": ("Normal", True),
    }

    added = False

    for file in os.listdir(texture_folder):
        file_path = os.path.join(texture_folder, file)
        file_lower = file.lower()

        if not file_lower.endswith(('.png', '.jpg', '.jpeg', '.exr')):
            continue

        for key, (bsdf_input, is_normal) in tex_map.items():
            if key in file_lower:
                image = bpy.data.images.load(file_path)

                tex_node = nodes.new('ShaderNodeTexImage')
                tex_node.image = image
                tex_node.label = key
                tex_node.location = (-600, -len(nodes) * 200)

                if is_normal:
                    normal_map = nodes.new('ShaderNodeNormalMap')
                    normal_map.location = (-400, tex_node.location.y)
                    links.new(tex_node.outputs[0], normal_map.inputs[0])
                    links.new(normal_map.outputs[0], bsdf.inputs[bsdf_input])
                else:
                    links.new(tex_node.outputs[0], bsdf.inputs[bsdf_input])

                added = True
                break

    return mat if added else None

def get_object_radius(obj):
    bbox = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
    center = obj.location.xy
    max_dist = max((corner.xy - center).length for corner in bbox)
    return max_dist

def normalize_and_place_object(obj, placed_objs):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    # Decide whether to normalize this object
    apply_normalization = random.choice([True, False])

    # Loop to attempt scaling + placement
    for attempt in range(10):
        if apply_normalization:
            # Get original bounding box size
            bbox = [mathutils.Vector(corner) for corner in obj.bound_box]
            size = max(
                max(v[i] for v in bbox) - min(v[i] for v in bbox)
                for i in range(3)
            )
            if size == 0:
                continue

            # Pick random scale, but clamp max size to fit floor
            target_scale = random.uniform(SCALE_MIN, SCALE_MAX)
            max_fit_scale = FLOOR_SIZE / 3  # empirical limit
            target_scale = min(target_scale, max_fit_scale)
            scale_factor = target_scale / size
            obj.scale = (scale_factor, scale_factor, scale_factor)
            bpy.ops.object.transform_apply(scale=True)

        # Update geometry after scaling
        bpy.context.view_layer.update()

        # Drop to floor based on mesh vertices
        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.to_mesh()
        verts_world = [eval_obj.matrix_world @ v.co for v in mesh.vertices]
        min_z = min(v.z for v in verts_world)
        eval_obj.to_mesh_clear()

        obj.location.z -= min_z
        bpy.context.view_layer.update()

        # Try to find a valid position on the plane
        margin = 1.0
        max_pos = FLOOR_SIZE / 2 - margin
        for _ in range(100):
            x = random.uniform(-max_pos, max_pos)
            y = random.uniform(-max_pos, max_pos)
            obj.location.x = x
            obj.location.y = y
            bpy.context.view_layer.update()

            bbox = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
            min_x = min(v.x for v in bbox)
            max_x = max(v.x for v in bbox)
            min_y = min(v.y for v in bbox)
            max_y = max(v.y for v in bbox)

            # Check floor bounds
            if not (-FLOOR_SIZE / 2 <= min_x <= FLOOR_SIZE / 2 and -FLOOR_SIZE / 2 <= max_x <= FLOOR_SIZE / 2 and
                    -FLOOR_SIZE / 2 <= min_y <= FLOOR_SIZE / 2 and -FLOOR_SIZE / 2 <= max_y <= FLOOR_SIZE / 2):
                continue

            # Circle-based overlap check (fast and accurate for floor placement)
            new_radius = get_object_radius(obj)
            center = obj.location.xy

            overlap = False
            for other in placed_objs:
                other_center = other.location.xy
                other_radius = get_object_radius(other)
                if (center - other_center).length < (new_radius + other_radius + 0.3):  # 0.3 = padding
                    overlap = True
                    break

            if not overlap:
                placed_objs.append(obj)
                return

    # If all attempts fail, skip this object
    print(f"⚠️ Could not place {obj.name} without overlap.")
    bpy.data.objects.remove(obj, do_unlink=True)

def import_random_objects(obj_paths, count):
    max_attempts = count * 5  # safety limit
    added = []
    attempted_paths = set()

    while len(added) < count and len(attempted_paths) < max_attempts:
        path = random.choice(obj_paths)
        if path in attempted_paths:
            continue
        attempted_paths.add(path)

        ext = os.path.splitext(path)[1].lower()
        before = set(bpy.context.scene.objects)

        if ext == ".obj":
            bpy.ops.import_scene.obj(filepath=path)
        elif ext == ".fbx":
            bpy.ops.import_scene.fbx(filepath=path)
        else:
            continue

        # Get new mesh objects
        new_objs = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH' and obj not in before]
        if not new_objs:
            continue

        obj = new_objs[0]
        normalize_and_place_object(obj, added)

    if len(added) < count:
        print(f"⚠️ Only placed {len(added)} out of {count} requested objects.")

    return added

def setup_camera():
    cam = bpy.data.objects.get("Camera")
    if not cam:
        bpy.ops.object.camera_add()
        cam = bpy.context.active_object
        cam.name = "Camera"
    bpy.context.scene.camera = cam
    return cam

def randomize_camera(cam):
    angle = random.uniform(0, 2 * math.pi)
    radius = 12  # Increased distance for better coverage
    height = random.uniform(5, 7)  # Slightly elevated view

    cam.location = (
        math.cos(angle) * radius,
        math.sin(angle) * radius,
        height
    )

    direction = mathutils.Vector((0, 0, 1)) - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    # Set camera lens for wider view (in mm)
    cam.data.lens = 24 

def setup_environment(hdri_path):
    # Create a new world if needed
    if not bpy.context.scene.world:
        bpy.context.scene.world = bpy.data.worlds.new("MyWorld")
    world = bpy.context.scene.world

    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links

    for node in nodes:
        nodes.remove(node)

    env_tex = nodes.new("ShaderNodeTexEnvironment")
    env_tex.image = bpy.data.images.load(hdri_path)

    bg = nodes.new("ShaderNodeBackground")
    output = nodes.new("ShaderNodeOutputWorld")

    links.new(env_tex.outputs['Color'], bg.inputs['Color'])
    links.new(bg.outputs['Background'], output.inputs['Surface'])

# --- Execution ---

object_files = [os.path.join(OBJECTS_DIR, f) for f in os.listdir(OBJECTS_DIR) if f.endswith((".obj", ".fbx"))]
material_dirs = [
    os.path.join(MATERIALS_DIR, d)
    for d in os.listdir(MATERIALS_DIR)
    if os.path.isdir(os.path.join(MATERIALS_DIR, d)) and os.path.exists(os.path.join(MATERIALS_DIR, d, "textures"))
]

setup_environment(ENVIRONMENT_MAP)

floor = add_floor()
mat_dir = random.choice(material_dirs)
floor_mat = create_material_from_folder(mat_dir)

if floor_mat:
    floor.data.materials.clear()
    floor.data.materials.append(floor_mat)
else:
    print(f"No valid material found in {mat_dir}")

num_objects = random.randint(OBJECTS_MIN, OBJECTS_MAX)
imported_objs = import_random_objects(object_files, num_objects)

cam = setup_camera()
randomize_camera(cam)

bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
bpy.context.scene.render.filepath = os.path.join(RENDER_OUTPUT_DIR, f"scene_010.png")
bpy.ops.render.render(write_still=True)

## Optional: cleanup at end of scene if needed
#bpy.ops.object.select_all(action='SELECT')
#bpy.ops.object.delete()
