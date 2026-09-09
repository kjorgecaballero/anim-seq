import bpy
import os
from bpy_extras.io_utils import ExportHelper
from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
)


class ANIM_SEQ_OT_export_sequence(bpy.types.Operator, ExportHelper):
    """Export mesh sequence as OBJ for each frame (with vertex colors)"""
    
    bl_idname = "export_scene.meshseq"
    bl_label = "Export OBJ Sequence"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".obj"
    filter_glob: StringProperty(
        default="*.obj",
        options={'HIDDEN'},
    )

    frame_start: IntProperty(
        name="Start Frame",
        description="Start frame for export",
        default=0,
        min=0,
    )

    frame_end: IntProperty(
        name="End Frame",
        description="End frame for export",
        default=10,
        min=0,
    )

    frame_step: IntProperty(
        name="Frame Step",
        description="Export every X frames",
        default=1,
        min=1,
    )

    export_mesh_only: BoolProperty(
        name="Mesh Only",
        description="Export only mesh without bones",
        default=True,
    )

    export_vertex_colors: BoolProperty(
        name="Vertex Colors",
        description="Export vertex colors in OBJ files (Blender 3.3+)",
        default=True,
    )

    def invoke(self, context, event):
        self.frame_start = context.scene.frame_start
        self.frame_end = context.scene.frame_end
        if context.active_object:
            self.filepath = context.active_object.name + "_sequence"
        else:
            self.filepath = "sequence"
        return super().invoke(context, event)

    def execute(self, context):
        folder_path = self.filepath
        if os.path.isfile(folder_path) or '.' in os.path.basename(folder_path):
            folder_path = os.path.dirname(folder_path)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        ext = ".obj"
        if self.filepath and self.filepath != "":
            base_name = os.path.basename(self.filepath)
            if '.' in base_name:
                base_name = os.path.splitext(base_name)[0]
        else:
            base_name = "frame"

        start_frame = self.frame_start
        end_frame = self.frame_end

        bpy.ops.object.mode_set(mode='OBJECT')

        original_selection = context.selected_objects.copy()
        original_active = context.active_object

        exported_count = 0

        for frame in range(start_frame, end_frame + 1, self.frame_step):
            bpy.context.scene.frame_set(frame)

            for obj in original_selection:
                if self.export_mesh_only and obj.type not in {'MESH', 'CURVE', 'SURFACE', 'FONT', 'META'}:
                    continue

                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                context.view_layer.objects.active = obj

                original_type = obj.type

                if self.export_mesh_only and obj.type != 'MESH':
                    try:
                        bpy.ops.object.convert(target='MESH')
                    except:
                        continue

                bpy.ops.object.duplicate()
                temp_obj = context.active_object

                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                bpy.ops.object.convert(target='MESH')

                if len(original_selection) == 1:
                    filename = os.path.join(folder_path, f"{base_name}_{frame:04d}{ext}")
                else:
                    filename = os.path.join(folder_path, f"{base_name}_{obj.name}_{frame:04d}{ext}")

                filename = filename.replace("*", "").replace("?", "").replace('"', "").replace("<", "").replace(">", "").replace("|", "")

                try:
                    bpy.ops.wm.obj_export(
                        filepath=filename,
                        export_selected_objects=True,
                        export_uv=True,
                        export_normals=True,
                        export_materials=True,
                        export_colors=self.export_vertex_colors,
                    )
                    exported_count += 1
                except Exception as e:
                    print(f"Error exporting {obj.name} at frame {frame}: {str(e)}")
                    import traceback
                    traceback.print_exc()

                bpy.data.objects.remove(temp_obj, do_unlink=True)

                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                context.view_layer.objects.active = obj

                if self.export_mesh_only and original_type != 'MESH':
                    try:
                        bpy.ops.object.select_all(action='DESELECT')
                        obj.select_set(True)
                        context.view_layer.objects.active = obj
                        bpy.ops.object.convert(target=original_type)
                    except:
                        pass

        bpy.ops.object.select_all(action='DESELECT')
        for obj in original_selection:
            if obj:
                obj.select_set(True)

        if original_active:
            context.view_layer.objects.active = original_active

        if exported_count > 0:
            self.report({'INFO'}, f"Export completed: {exported_count} files to {folder_path}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No files exported")
            return {'CANCELLED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Frame Range:")
        row = layout.row(align=True)
        row.prop(self, "frame_start")
        row.prop(self, "frame_end")
        layout.prop(self, "frame_step")

        layout.separator()
        layout.label(text="Export Options:")
        layout.prop(self, "export_mesh_only")
        layout.prop(self, "export_vertex_colors")


def register():
    bpy.utils.register_class(ANIM_SEQ_OT_export_sequence)


def unregister():
    bpy.utils.unregister_class(ANIM_SEQ_OT_export_sequence)