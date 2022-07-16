# MB-Lab
#
# MB-Lab fork website : https://github.com/animate1978/MB-Lab
#
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
#
# ManuelbastioniLAB - Copyright (C) 2015-2018 Manuel Bastioni

# MB-Lab Imports

# try:
from dataclasses import dataclass
import sys  # nopep8
import os  # nopep8
sys.path.insert(0, os.path.dirname(__file__))  # nopep8

import readcsv_fingerpose
import readcsv_wristpose
import bpy
import mathutils
import mlib
import mblab
import random
import math
import csv
import pandas as pd


# Type can be "IK",
# Used by something to

# def create_empty(name = "empty"):
#   o = bpy.data.objects.new( name, None )

#   # due to the new mechanism of "collection"
#   bpy.context.scene.collection.objects.link( o )

#   # empty_draw was replaced by empty_display
#   o.empty_display_size = .2
#   o.empty_display_type = 'PLAIN_AXES'
#   return o


make_guy = True
num_frames = 700


class State:
    collection = None
    file = None
    file_wristpose = None
    empties = []

    camera = None

    def __init__(self):
        self.collection = bpy.data.collections['Collection']
        self.frame = 0


# WXYZ, not XYZW.
sqrt2_2 = math.sqrt(2)/2
camera_forward = mathutils.Quaternion((sqrt2_2, sqrt2_2, 0, 0))
camera_left = mathutils.Quaternion((0.5, 0.5, 0.5, 0.5))
camera_right = mathutils.Quaternion((0.5, 0.5, -0.5, -0.5))
camera_top = mathutils.Quaternion((0, 1, 0, 0))
camera_bottom = mathutils.Quaternion((1, 0, 0, 0))


@dataclass
class camera_dir_pairing:
    name: str
    direction: mathutils.Quaternion


camera_dir_pairings = [
    camera_dir_pairing("forward", camera_forward),
    camera_dir_pairing("left", camera_left),
    camera_dir_pairing("right", camera_right),
    camera_dir_pairing("top", camera_top),
    camera_dir_pairing("bottom", camera_bottom),
]


def init_random(st: State):

    bpy.context.scene.frame_end = 1000
    bpy.context.scene.render.fps = 30
    bpy.context.scene.render.resolution_x = 512
    bpy.context.scene.render.resolution_y = 512
    camera = mlib.create_camera("camera_forward")
    bpy.context.scene.camera = camera
    st.camera = camera

    # point it up
    camera.rotation_quaternion = (0.707, 0.707, 0, 0)
    if False:
        # This is as close to where the index camera really would be
        # Half of Index camera baseline
        camera.location.x = -0.067489996552467346
        # Came up with this on a whim
        camera.location.y = 0.069146
        # Ditto
        camera.location.z = -0.025
    else:
        # This is moved back and up a little bit to get out of the way of the IK arm
        # Half of Index camera baseline
        camera.location.x = -0.067489996552467346
        # Came up with this on a whim
        camera.location.y = 0.061095
        # Ditto
        camera.location.z = -0.011319

    camera.data.lens_unit = 'FOV'
    camera.data.angle = math.pi/2
    # 1mm
    camera.data.clip_start = 0.001
    # 5 meters. Overkill but fine
    camera.data.clip_end = 5


def setup_arm_ik(doot, hand_target):
    ik = mlib.new_constraint(doot, "hand_L", "IK")

    ik.target = hand_target
    ik.chain_count = 3
    ik.use_tail = False

    copyrot = mlib.new_constraint(doot, "hand_L", "COPY_ROTATION")
    copyrot.target = hand_target

    # setup stiffness and constraints for shoulder
    clavicle = doot.pose.bones["clavicle_L"]
    clavicle.ik_stiffness_y = 0.6

    clavicle.ik_stiffness_x = 0.3
    clavicle.ik_stiffness_z = 0.3

    clavicle.use_ik_limit_x = True
    clavicle.use_ik_limit_y = True
    clavicle.use_ik_limit_z = True

    # Twist-ish
    clavicle.ik_min_y = math.radians(-10)
    clavicle.ik_max_y = math.radians(10)

    clavicle.ik_min_x = math.radians(-50)
    clavicle.ik_max_x = math.radians(50)

    clavicle.ik_min_z = math.radians(-50)
    clavicle.ik_max_z = math.radians(50)


def dumbest_possible_add_lights():

    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = random.uniform(
        0, 1)

    num_lights = int(random.uniform(1, 5))
    center = mathutils.Vector((0, 0.1, 0.3))
    print(num_lights)
    for i in range(num_lights):
        obj = mlib.create_light(str(i))
        max_light_dist = 1
        obj.location = center + mathutils.Vector((random.uniform(-max_light_dist, max_light_dist),
                                                  random.uniform(-max_light_dist,
                                                                 max_light_dist),
                                                  random.uniform(-max_light_dist, max_light_dist)))
        obj.data.energy = 0.0 + random.random()*13.5

    # for obj in bpy.data.collections["lights"].objects:
    #     max_light_dist = 1
    #     obj.location = center + mathutils.Vector((random.uniform(-max_light_dist, max_light_dist),
    #     random.uniform(-max_light_dist, max_light_dist),
    #     random.uniform(-max_light_dist, max_light_dist)))
    #     obj.data.energy = 0.0 + random.random()*13.5


