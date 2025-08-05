import bpy
import mathutils
import math


bone_axis_correction = mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'Z')
bone_axis_correction_inv = mathutils.Matrix.Rotation(math.radians(90.0), 4, 'Z')


def BoneAxisCorrection(T):
    return T @ bone_axis_correction

def BoneAxisCorrectionRevert(T):
    return T @ bone_axis_correction_inv

def starfield_fbx_export(fbx_filepath):
	# check armatures
	selObjects = bpy.context.selected_objects
	armatures = []
	collision_objects = []
	for selObj in selObjects:
	    if (selObj.type == 'ARMATURE') :
	        armatures.append(selObj)
	    if (selObj.type == 'MESH' and selObj.name.startswith("collision_")):
	        collision_objects.append(selObj)
	        

	if len(armatures)>1:
	    raise ValueError("Too many armatures selected")

	if len(armatures)==0:
	    raise ValueError("Too few armatures selected")
	   

	# handle armatures
	# make armature the active object

	bpy.context.view_layer.objects.active = armatures[0]
	bpy.ops.object.mode_set(mode='EDIT')
	# user selected from gui
	obj = bpy.context.edit_object
	bones = obj.data.edit_bones

	for cur_bone in bones:
	    T = BoneAxisCorrectionRevert(cur_bone.matrix)
	    cur_bone.matrix = T
	bpy.ops.object.mode_set(mode='OBJECT')
	    
	# fbx export with y up z forward, fbx scale all, no leaf bones, keep animations
	bpy.ops.export_scene.fbx(filepath=fbx_filepath,
	                         use_selection=True,
	                         global_scale=1.0,
	                         apply_unit_scale=True,
	                         apply_scale_options='FBX_SCALE_ALL',
	                         use_space_transform=True,
	                         axis_forward='Z',
	                         axis_up='Y',
	                         add_leaf_bones=False,
	                         bake_anim_use_all_actions=True,
	                         bake_anim_use_all_bones=True)
	                        
	                         
	bpy.ops.object.mode_set(mode='EDIT')
	for cur_bone in bones:
	    T = BoneAxisCorrection(cur_bone.matrix)
	    cur_bone.matrix = T

	bpy.ops.object.mode_set(mode='OBJECT')

