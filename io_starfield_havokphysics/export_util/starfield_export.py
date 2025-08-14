import bpy
import mathutils
import math


bone_axis_correction = mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'Z')
bone_axis_correction_inv = mathutils.Matrix.Rotation(math.radians(90.0), 4, 'Z')

def BoneAxisCorrection(T):
    return T @ bone_axis_correction

def BoneAxisCorrectionRevert(T):
    return T @ bone_axis_correction_inv


revert_rename_dict = {}



rename_dict = {"Thigh.R": "R_Thigh", "Calf.R": "R_Calf", "Foot.R": "R_Foot", "Toe.R": "R_Toe", "CalfMass.R": "R_CalfMass", "Knee.R": "R_Knee",
"Thigh_Twist.R": "R_Thigh_Twist", "Thigh_Twist1.R": "R_Thigh_Twist1", "Thigh.L": "L_Thigh", "Calf.L": "L_Calf", "Foot.L": "L_Foot", "Toe.L": "L_Toe",
"CalfMass.L": "L_CalfMass", "Knee.L": "L_Knee", "Thigh_Twist.L": "L_Thigh_Twist", "Thigh_Twist1.L": "L_Thigh_Twist1", "Butt.L": "L_Butt", "Butt.R": "R_Butt",
"Balls.R": "R_Balls", "Balls.L": "L_Balls", "Vag.R": "R_Vag", "Vag.L": "L_Vag", "Eye.L": "L_Eye", "Eye.R": "R_Eye",
"Ear1.R": "R_Ear1", "Ear2.R": "R_Ear2", "Ear1.L": "L_Ear1", "Ear2.L": "L_Ear2", "Clavicle.L": "L_Clavicle", "Biceps.L": "L_Biceps",
"Forearm.L": "L_Forearm", "Wrist.L": "L_Wrist", "AnimObject1.L": "L_AnimObject1", "AnimObject2.L": "L_AnimObject2", "AnimObject3.L": "L_AnimObject3", "Thumb.L": "L_Thumb",
"Thumb1.L": "L_Thumb1", "Thumb2.L": "L_Thumb2", "Index.L": "L_Index", "Index1.L": "L_Index1", "Index2.L": "L_Index2", "Middle.L": "L_Middle",
"Middle1.L": "L_Middle1", "Middle2.L": "L_Middle2", "Ring.L": "L_Ring", "Ring1.L": "L_Ring1", "Ring2.L": "L_Ring2", "Cup.L": "L_Cup",
"Pinky.L": "L_Pinky", "Pinky1.L": "L_Pinky1", "Pinky2.L": "L_Pinky2", "Arm.L": "L_Arm", "Wrist_Twist.L": "L_Wrist_Twist", "Wrist_Twist1.L": "L_Wrist_Twist1",
"Wrist_Twist2.L": "L_Wrist_Twist2", "Elbow.L": "L_Elbow", "Biceps_Twist.L": "L_Biceps_Twist", "ArmMass.L": "L_ArmMass", "Deltoid.L": "L_Deltoid", "Biceps_Twist1.L": "L_Biceps_Twist1",
"Clavicle.R": "R_Clavicle", "Biceps.R": "R_Biceps", "Forearm.R": "R_Forearm", "Wrist.R": "R_Wrist", "AnimObject1.R": "R_AnimObject1", "AnimObject2.R": "R_AnimObject2",
"AnimObject3.R": "R_AnimObject3", "Cup.R": "R_Cup", "Pinky.R": "R_Pinky", "Pinky1.R": "R_Pinky1", "Pinky2.R": "R_Pinky2", "Thumb.R": "R_Thumb",
"Thumb1.R": "R_Thumb1", "Thumb2.R": "R_Thumb2", "Ring.R": "R_Ring", "Ring1.R": "R_Ring1", "Ring2.R": "R_Ring2", "Middle.R": "R_Middle",
"Middle1.R": "R_Middle1", "Middle2.R": "R_Middle2", "Index.R": "R_Index", "Index1.R": "R_Index1", "Index2.R": "R_Index2", "Arm.R": "R_Arm",
"Wrist_Twist.R": "R_Wrist_Twist", "Wrist_Twist1.R": "R_Wrist_Twist1", "Wrist_Twist2.R": "R_Wrist_Twist2", "Elbow.R": "R_Elbow", "Biceps_Twist.R": "R_Biceps_Twist", "ArmMass.R": "R_ArmMass",
"Deltoid.R": "R_Deltoid", "Biceps_Twist1.R": "R_Biceps_Twist1", "HandIk.R": "R_HandIk", "HandIk.L": "L_HandIk", "Pecs.R": "R_Pecs", "Nipple.R": "R_Nipple",
"Pecs.L": "L_Pecs", "Nipple.L": "L_Nipple"}


def rename_on_export(bone):
	if bone.name in rename_dict.keys():
		new_bone_name = rename_dict[bone.name]
		# store to flip back later
		revert_rename_dict[new_bone_name] = bone.name
		bone.name = new_bone_name
		

def revert_bone_renaming(bone):
	if bone.name in revert_rename_dict.keys():
		bone.name = revert_rename_dict[bone.name]

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
	    rename_on_export(cur_bone)

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
	    revert_bone_renaming(cur_bone)

	bpy.ops.object.mode_set(mode='OBJECT')

