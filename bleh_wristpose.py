import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.append('/home/moses/.local/lib/python3.10/site-packages') # WHYYYYYYYY

print(sys.executable)
print(sys.path)
import bpy
import readcsv_wristpose

def create_empty(name = "empty"):
  o = bpy.data.objects.new( name, None )

  # due to the new mechanism of "collection"
  bpy.context.scene.collection.objects.link( o )

  # empty_draw was replaced by empty_display
  o.empty_display_size = .01
  o.empty_display_type = 'PLAIN_AXES'   
  return o

class State:
    collection = None
    file = None
    empties = []
    def __init__(self):
        self.collection = bpy.data.collections['Collection']
        self.frame = 0

def main():
    st = State()
    st.file = readcsv_wristpose.get_file()
    e = create_empty()
    e.rotation_mode = 'QUATERNION'
    e.empty_display_size = .1
    e.empty_display_type = 'ARROWS'
    st.empties.append(e)
    mul = 3.2
    for i in range(int(700/mul)):
        p,q = readcsv_wristpose.get_pos(st.file, int(i*mul))
        e.rotation_quaternion = q

        e.location = p
        e.keyframe_insert(data_path="location", frame=i)
        e.keyframe_insert(data_path="rotation_quaternion", frame=i)


main()