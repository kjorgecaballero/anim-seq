import bpy
from pathlib import Path
import re


def extract_number(filepath):
    """Extract numbers from filename for sorting"""
    match = re.search(r'(\d+)$', filepath.stem)
    return int(match.group(1)) if match else -1


def import_mesh_file(filepath):
    """Import a mesh file according to its extension"""
    file_ext = filepath.suffix.lower()
    
    try:
        if file_ext == '.fbx':
            bpy.ops.import_scene.fbx(filepath=str(filepath), axis_forward='-Z', axis_up='Y')
        elif file_ext == '.obj':
            bpy.ops.wm.obj_import(filepath=str(filepath))
        else:
            return None
            
        return bpy.context.selected_objects[-1] if bpy.context.selected_objects else None
        
    except Exception as e:
        print(f"Error importing {filepath}: {e}")
        return None