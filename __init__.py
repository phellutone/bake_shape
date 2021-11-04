#
#Copyright (c) 2021 phellutone
#
#Released under the MIT license.
#see https://opensource.org/licenses/MIT
#

import bpy
import numpy as np

bl_info = {
    "name": "bake shape",
    "author": "phellutone",
    "version": (0, 1),
    "blender": (2, 93, 0),
    "location": "View3D > Sidebar > Edit Tab",
    "description": "bake shape keys to vertex groups",
    "warning": "work in progress",
    "support": "TESTING",
    "category": "Object"
}

class BAKESHAPE_OT_bake(bpy.types.Operator):
    bl_idname = "object.bake_shape"
    bl_label = "bake"
    bl_description = "bake shape keys to vertex groups"
    bl_options = {'REGISTER', 'UNDO'}
    
    def bake(self, obj, s):
        IS_REBAKE = True
        data = np.array([v for v in [vs.co for vs in s.data]])-np.array([v for v in [vs.co for vs in s.relative_key.data]])
        length = np.abs(data).max()*2
        data = data/length+0.5 if length != 0 else np.zeros(data.shape)
        for i in range(3):
            g = obj.vertex_groups.get(s.name+"_"+["X", "Y", "Z"][i])
            if not g:
                g = obj.vertex_groups.new(name=s.name+"_"+["X", "Y", "Z"][i])
                IS_REBAKE = False
            for idx in range(len(data)):
                g.add([idx], data[idx, i], "REPLACE")
        
        return (length, IS_REBAKE)
    
    def execute(self, context):
        obj = context.active_object
        
        if not obj.type == "MESH":
            return {'CANCELLED'}
        
        if not obj.data.shape_keys:
            return {'CANCELLED'}
        
        if not obj.data.shape_keys.use_relative:
            return {'CANCELLED'}
        
        for s in obj.data.shape_keys.key_blocks:
            if s.relative_key == s or s.mute:
                continue
            length, IS_REBAKE = self.bake(obj, s)
            self.report({'INFO'}, s.name+": "+str(length)+(", rebake" if IS_REBAKE else ""))
        
        return {'FINISHED'}
        

class OBJECT_PT_bake_shape(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Edit"
    bl_context = "objectmode"
    bl_idname = "VIEW3D_PT_bake_shape"
    bl_label = "bake shape"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        if not obj:
            return
        
        if not obj.type == "MESH":
            return
        
        if not obj.data.shape_keys:
            return
        
        if not obj.data.shape_keys.use_relative:
            return
        
        layout.operator(BAKESHAPE_OT_bake.bl_idname, text="bake")
        
classes = (
    BAKESHAPE_OT_bake,
    OBJECT_PT_bake_shape
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()