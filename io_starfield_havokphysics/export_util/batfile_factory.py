import bpy
import os

def generate_filtermanager_batfile(context, fbx_filepath, batfile_name=""):

	fbx_filename = os.path.basename(fbx_filepath)
	hkt_filename = fbx_filename.replace('.fbx','.hkt')

	props = context.scene.hkxPhysicsExport_props

	if props.exportpath and props.exportpath != "//":
		export_folder = props.exportpath
	else:
		blend_path = bpy.data.filepath
		export_folder = os.path.dirname(blend_path)

	FBXImporter = props.fbx_importer_path
	filtermanagersettings = props.havok_filtermanager_settings_path
	filtermanager = props.havok_filtermanager_path

	batfile_str=f"""
\"{FBXImporter}\" -t -d \"{export_folder}\" \"{fbx_filepath}\"

\"{filtermanager}\" --settings=\"{filtermanagersettings}\" --asset=\"{export_folder}\\{fbx_filename}\"  -i \"{export_folder}\\{hkt_filename}\"

"""
	if batfile_name:
		out_path = batfile_name
	else:
		out_path = f"{export_folder}\\run_filtermanager_{fbx_filename.replace('.fbx', '.bat')}"

	with open(out_path, "w") as f:
		f.write(batfile_str)

	
	return out_path
