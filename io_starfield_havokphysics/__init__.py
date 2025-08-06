# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    "name": "Havok physics exporter",
    "author": "OpheliaComplex and Tlarok",
    "version": (1, 0),
    "blender": (4, 3, 0),
    "location": "View3D > Sidebar > Havok export",
    "description": "Starfield Havok physics export tools",
    "warning": "",
    "category": "Import-Export | Object",
    }



import bpy
from io_starfield_havokphysics.ui.panels import HavokPhysicsPanel
from io_starfield_havokphysics.ui.properties import HavokExportProperties
from io_starfield_havokphysics.operators.export_ops import ExportVertexGroupWeightsOperator, SaveHKXSelectionSetOperator,  ExportFBXAndRunImporterOperator, PostProcessHKXOperator
from io_starfield_havokphysics.operators.util_ops import SelectVerticesFromFileOperator, OpenSelectionSetFolderOperator, SelectAbsDirPathBrowserOperator


classes = [
    HavokPhysicsPanel,
    HavokExportProperties,
    ExportVertexGroupWeightsOperator, 
    SelectVerticesFromFileOperator, 
    SaveHKXSelectionSetOperator, 
    OpenSelectionSetFolderOperator, 
    ExportFBXAndRunImporterOperator, 
    PostProcessHKXOperator,
    SelectAbsDirPathBrowserOperator
]

def register():
    # Register all classes
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            print(f"Class {cls.__name__} already registered")
    
    # Initialize properties
    bpy.types.Scene.hkxPhysicsExport_props = bpy.props.PointerProperty(type=HavokExportProperties)

def unregister():
    # Unregister all classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    # Remove properties
    del bpy.types.Scene.hkxPhysicsExport_props

if __name__ == "__main__":
    register()