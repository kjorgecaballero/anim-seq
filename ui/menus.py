import bpy


def menu_func_import(self, context):
    self.layout.operator(
        "import_scene.meshseq", 
        text="Mesh Sequence As Shapekey (.fbx, .obj)"
    )


def register():
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)