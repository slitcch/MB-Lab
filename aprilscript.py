#import os
#print("PYTHONPATH:", os.environ.get('PYTHONPATH'))
#print("PATH:", os.environ.get('PATH'))


import pandas as pd
import numpy as np
import bpy
import mathutils
import math
import bpy_extras
import os
import random
import csv

C = bpy.context
D = bpy.data


class State:
    collection = None
    def __init__(self):
        self.collection = bpy.data.collections['Collection']
        self.frame = 0
        self.guy = D.objects["guy.002"]


def simple_rotation(vector_from, vector_to):
    axis = vector_from.cross(vector_to).normalized()
    angle = math.acos(vector_from.dot(vector_to))
    
    return mathutils.Quaternion(axis, angle)

def matrix_from_array(inp):
    m = mathutils.Matrix()
    acc_idx = 0
    for row in range(3):
        for col in range(4):
#            print(inp[acc_idx])
            m[row][col] = inp[acc_idx]
            acc_idx+=1
    return m

def mat_to_guy(st, inp):
#    m = mathutils.Matrix()
#    C.object.location.x = inp[0]
#    C.object.location.y = inp[1]
#    C.object.location.z = inp[2]
#    
#    C.object.rotation_quaternion.x = inp[3]
#    C.object.rotation_quaternion.y = inp[4]
#    C.object.rotation_quaternion.z = inp[5]
#    C.object.rotation_quaternion.w = inp[6]

#    x = inp[3]
#    y = inp[7]
#    z = inp[11]

#    acc_idx = 0
#    for row in range(3):
#        for col in range(4):
#            C.object.matrix_world[row][col] = inp[acc_idx]
#            acc_idx+=1
#    C.view_layer.update()
    C.object.location = inp.to_translation()
    C.object.rotation_quaternion = inp.to_quaternion()
    C.object.keyframe_insert(data_path="location", frame=st.frame)
    C.object.keyframe_insert(data_path="rotation_quaternion", frame=st.frame)
    
#    st.frame += 1
#    C.object.data.matrix_world
#    emp = bpy.data.objects.new(name, None)
#    emp.location.x = x
#    emp.location.y = -z
#    emp.location.z = y
#    emp.empty_display_size = 0.01
#    
#    st.collection.objects.link(emp)

def mat_to_bone(st, inp, name):
    bone = C.object.pose.bones[name]
    

    
    print(bone.bone.matrix_local)
    print(bone.bone.matrix_local.inverted())

    the = inp @ bone.bone.matrix_local.inverted()
    


    

#    print(bone.bone.matrix_local.inverted() @ inp)
##    print(inp * bone.bone.matrix_local.inverted())
#    
#    the = inp @ bone.bone.matrix_local.inverted()
#    raise
#    the = inp
    print(the.to_translation())
    print(bone.bone.matrix_local.to_translation())
    
    trans = the.to_translation()
    trans.y = the.to_translation().z
    trans.z = -the.to_translation().y
    
    bone.location = trans - bone.bone.matrix_local.to_translation()
    bone.location = inp.to_translation()
    print(bone.location)
#    bone.location = (0,0,0)
    bone.rotation_quaternion = inp.to_quaternion()
    print(bone.rotation_quaternion)
    bone.keyframe_insert(data_path="location", frame=st.frame)
    bone.keyframe_insert(data_path="rotation_quaternion", frame=st.frame)
#    raise
    return

def set_pose(obj, inp):
    
#    mathutils.Quaternion() q

    obj.location.x = inp[0]
    obj.location.y = inp[1]
    obj.location.z = inp[2]
    
    obj.rotation_quaternion.x = inp[3]
    obj.rotation_quaternion.y = inp[4]
    obj.rotation_quaternion.z = inp[5]
    obj.rotation_quaternion.w = inp[6]

    obj.keyframe_insert(data_path="location", frame=st.frame)
    obj.keyframe_insert(data_path="rotation_quaternion", frame=st.frame)

def set_pose(obj, mat, inp):
    
    q_extra = mathutils.Euler((-(math.pi/2), 0, 0)).to_quaternion()
    

    v = mathutils.Vector()    
    q = mathutils.Quaternion() 

    v.x = inp[0]
    v.y = inp[1]
    v.z = inp[2]
    
    q.x = inp[3]
    q.y = inp[4]
    q.z = inp[5]
    q.w = inp[6]
    
    m_new = mathutils.Matrix()
    m_new = m_new.LocRotScale(v, q, None)
    
#    print("it's", m_new)
#    print(v, q)
#    raise
    m_new = mat @ m_new;
    
    v = m_new.to_translation()
    q = m_new.to_quaternion()
    
    q = q @ q_extra
    
    obj.location = v;
    obj.rotation_quaternion = q;    
    
    
    obj.keyframe_insert(data_path="location", frame=st.frame)
    obj.keyframe_insert(data_path="rotation_quaternion", frame=st.frame)

    return m_new


