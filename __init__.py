bl_info = {
    "name": "Anim Sequence IO",
    "author": "Siruka",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "File > Import",
    "description": "Import mesh sequences (FBX/OBJ) as shapekeys with animation",
    "category": "Import-Export",
}

from . import operators, ui, utils

def register():
    operators.register()
    ui.register()

def unregister():
    operators.unregister()
    ui.unregister()