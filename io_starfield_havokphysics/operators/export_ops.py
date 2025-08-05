import bpy
import os
import subprocess
from io_starfield_havokphysics.export_util.starfield_export import starfield_fbx_export
from io_starfield_havokphysics.export_util.batfile_factory import generate_filtermanager_batfile
from io_starfield_havokphysics.export_util.post_process_hkx import post_process_hkx


class ExportVertexGroupWeightsOperator(bpy.types.Operator):
    bl_idname = "mesh.export_vertex_group_weights"
    bl_label = "Export vertex group weights"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.hkxPhysicsExport_props
        obj = context.active_object

        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object.")
            return {'CANCELLED'}

        vg_name = props.vertex_group_name
        if vg_name not in obj.vertex_groups:
            self.report({'ERROR'}, f"Vertex group '{vg_name}' not found.")
            return {'CANCELLED'}

        vgroup = obj.vertex_groups[vg_name]

        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.faces.ensure_lookup_table()

        uv_layer = bm.loops.layers.uv.active
        if not uv_layer:
            self.report({'ERROR'}, "Mesh has no active UV map.")
            bm.free()
            return {'CANCELLED'}

        loop_weights = []  # List of (uv_index, hex_weight)

        uv_index = 0
        for face in bm.faces:
            if len(face.verts) != 3:
                self.report({'ERROR'}, "Non-triangular face detected. Please triangulate the mesh.")
                bm.free()
                return {'CANCELLED'}

            for loop in face.loops:
                vert = loop.vert
                try:
                    weight = vgroup.weight(vert.index)
                except RuntimeError:
                    weight = 0.0
                hex_value = weight
                loop_weights.append((uv_index, hex_value))
                uv_index += 1

        bm.free()

        if props.exportpath:
            blend_path = props.exportpath
        else:
            blend_path = bpy.data.filepath
            if not blend_path:
                self.report({'ERROR'}, "Please save your .blend file first.")
                return {'CANCELLED'}

        export_dir = os.path.join(os.path.dirname(blend_path), "export_data/floatchannels")
        os.makedirs(export_dir, exist_ok=True)

        filename = f"{obj.name}_{vg_name}.txt"
        filepath = os.path.join(export_dir, filename)
        
        props = context.scene.hkxPhysicsExport_props
        export_mode = props.export_type
        
        clamp_min = context.scene.hkxPhysicsExport_props.clamp_min
        clamp_max = context.scene.hkxPhysicsExport_props.clamp_max
        
        export_mode_int = {
            'FLOAT': 0,
            'DISTANCE': 1,
            'ANGLE': 2
        }[export_mode]
                
        try:
            with open(filepath, 'w') as f:
                f.write(f"{export_mode_int}\n")
                for uv_idx, hex_weight in loop_weights:
                    w = (hex_weight * (clamp_max - clamp_min)) + clamp_min
                    f.write(f"{round(w, 5)}\n")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to write file: {str(e)}")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Exported {len(loop_weights)} UV weights to {filepath}")
        return {'FINISHED'}