def create_empty(name, collection, size):
    empty = bpy.data.objects.new(name, None)  # Create new empty object
    collection.objects.link(empty)  # Link empty to the current object's collection
    empty.empty_display_type = 'ARROWS'
    empty.rotation_mode = 'QUATERNION'
    empty.empty_display_size = size;
    return empty

def create_camera(name, collection):
    cam = bpy.data.cameras.new(name)  # Create new empty object
    empty = bpy.data.objects.new(name, cam)
    collection.objects.link(empty)  # Link empty to the current object's collection
    empty.rotation_mode = 'QUATERNION'
    return empty



def do_side(st, the_array, side_name):
    shoulder_l = matrix_from_array(the_array[2:2+12])

    elb_l = matrix_from_array(the_array[15:15+12])
    wrist_l = matrix_from_array(the_array[28:28+12]) 
    
    mat_to_bone(st, shoulder_l, f"J_Bip_{side_name}_UpperArm")
    mat_to_bone(st, elb_l, f"J_Bip_{side_name}_LowerArm")
    mat_to_bone(st, wrist_l, f"J_Bip_{side_name}_Hand")

def miniball(pts):
    min_x = pts[0].x
    min_y = pts[0].y
    min_z = pts[0].z

    max_x = pts[0].x
    max_y = pts[0].y
    max_z = pts[0].z
    
    for pt in pts:
        min_x = min(min_x, pt.x)
        min_y = min(min_y, pt.y)
        min_z = min(min_z, pt.z)
        
        max_x = max(max_x, pt.x)
        max_y = max(max_y, pt.y)
        max_z = max(max_z, pt.z)
        
    c = mathutils.Vector()
    c.x = (min_x + max_x)/2
    c.y = (min_y + max_y)/2
    c.z = (min_z + max_z)/2
    
    r = 0
    for pt in pts:
        v = pt-c
        r = max(v.length, r)
    return c, r
        
        
csvfile = open("/media/moses/TRAINDATA/munge_april26/artificial_april28_again.csv", "w+")
augwriter = csv.writer(csvfile, delimiter=" ", quotechar="|", quoting=csv.QUOTE_NONNUMERIC)

obj_list = []
matrix_list = []

col = bpy.data.collections["delete"]

names = ["UpperArm", "Forearm", "Wrist"]

names += ["ThumbMetacarpal", "ThumbProximal", "ThumbDistal", "ThumbTip"]

for finger in ["Index", "Middle", "Ring", "Little"]:
    for bone in ["Metacarpal", "Proximal", "Intermediate", "Distal", "Tip"]:
        names.append(f"{finger}{bone}")

names_21kp = ["Wrist", "ThumbMetacarpal", "ThumbProximal", "ThumbDistal", "ThumbTip"]

for finger in ["Index", "Middle", "Ring", "Little"]:
    for bone in ["Proximal", "Intermediate", "Distal", "Tip"]:
        names_21kp.append(f"{finger}{bone}")

names_21kp.append("Forearm")

while col.objects:
    obj = col.objects[0]
#    col.objects.unlink(col.objects[0])
    bpy.data.objects.remove(obj, do_unlink = True)

obj_list.append(create_camera("cam", col))

obj_list.append(create_empty("UpperArm", col, 0.2))
obj_list.append(create_empty("Forearm", col, 0.1))
obj_list.append(create_empty("Wrist", col, 0.05))

for name in names[3:]:
    obj_list.append(create_empty(name, col, 0.02))

empties_21kp = []

for name in names_21kp:
    empties_21kp.append(create_empty(f"21_{name}", col, 0.02))

center_empty = create_empty("is this the center?", col, 0.05)


arm = bpy.data.objects["guy.002"]

for name in names:
    # Remove all constraints (watch out!)
    while arm.pose.bones[name].constraints:
        arm.pose.bones[name].constraints.remove(arm.pose.bones[name].constraints[0])
        
    
    constraint_type = "COPY_TRANSFORMS"
    
    if "Thumb" in name:
        if "Metacarpal" in name:
            print("metacarpal", name)
            constraint_type = "COPY_ROTATION"
    elif "Proximal" in name:
            print(name)
            constraint_type = "COPY_ROTATION"
            

    c = arm.pose.bones[name].constraints.new(constraint_type)
    c.target = D.objects[name]

#raise

st = State()

miniball_sphere = D.objects["Sphere"]
render_size = [384, 384]

    

c = pd.read_csv("/3/epics/ARTIFICIAL_DATA/artificial_sk/for_blender.csv", delimiter=" ")

b = list(range(len(c)))
random.shuffle(b)


for i in b: #400):
    e = np.array(c.iloc[i])
    g = e[1+7:]
    m = mathutils.Matrix()
    m.identity()
#    m = set_pose(obj_list[0], m, g)
    matrix_list.append(None)
    


    

    for j in range(3+25):
        g = e[1+j*7:]

        r = set_pose(obj_list[j], m, g)
        # wrist and onward
#        if j >= 4:
#            vec += r.to_translation()
#            vec_list.append(r.to_translation())

            
        matrix_list.append(r)
    
    
