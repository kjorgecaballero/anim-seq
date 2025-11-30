import bpy
from pathlib import Path
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    StringProperty,
)
from bpy_extras.io_utils import ImportHelper

from ..utils.mesh_utils import extract_number, import_mesh_file


class ANIM_SEQ_OT_import_sequence(bpy.types.Operator, ImportHelper):
    """Importa una secuencia de mallas (FBX/OBJ) como shapekeys"""
    
    bl_idname = "import_scene.meshseq"
    bl_label = "Import Mesh Sequence"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".*"
    filter_glob: StringProperty(default="*.fbx;*.obj", options={"HIDDEN"})

    files: CollectionProperty(
        name="File Path",
        description="Archivos para importar la secuencia",
        type=bpy.types.OperatorFileListElement,
    )
    directory: StringProperty()

    relative_shapekey: BoolProperty(
        name="Relative ShapeKey",
        description="Importar shapekeys como relativas",
        default=True,
    )

    def execute(self, context):
        filepaths = [Path(self.directory, f.name) for f in self.files]
        if not filepaths:
            filepaths.append(Path(self.directory, self.filename))

        filepaths.sort(key=extract_number)
        self.create_shapekeys(filepaths)

        return {"FINISHED"}

    def create_shapekeys(self, filepaths):
        if not filepaths:
            self.report({'ERROR'}, "No files selected")
            return None

        # Importar primer archivo
        main_obj = import_mesh_file(filepaths[0])
        if not main_obj:
            self.report({'ERROR'}, f"Failed to import {filepaths[0]}")
            return None

        main_obj.location = (0, 0, 0)
        main_obj.rotation_euler = (1.5708, 0, 0)

        if not main_obj.data.shape_keys:
            main_obj.shape_key_add(name="Basis")

        # Importar el resto como shapekeys
        for filepath in filepaths[1:]:
            current_obj = import_mesh_file(filepath)
            if not current_obj:
                continue
                
            current_obj.location = (0, 0, 0)
            current_obj.rotation_euler = (1.5708, 0, 0)

            bpy.context.view_layer.objects.active = main_obj
            bpy.ops.object.join_shapes()
            bpy.data.objects.remove(current_obj, do_unlink=True)

        # Contar shapekeys (sin incluir Basis)
        shapekey_count = len(main_obj.data.shape_keys.key_blocks) - 1
        
        # Animar shapekeys
        if shapekey_count > 0:
            for i, key_block in enumerate(main_obj.data.shape_keys.key_blocks):
                if key_block.name == "Basis":
                    continue
                
                anim_index = i - 1
                
                key_block.value = 0.0
                key_block.keyframe_insert("value", frame=anim_index - 1)
                key_block.value = 1.0
                key_block.keyframe_insert("value", frame=anim_index)
                key_block.value = 0.0
                key_block.keyframe_insert("value", frame=anim_index + 1)

        # Configurar tiempo
        bpy.context.scene.frame_start = 0
        bpy.context.scene.frame_end = max(shapekey_count, 1)

        return main_obj


def register():
    bpy.utils.register_class(ANIM_SEQ_OT_import_sequence)


def unregister():
    bpy.utils.unregister_class(ANIM_SEQ_OT_import_sequence)