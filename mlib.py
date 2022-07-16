import sys  # nopep8
import os  # nopep8
sys.path.insert(0, os.path.dirname(__file__))  # nopep8
sys.path.append('/home/moses/.local/lib/python3.10/site-packages')  # nopep8

import bpy  # nopep8
import math  # nopep8


def create_empty(name="empty"):
    o = bpy.data.objects.new(name, None)

    bpy.context.scene.collection.objects.link(o)

    o.empty_display_size = .02
    o.empty_display_type = 'ARROWS'
    o.rotation_mode = 'QUATERNION'
    return o

def create_camera(name="empty"):
    c = bpy.data.cameras.new(name)
    o = bpy.data.objects.new(name, c)

    bpy.context.scene.collection.objects.link(o)

    o.rotation_mode = 'QUATERNION'
    return o
def create_light(name="empty"):
    # ('POINT', 'SUN', 'SPOT', 'AREA')
    c = bpy.data.lights.new(name, "POINT")
    o = bpy.data.objects.new(name, c)

    bpy.context.scene.collection.objects.link(o)

    return o


def new_constraint(obj, bone_name, type):
    return obj.pose.bones[bone_name].constraints.new(type)


def add_1dof_constraint(obj, bone_name):
    c = new_constraint(obj, bone_name, 'LIMIT_ROTATION')

    c.owner_space = 'LOCAL'

    c.use_limit_y = True
    c.use_limit_z = True

    c.use_limit_x = True
    c.max_x = math.radians(0)
    c.min_x = math.radians(-90)
