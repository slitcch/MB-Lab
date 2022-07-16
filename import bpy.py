import bpy
import sys
import os
import readcsv_fingerpose

def create_empty(name = "empty"):
  o = bpy.data.objects.new( name, None )

  # due to the new mechanism of "collection"
  bpy.context.scene.collection.objects.link( o )

  # empty_draw was replaced by empty_display
  o.empty_display_size = .2
  o.empty_display_type = 'PLAIN_AXES'   
  return o

class State:
    collection = None
    file = None
    def __init__(self):
        self.collection = bpy.data.collections['Collection']
        self.frame = 0

def main():
    st = State()
    st.file = readcsv_fingerpose.get_file()