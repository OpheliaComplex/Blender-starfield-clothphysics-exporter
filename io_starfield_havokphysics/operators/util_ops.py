import bpy
import os
import subprocess

class SelectVerticesFromFileOperator(bpy.types.Operator):
    bl_idname = "mesh.select_vertices_from_file"
    bl_label = "Select pre-saved vertices from File"

    def execute(self, context):
        props = context.scene.hkxPhysicsExport_props
        obj = bpy.context.active_object

        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        # Ensure correct filename
        filename = props.selectionset_file
        if not filename.startswith(obj.name + "_"):
            filename = f"{obj.name}_{filename}"

        if props.exportpath:
            blend_path = props.exportpath
        else:
            blend_path = bpy.data.filepath
        if not blend_path:
            self.report({'ERROR'}, "Please save your .blend file first.")
            return {'CANCELLED'}

        folder = os.path.join(os.path.dirname(blend_path), "export_data", "selectionsets")
        filepath = os.path.join(folder, filename)

        if not os.path.isfile(filepath):
            self.report({'ERROR'}, f"File not found: {filepath}")
            return {'CANCELLED'}

        # Go to edit mode and deselect all
        if bpy.context.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        mesh = obj.data
        selected_indices = []

        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if ":" in line:
                        try:
                            index = int(line.split(":")[0])
                            selected_indices.append(index)
                        except ValueError:
                            continue
        except Exception as e:
            self.report({'ERROR'}, f"Failed to read file: {e}")
            return {'CANCELLED'}

        for idx in selected_indices:
            if 0 <= idx < len(mesh.vertices):
                mesh.vertices[idx].select = True

        bpy.ops.object.mode_set(mode='EDIT')
        self.report({'INFO'}, f"Selected {len(selected_indices)} vertices from {filename}")
        return {'FINISHED'}

class OpenSelectionSetFolderOperator(bpy.types.Operator):
    bl_idname = "mesh.open_uv_folder"
    bl_label = "Open Output Folder"

    def execute(self, context):
        props = context.scene.hkxPhysicsExport_props
        if props.exportpath:
            folder = props.exportpath
        else:
            folder = bpy.data.filepath
            self.report({'WARNING'}, "Export folder have not been set, using blend file path")

        if folder == "//":
            #in that case just override to abspath
            blend_path = bpy.data.filepath
            folder = os.path.dirname(blend_path)

        if os.name == 'nt':
            subprocess.Popen(f'explorer "{folder}"')
        elif os.name == 'posix':
            subprocess.Popen(['xdg-open', folder])
        else:
            self.report({'WARNING'}, "Unsupported OS for opening folder")
        return {'FINISHED'}

class SelectAbsDirPathBrowserOperator(bpy.types.Operator):
    bl_idname = "wm.select_export_folder"
    bl_label = "Select Export Folder"

    filepath: bpy.props.StringProperty(subtype='DIR_PATH')

    # This will execute when the user selects a folder
    def execute(self, context):
        # Get the file path selected by the user
        selected_directory = self.filepath

        #detect relative path blender syntax
        if selected_directory == "//":
            #in that case just override to abspath
            blend_path = bpy.data.filepath
            selected_directory = os.path.dirname(blend_path)

        props = context.scene.hkxPhysicsExport_props
        props.exportpath = selected_directory
        return {'FINISHED'}

    # This defines the file browser settings
    def invoke(self, context, event):
        # Open the folder selection dialog
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