class SaveHKXSelectionSetOperator(bpy.types.Operator):
    bl_idname = "mesh.extract_uv_indices"
    bl_label = "Save selected vertices to file"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.hkxPhysicsExport_props
        filename = props.filename.strip()
        if not filename:
            self.report({'ERROR'}, "Filename cannot be empty")
            return {'CANCELLED'}
        if not filename.endswith(".txt"):
            filename += ".txt"

        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        if props.exportpath:
            blend_path = props.exportpath
        else:
            blend_path = bpy.data.filepath
            if not blend_path:
                self.report({'ERROR'}, "Please save your .blend file first.")
                return {'CANCELLED'}

        export_dir = os.path.join(os.path.dirname(blend_path), "export_data/selectionsets")
        os.makedirs(export_dir, exist_ok=True)

        filename = obj.name + "_" + filename
        output_path = os.path.join(export_dir, filename)
        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.faces.ensure_lookup_table()

        uv_layer = bm.loops.layers.uv.active
        if not uv_layer:
            self.report({'ERROR'}, "Mesh has no UV layer")
            return {'CANCELLED'}

        uv_index_counter = 0
        loop_to_uv_index = {}
        
        for face in bm.faces:
            if len(face.verts) != 3:
                self.report({'ERROR'}, "Mesh contains non-triangular face(s). Operation cancelled.")
                return {'CANCELLED'}
            for loop in face.loops:
                loop_to_uv_index[loop] = uv_index_counter
                uv_index_counter += 1

        vertex_uv_map = {}
        for vert in bm.verts:
            if not vert.select:
                continue

            uv_entries = []
            for loop in vert.link_loops:
                if loop.face not in bm.faces or len(loop.face.verts) != 3:
                    continue
                if loop not in loop_to_uv_index:
                    continue

                uv_idx = loop_to_uv_index[loop]
                uv_entries.append((uv_idx, loop.face.index))

            if uv_entries:
                vertex_uv_map[vert.index] = uv_entries

        with open(output_path, 'w') as f:
            for vtx_idx, uv_refs in vertex_uv_map.items():
                f.write(f"{vtx_idx}: ")
                for uv_idx, face_idx in uv_refs:
                    f.write(f"{uv_idx} ")
                f.write("\n")

        bm.free()
        self.report({'INFO'}, f"HKX selection set saved to: {output_path}")
        return {'FINISHED'}

class ExportFBXAndRunImporterOperator(bpy.types.Operator):
    bl_idname = "mesh.export_and_run_fbximporter"
    bl_label = "Export havok scene file"

    def execute(self, context):
        obj = context.active_object
        props = context.scene.hkxPhysicsExport_props

        fbx_importer = props.fbx_importer_path

        if not os.path.isfile(fbx_importer):
            self.report({'ERROR'}, "FBXImporter path is invalid")
            return {'CANCELLED'}
        
        if props.exportpath and props.exportpath != "//":
            blend_dir = props.exportpath
        else:
            blend_path = bpy.data.filepath
            blend_dir = os.path.dirname(blend_path)

        fbx_path = os.path.join(blend_dir, f"{obj.name}.fbx")


        starfield_fbx_export(fbx_path)

        try:
            subprocess.run([fbx_importer, fbx_path], check=True)
        except subprocess.CalledProcessError as e:
            self.report({'ERROR'}, f"FBXImporter failed: {e}")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Exported and ran FBXImporter on: {fbx_path}")

        if props.run_filtermanager:
            batfile_filepath = generate_filtermanager_batfile(context, fbx_path)
            try:
                subprocess.run(batfile_filepath, shell=True, stdout = subprocess.PIPE)
            except subprocess.CalledProcessError as e:
                self.report({'ERROR'}, f"calling filtermanager failed: {e}")
                return {'CANCELLED'}
        return {'FINISHED'}

class PostProcessHKXOperator(bpy.types.Operator):
    bl_idname = "mesh.havok_cloth_postprocess"
    bl_label = "export post processed .hkx"

    filter_glob: bpy.props.StringProperty(default="*.hkx")
    filepath: bpy.props.StringProperty(subtype='FILE_PATH', options={'SKIP_SAVE'})

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):

        props = context.scene.hkxPhysicsExport_props
        meshconverter_dll = props.geometry_bridge_dll_path

        input_hkx = props.havok_cloth_hkx
        output_hkx = self.filepath

        if not os.path.isfile(meshconverter_dll):
            self.report({'ERROR'}, "MeshConverter.dll path is invalid")
            return {'CANCELLED'}

        if not os.path.isfile(input_hkx):
            self.report({'ERROR'}, f"input hkx path {input_hkx} is invalid")
            return {'CANCELLED'}

        status = post_process_hkx(input_hkx, output_hkx, meshconverter_dll)

        if status:
            return {'FINISHED'}
        else:
            return {'CANCELLED'}

