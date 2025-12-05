import bpy


def menu_func_import(self, context):
    self.layout.operator(
        "import_scene.meshseq", 
        text="Mesh Sequence (.fbx, .obj)"
    )


def menu_func_export(self, context):
    self.layout.operator(
        "export_scene.meshseq", 
        text="Mesh Sequence (.fbx, .obj)"
    )


def register():
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)