import bpy
from pathlib import Path
import re


def extract_number(filepath):
    match = re.search(r'(\d+)$', filepath.stem)
    return int(match.group(1)) if match else -1


def import_mesh_file(filepath):
    file_ext = filepath.suffix.lower()
    if file_ext == '.obj':
        try:
            bpy.ops.wm.obj_import(filepath=str(filepath))
            return bpy.context.selected_objects[-1] if bpy.context.selected_objects else None
        except Exception as e:
            print(f"Error importing {filepath}: {e}")
            return None
    else:
        return None