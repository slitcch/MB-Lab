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
if 1:
    import .
    exit(0)
    print(__file__)
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    print(sys.path)
    import magic2
    exit(0)

    import logging

    import time
    import datetime
    import json
    import os
    import numpy
    #from pathlib import Path
    from math import radians, degrees

    import bpy
    from bpy.app.handlers import persistent
    from bpy_extras.io_utils import ExportHelper, ImportHelper

    import addon_updater_ops
    import algorithms
    import animationengine
    import creation_tools_ops
    import expressionengine
    import expressionscreator
    import facerig
    import file_ops
    import hairengine
    import humanoid
    import humanoid_rotations
    import jointscreator
    import morphcreator
    import node_ops
    import numpy_ops
    import object_ops
    import proxyengine
    import transfor
    import utils
    import preferences
    import mesh_ops
    import measurescreator
    import skeleton_ops
    import vgroupscreator


    print('hi sisters?')
# finally:
#     print("bye sisters")
#     exit(0)