def dumb_render_settings():
    bpy.context.scene.eevee.taa_render_samples = 16

    bpy.context.scene.eevee.use_bloom = True  # are we sure?
    bpy.context.scene.eevee.use_motion_blur = True
    bpy.context.scene.eevee.motion_blur_shutter = 0.6
    bpy.context.scene.eevee.motion_blur_steps = 3


def hand_joints_bone_root_position(bones, bone, camera_pos):
    return list((bones.matrix_world @ bone.matrix).translation - camera_pos)


def hand_joints(st, bones):
    locations = []

    locations.append(hand_joints_bone_root_position(
        bones, bones.pose.bones["hand_L"], st.camera.location))

    for finger in 'thumb', 'index', 'middle', 'ring', 'pinky':
        for joint in '01', '02', '03':
            name = finger+joint+"_L"
            locations.append(hand_joints_bone_root_position(
                bones, bones.pose.bones[name], st.camera.location))

        name = finger+'03_L'
        bone = bones.pose.bones[name]
        loc = bones.matrix_world @ bone.matrix @ mathutils.Vector((0, bone.length, 0))
        loc -= st.camera.location
        locations.append(loc)

    print(len(locations))
    return locations


def main():

    st = State()

    init_random(st)
    dumbest_possible_add_lights()
    dumb_render_settings()

    wrist_empty = mlib.create_empty('wrist_empty')
    wrist_empty.rotation_mode = 'QUATERNION'
    # wrist_empty.rotation_quaternion = (0, -0.903, 0, 0.430)
    # wrist_empty.rotation_quaternion = (0, 0.430, 0, 0.903)
    wrist_empty.rotation_quaternion = (-.304, .304, 0.639, 0.639)

    wrist_empty.location = (0.122, -0.29, 1.13+0.2)

    # This is dumb; the default rig's hand bone is 180 degrees around the forward axis wrong. But probably good to have a layer of indirection anyhow
    hand_target = mlib.create_empty('hand_target')
    if False:
        hand_target.rotation_quaternion.w = 0
        hand_target.rotation_quaternion.x = 0
        hand_target.rotation_quaternion.y = 0.785892
        hand_target.rotation_quaternion.z = -0.618364
    elif False:
        hand_target.rotation_quaternion = (-0.019, 0.009, 0.763, -0.647)
    else:
        hand_target.rotation_quaternion = (-0.013, 0.016, 0.763, -0.647)
    hand_target.parent = wrist_empty

    start_z = wrist_empty.location.z
    start_x = wrist_empty.location.x

    tip_correct_rot = mathutils.Quaternion((-0.707107, 0.707107, 0, 0))

    # might be equivalent to above
    wrist_correct_prerot = mathutils.Quaternion((0.707107, 0.707107, 0, 0))

    st.file_wristpose = readcsv_wristpose.get_file()

    for i in range(num_frames):
        p, q = readcsv_wristpose.get_pos(st.file_wristpose, int(i*(144/30)))
        wrist_empty.location.x = p.x
        wrist_empty.location.y = -p.z
        wrist_empty.location.z = p.y

        q.rotate(wrist_correct_prerot)
        # wrist_empty.location = p
        # q.
        wrist_empty.rotation_quaternion = q

        # wrist_empty.location.z = start_z + 0.02*math.sin(st.frame*0.1)
        # wrist_empty.location.x = start_x + 0.03*math.cos(st.frame*0.1)
        wrist_empty.keyframe_insert(data_path="location", frame=st.frame)
        wrist_empty.keyframe_insert(
            data_path="rotation_quaternion", frame=st.frame)
        st.frame += 1

    st.file = readcsv_fingerpose.get_file()

    for i in range(26):
        e = mlib.create_empty()
        # e.rotation_mode = 'QUATERNION'
        e.empty_display_size = .01
        # e.empty_display_type = 'ARROWS'
        e.parent = wrist_empty
        st.empties.append(e)

    for i in range(num_frames):
        for j in range(26):
            # s = readcsv_fingerpose.readcsv_fingerpose_settings(st.file, 1.1)
            s = readcsv_fingerpose.readcsv_fingerpose_settings(st.file, 1.02)
            p, q = readcsv_fingerpose.get_joint(s, int(i*(54/30)), j)

            # q = q.rotate()
            newguy = tip_correct_rot.copy()
            newguy.rotate(q)
            q = newguy
            # q = tip_correct_rot.rotate(q)
            e = st.empties[j]
            e.rotation_quaternion = q

            e.location = p
            e.keyframe_insert(data_path="location", frame=i)
            e.keyframe_insert(data_path="rotation_quaternion", frame=i)

    if make_guy:

        root_empty = mlib.create_empty()
        root_empty.location.z = -1.7158
        root_empty.location.y = -0.12389

        # rotate 180 degrees on Blender's Z/vertical axis - MB-Lab characters are pointing backwards for some reason.
        root_empty.rotation_quaternion = (0, 0, 0, -1)

        character_list = [
            "f_af01",
            "f_as01",
            "f_ca01",
            "f_la01",
            "m_af01",
            "m_as01",
            "m_ca01",
            "m_la01",
            # "f_an01",
            # "f_an02",
            # "f_an03",
            # "m_an01",
            # "m_an02",
            # "m_an03",
            "f_ft01",
            "m_ft01",
            "m_ft02"
        ]

        settings = mblab.humanoid_settings(
            # character_identifier = random.choice(character_list),
            character_identifier="m_ca01",
            use_ik=False,
            use_muscle=False,
        )

        mblab.start_lab_session(settings)

        bones_object = None
        for obj in bpy.data.objects:
            if "doot doot" in obj.name:
                bones_object = obj
        if bones_object == None:
            raise
        bones_object.parent = root_empty

        setup_arm_ik(bones_object, hand_target)

        pairings = [
            (readcsv_fingerpose.XRT_HAND_JOINT_THUMB_TIP, "thumb03_L"),
            (readcsv_fingerpose.XRT_HAND_JOINT_INDEX_TIP, "index03_L"),
            (readcsv_fingerpose.XRT_HAND_JOINT_MIDDLE_TIP, "middle03_L"),
            (readcsv_fingerpose.XRT_HAND_JOINT_RING_TIP, "ring03_L"),
            (readcsv_fingerpose.XRT_HAND_JOINT_LITTLE_TIP, "pinky03_L"),
        ]

        for pair in pairings:
            ik = mlib.new_constraint(bones_object, pair[1], "IK")
            ik.target = st.empties[pair[0]]
            ik.chain_count = 3
            ik.use_tail = True
            ik.use_rotation = True
            ik.orient_weight = 0.05

        joints_1dof = ["thumb02_L", "thumb03_L",
                       "index02_L", "index03_L",
                       "middle02_L", "middle03_L",
                       "ring02_L", "ring03_L",
                       "pinky02_L", "pinky03_L", ]

        for joint in joints_1dof:
            bones_object.pose.bones[joint].lock_ik_y = True
            bones_object.pose.bones[joint].lock_ik_z = True

            bones_object.pose.bones[joint].use_ik_limit_x = True
            bones_object.pose.bones[joint].ik_min_x = math.radians(-100)
            bones_object.pose.bones[joint].ik_max_x = math.radians(6)
            # bones_object.pose.bones[joint].ik_max_x = math.radians(0)

        proximals = ["index01_L",
                     "middle01_L",
                     "ring01_L",
                     "pinky01_L"]

        for joint in proximals:
            bone = bones_object.pose.bones[joint]
            bone.use_ik_limit_x = True
            bone.ik_min_x = math.radians(-100)
            bone.ik_max_x = math.radians(35)

            bone.use_ik_limit_y = True
            bone.ik_min_y = math.radians(-10)
            bone.ik_max_y = math.radians(10)

            bone.use_ik_limit_z = True
            bone.ik_min_z = math.radians(-30)
            bone.ik_max_z = math.radians(30)

        joint = "thumb01_L"
        bone = bones_object.pose.bones[joint]
        bone.use_ik_limit_x = True
        bone.ik_min_x = math.radians(-45)
        bone.ik_max_x = math.radians(45)

        bone.use_ik_limit_y = True
        bone.ik_min_y = math.radians(-10)
        bone.ik_max_y = math.radians(10)

        bone.use_ik_limit_z = True
        bone.ik_min_z = math.radians(-40)
        bone.ik_max_z = math.radians(40)

        # mlib.add_1dof_constraint(bones_object, joint)

        # for j_idx in readcsv_fingerpose.

    render = False

    # MBLab sets this for some reason
    for scene in bpy.data.scenes:
        print("scene is", scene)
        scene.render.engine = 'BLENDER_EEVEE'

    # for i in range(20):

    if (render):
        for i in range(20):


            for idx, pair in enumerate(camera_dir_pairings):
                st.camera.rotation_quaternion = pair.direction

                print('render', i)
                bpy.context.scene.frame_current = i
                bpy.context.scene.render.filepath = f"/3/inshallah/{i}{pair.name}.png"
                bpy.ops.render.render(write_still=True)

            # Take hand joints array and write it to a csv file.
            # Note we do this after rendering so that the view layer is updated and the bones are where we want them to be.
            hand_joints_array = hand_joints(st, bones_object)
            df = pd.DataFrame(hand_joints_array)
            print(df)
            df.to_csv(f"/3/inshallah/{i}.csv", encoding='utf-8', index=False)

    # wrist_empty.rotation
    # copy

    print("hey kids")


if __name__ == "__main__":
    main()
