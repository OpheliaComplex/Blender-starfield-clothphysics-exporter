import bpy


class HavokPhysicsPanel(bpy.types.Panel):
    bl_label = "Havok physics exporter"
    bl_idname = "VIEW3D_PT_havok_exporter"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HavokPhysicsExport'

    def draw(self, context):
        layout = self.layout
        props = context.scene.hkxPhysicsExport_props
        obj = context.active_object
        scene = context.scene
        
        layout.label(text="Root export folder, selection sets will be saved here. Default: this blend files' location")
        layout.prop(props, "exportpath")

        layout.label(text="------------- Vertex selection sets -------------")
        layout.prop(props, "filename")
        layout.operator("mesh.extract_uv_indices", icon='EXPORT')
        layout.separator()
        layout.label(text="Manage saved vertex selection files:")
        layout.prop(props, "selectionset_file")
        layout.operator("mesh.select_vertices_from_file", icon='RESTRICT_SELECT_OFF')
        layout.operator("mesh.open_uv_folder", icon='FILE_FOLDER')
        layout.separator()
        layout.label(text="------------- Vertex float data -------------")
        layout.prop(props, "export_type", text="Weight Type")
        layout.prop(props, "vertex_group_name")
        layout.operator("mesh.export_vertex_group_weights", icon='EXPORT')
            
            
        layout.separator()
        layout.label(text="------------- Export .hkt/.hkx section -------------")
        layout.prop(props, "fbx_importer_path")
        layout.prop(props, "geometry_bridge_dll_path")
        layout.prop(props, "havok_filtermanager_path")
        layout.prop(props, "havok_filtermanager_settings_path")
        col = layout.column()
        row = col.split(factor=0.8)
        row.operator("mesh.export_and_run_fbximporter", icon='EXPORT')
        row.prop(props, "run_filtermanager")
        layout.separator()
        layout.label(text="---------- Post process .hkx for starfield ----------")
        layout.prop(props, "havok_cloth_hkx")
        layout.operator("mesh.havok_cloth_postprocess", icon='EXPORT')