#    vec = mathutils.Vector()
    vec_list = []
    
    bpy.context.view_layer.update()
    
    for idx, name in enumerate(names_21kp[:-1]):
        bone = st.guy.pose.bones[name]
        loc = st.guy.matrix_world @ bone.matrix @ bone.location
        print(loc)
        empties_21kp[idx].location = loc
        empties_21kp[idx].keyframe_insert(data_path="location", frame=st.frame)
        print(name)
#        vec += loc
        vec_list.append(loc)

        

    # Calculate maximum rotation between the "center" and the outside keypoint, to figure out what the camera's FOV should be.
    center, radius = miniball(vec_list)
    
    miniball_sphere.location = center
    miniball_sphere.scale = [radius]*3
    
    miniball_sphere.keyframe_insert(data_path="scale", frame=st.frame)
    miniball_sphere.keyframe_insert(data_path="location", frame=st.frame)
    
    o = D.objects["Camera.001"]

    o.rotation_quaternion = simple_rotation(mathutils.Vector((0,0,-1)), center.normalized())
    o.keyframe_insert(data_path="rotation_quaternion", frame=st.frame)
    
#    angular_radius = math.tan(radius/center.length)
    # Tangent to sphere, not the other thing. Look in your notebook
    angular_radius = math.sin(radius/center.length)
    
    o.data.angle = angular_radius*2.
    # This adds a little padding
    o.data.angle *= 2.3
    
    o.data.keyframe_insert(data_path="lens", frame=st.frame)
        
    
    center_empty.location = center
    center_empty.keyframe_insert(data_path="location", frame=st.frame)
    
    
#    for idx, name in? enumerate(["Forearm"]):
    name = "Forearm"
    bone = st.guy.pose.bones[name]
    loc = st.guy.matrix_world @ bone.matrix @ bone.location
    print("before", loc)
    loc = (loc*1/5) +  (empties_21kp[0].location*4/5)
    print("after", loc)
#    raise
    
    empties_21kp[21].location = loc
    
    # 2/3 of the way back to the wrist
#    empties_21kp[21].location += empties_21kp[0].location*2
#    empties_21kp[21].location *= 0.3333
    
    empties_21kp[21].keyframe_insert(data_path="location", frame=st.frame)
    print(name)
#        vec += loc
    vec_list.append(loc)
    
    
    
    for obj in bpy.data.collections["lights"].objects:
        max_light_dist = 1
        obj.location = center + mathutils.Vector((random.uniform(-max_light_dist, max_light_dist), 
        random.uniform(-max_light_dist, max_light_dist), 
        random.uniform(-max_light_dist, max_light_dist)))
        obj.data.energy = 0.0 + random.random()*13.5
    
    # Render!
    bpy.context.scene.frame_current = st.frame

    
    fp_root = "/media/moses/TRAINDATA/munge_april26/"
    lum_sub = os.path.join("artificial_april28/", "{:07d}".format(st.frame) + "_luminance.jpg")
    mask_sub = os.path.join("artificial_april28/", "{:07d}".format(st.frame) + "_mask.jpg")
    

    

    bpy.context.scene.render.filepath = "/tmp/a"
    
    os.system(f"rm -r {fp_root}/0a_tmp/mask/*")
    os.system(f"rm -r {fp_root}/0a_tmp/luminance/*")
    
    
    bpy.data.scenes["Scene"].node_tree.nodes["File Output.003"].base_path = fp_root + "0a_tmp/mask"
    bpy.data.scenes["Scene"].node_tree.nodes["File Output.002"].base_path = fp_root + "0a_tmp/luminance"
    
    print(fp_root + "0a_tmp/mask")

    bpy.ops.render.render(write_still=True)
    bpy.ops.render.render()
    print(bpy.context.scene.render.filepath)
    
    out_luminance = os.path.join(fp_root, lum_sub)
    out_mask = os.path.join(fp_root, mask_sub)
    
    print(out_luminance)
    print(out_mask)
#    raise
    
    os.system(f"cp {fp_root}/0a_tmp/mask/* {out_mask}")
    os.system(f"cp {fp_root}/0a_tmp/luminance/* {out_luminance}")
        
    print(len(vec_list))


    numpy_pts = []
    row = [lum_sub]
    
    wrist_dist = vec_list[0].length
    
    palm_size = (vec_list[0]-vec_list[9]).length
    
    for pt in vec_list:
        cco = bpy_extras.object_utils.world_to_camera_view(C.scene, o, pt)
        x=(round(cco.x * render_size[0]))
        y=(render_size[1]-round(cco.y * render_size[1]))
        row.append(x)
        row.append(y)
        dist = (pt.length - wrist_dist)/ palm_size
        row.append(dist)
        print(dist)
    
    for i in range(22):
        row += [1, 1, 1]
    
    row.append(False) # All left hands!
    
    row.append(mask_sub)
    augwriter.writerow(row)
    csvfile.flush()


#    np.savetxt("/tmp/points_" + "{:07d}".format(st.frame), numpy_pts)
    
    
    

#    arm.pose.bones['J_Bip_L_Shoulder']
    
    st.frame += 1


    print()
    print()
    print()
    print()