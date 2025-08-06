import bpy
from bpy.props import StringProperty, EnumProperty, FloatProperty, BoolProperty, IntVectorProperty
import os

def list_saved_files(self, context):
    
    props = context.scene.hkxPhysicsExport_props
    obj = context.active_object
    if not obj:
        return [("NONE", "None", "", 0)]
    
    if props.exportpath and props.exportpath != "//":
        blend_path = props.exportpath
        blend_directory = blend_path
    elif props.exportpath == "//": 
        # bad, shouldn't happen but we try to fix anyway
        # from my experience this works but blender pukes a ton of errors to console while doing it
        blend_path = bpy.data.filepath
        blend_directory = os.path.abspath(os.path.dirname(blend_path))
        props.exportpath = blend_directory
    else:
        blend_path = bpy.data.filepath
        blend_directory = os.path.dirname(blend_path)

    folder = os.path.abspath(os.path.join(blend_directory, "export_data", "selectionsets"))
    if not os.path.exists(folder):
        printf(f"No export data at {folder}")
        return [("NONE", "None", "", 0)]

    files = []
    prefix = obj.name + "_"
    for fname in os.listdir(folder):
        if fname.endswith(".txt") and fname.startswith(prefix):
            short_name = fname[len(prefix):-4]  # strip prefix and ".txt"
            files.append((fname, short_name, ""))

    if not files:
        files = [("NONE", "None", "")]

    return files


class HavokExportProperties(bpy.types.PropertyGroup):

    def vertex_group_items(self, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            return [(vg.name, vg.name, "") for vg in obj.vertex_groups]
        return [("NONE", "None", "")]

    vertex_group_name: bpy.props.EnumProperty(
        name="Vertex Group",
        description="Select a vertex group",
        items=vertex_group_items
    )

    def update_selected_file(self, context):
        obj = context.active_object
        if not obj or not self.selected_file or self.selected_file == "NONE":
            return

        prefix = obj.name + "_"
        filename = self.selected_file

        if filename.startswith(prefix):
            filename = filename[len(prefix):]

        if filename.lower().endswith(".txt"):
            filename = filename[:-4]

        self.filename = filename
 
    addon_script_file = os.path.realpath(__file__)
    addon_directory = os.path.dirname(addon_script_file)   
    hko_settings_file = os.path.join(addon_directory, "filtermanagersettings", "default_filtersetup.hko")

    filename: bpy.props.StringProperty(
        name="selection set name",
        description="Name for the  vertex selection set",
        default="selected_vertices"
    )
    
    exportpath: bpy.props.StringProperty(
        name="Folder path",
        description="Path to root export folder to save output data to",
        default="",
        subtype='DIR_PATH'
    )
    
    export_type: bpy.props.EnumProperty(
        name="Export Type",
        description="Choose the type of export",
        items=[
            ('FLOAT', "Float", "Export as float", 0),
            ('DISTANCE', "Distance", "Export as distance", 1),
            ('ANGLE', "Angle", "Export as angle", 2),
        ],
        default='FLOAT'
    )
    
    selectionset_file: bpy.props.EnumProperty(
        name="Saved Files",
        description="Choose a previously saved file",
        items=list_saved_files,
        update=update_selected_file
    )

    fbx_importer_path: bpy.props.StringProperty(
        name="FBXImporter.exe path",
        description="Path to FBXImporter executable",
        subtype='FILE_PATH',
        default="YOU HAVE TO SET THIS"
    )

    geometry_bridge_dll_path: bpy.props.StringProperty(
        name="MeshConverter.dll path",
        description="Path to MeshConverter.dll",
        subtype='FILE_PATH',
        default="YOU HAVE TO SET THIS"
    )

    havok_filtermanager_path: bpy.props.StringProperty(
        name="hctStandAloneFilterManager.exe path",
        description="Path to hctStandAloneFilterManager.exe",
        subtype='FILE_PATH',
        default="C:\\ProgramData\\BGS\\ArtTools\\HavokContentTools\\hctStandAloneFilterManager.exe"
    )

    havok_filtermanager_settings_path: bpy.props.StringProperty(
        name="havok filtermanager settings path",
        description="Path to filter manager settings (.hko)",
        subtype='FILE_PATH',
        default=hko_settings_file
    )

    run_filtermanager : bpy.props.BoolProperty(
        name="Run filtermanager",
        description="Generates a bat file and calls filtermanager with it  on export",
        default=True
    )

    havok_cloth_hkx: bpy.props.StringProperty(
        name=".hkx to postprocess",
        description="path to .hkx file from havok cloth",
        subtype='FILE_PATH'
    )