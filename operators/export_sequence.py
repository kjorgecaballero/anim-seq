import bpy
import os
from bpy_extras.io_utils import ExportHelper
from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    EnumProperty,
    FloatProperty,
)


class ANIM_SEQ_OT_export_sequence(bpy.types.Operator, ExportHelper):
    """Export mesh sequence (FBX/OBJ) for each frame"""
    
    bl_idname = "export_scene.meshseq"
    bl_label = "Export Mesh Sequence"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".fbx"
    filter_glob: StringProperty(
        default="*.fbx;*.obj",
        options={'HIDDEN'},
    )

    # File format selection
    file_format: EnumProperty(
        name="Format",
        description="File format to export",
        items=(
            ('FBX', "FBX", "Export as FBX"),
            ('OBJ', "OBJ", "Export as OBJ"),
        ),
        default='FBX',
    )

    # Frame range
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

    # Step option
    frame_step: IntProperty(
        name="Frame Step",
        description="Export every X frames",
        default=1,
        min=1,
    )

    # Export options
    export_mesh_only: BoolProperty(
        name="Mesh Only",
        description="Export only mesh without bones",
        default=True,
    )

    apply_modifiers: BoolProperty(
        name="Apply Modifiers",
        description="Apply all modifiers before export",
        default=True,
    )

    # Vertex colors option (only for OBJ format)
    export_vertex_colors: BoolProperty(
        name="Vertex Colors",
        description="Export vertex colors in OBJ files (Blender 3.3+)",
        default=True,
    )

    def invoke(self, context, event):
        # Set default frame range from scene
        self.frame_start = context.scene.frame_start
        self.frame_end = context.scene.frame_end
        
        # Set default filename
        if context.active_object:
            self.filepath = context.active_object.name + "_sequence"
        else:
            self.filepath = "sequence"
            
        return super().invoke(context, event)

    def execute(self, context):
        # Get the selected folder
        folder_path = self.filepath
        
        # If it's a file path, get the directory
        if os.path.isfile(folder_path) or '.' in os.path.basename(folder_path):
            folder_path = os.path.dirname(folder_path)
        
        # Create directory if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        # Determine extension based on format
        ext = ".fbx" if self.file_format == 'FBX' else ".obj"
        
        # Get base name from filepath or use default
        if self.filepath and self.filepath != "":
            # Remove extension if present
            base_name = os.path.basename(self.filepath)
            if '.' in base_name:
                base_name = os.path.splitext(base_name)[0]
        else:
            base_name = "frame"
        
        # Configure animation frames
        start_frame = self.frame_start
        end_frame = self.frame_end
        
        # Switch to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Store original selection
        original_selection = context.selected_objects.copy()
        original_active = context.active_object
        
        exported_count = 0
        
        # Iterate over all animation frames
        for frame in range(start_frame, end_frame + 1, self.frame_step):
            # Set current frame
            bpy.context.scene.frame_set(frame)
            
            # For each selected object
            for obj in original_selection:
                # Skip non-mesh objects if mesh only is enabled
                if self.export_mesh_only and obj.type not in {'MESH', 'CURVE', 'SURFACE', 'FONT', 'META'}:
                    continue
                
                # Select only this object
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                context.view_layer.objects.active = obj
                
                # Store original type for reversion
                original_type = obj.type
                
                # Convert to mesh if needed
                if self.export_mesh_only and obj.type != 'MESH':
                    try:
                        bpy.ops.object.convert(target='MESH')
                    except:
                        continue
                
                # CRÍTICO: Crear una copia temporal del objeto para exportar
                # Esto evita modificar el objeto original
                bpy.ops.object.duplicate()
                temp_obj = context.active_object
                
                # Aplicar todas las transformaciones a la copia
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                
                # Aplicar modificadores si está habilitado
                if self.apply_modifiers:
                    bpy.ops.object.convert(target='MESH')
                
                # Create unique filename for FBX/OBJ
                if len(original_selection) == 1:
                    filename = os.path.join(folder_path, f"{base_name}_{frame:04d}{ext}")
                else:
                    filename = os.path.join(folder_path, f"{base_name}_{obj.name}_{frame:04d}{ext}")
                
                # Remove invalid characters from filename
                filename = filename.replace("*", "").replace("?", "").replace('"', "").replace("<", "").replace(">", "").replace("|", "")
                
                # Export based on format
                try:
                    if self.file_format == 'FBX':
                        # Exportar FBX SIN animación horneada y SIN transformaciones embebidas
                        bpy.ops.export_scene.fbx(
                            filepath=filename,
                            use_selection=True,
                            apply_unit_scale=True,
                            axis_forward='-Z',
                            axis_up='Y',
                            use_mesh_modifiers=False,  # Ya aplicamos modificadores antes
                            bake_anim=False,  # CRÍTICO: No hornear animación
                            bake_anim_use_all_bones=False,
                            bake_anim_use_nla_strips=False,
                            bake_anim_use_all_actions=False,
                            bake_anim_force_startend_keying=True,
                            apply_scale_options='FBX_SCALE_NONE',
                            object_types={'MESH'},  # Solo exportar malla
                            mesh_smooth_type='FACE',
                            add_leaf_bones=False,  # Evitar huesos hoja vacíos
                            use_armature_deform_only=True,
                            primary_bone_axis='Y',
                            secondary_bone_axis='X',
                            use_space_transform=True,  # Exportar sin transformaciones de espacio
                            global_scale=1.0,  # Escala 1:1
                            use_custom_props=False  # No exportar propiedades personalizadas
                        )
                    else:  # OBJ
                        # Exportar OBJ CON soporte de colores de vértice
                        bpy.ops.wm.obj_export(
                            filepath=filename,
                            export_selected_objects=True,
                            export_uv=True,
                            export_normals=True,
                            export_materials=True,
                            export_colors=self.export_vertex_colors,  # ¡NUEVO: Exportar colores de vértice!
                        )
                    
                    exported_count += 1
                    
                except Exception as e:
                    print(f"Error exporting {obj.name} at frame {frame}: {str(e)}")
                    import traceback
                    traceback.print_exc()
                
                # Eliminar el objeto temporal
                bpy.data.objects.remove(temp_obj, do_unlink=True)
                
                # Restaurar selección original
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                context.view_layer.objects.active = obj
                
                # Revert conversion if applied
                if self.export_mesh_only and original_type != 'MESH':
                    try:
                        bpy.ops.object.select_all(action='DESELECT')
                        obj.select_set(True)
                        context.view_layer.objects.active = obj
                        bpy.ops.object.convert(target=original_type)
                    except:
                        pass
        
        # Restore original selection
        bpy.ops.object.select_all(action='DESELECT')
        for obj in original_selection:
            if obj:  # Check if object still exists
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
        
        # File format
        layout.label(text="File Format:")
        layout.prop(self, "file_format", expand=True)
        
        # Frame range
        layout.separator()
        layout.label(text="Frame Range:")
        row = layout.row(align=True)
        row.prop(self, "frame_start")
        row.prop(self, "frame_end")
        layout.prop(self, "frame_step")
        
        # Export options
        layout.separator()
        layout.label(text="Export Options:")
        layout.prop(self, "export_mesh_only")
        layout.prop(self, "apply_modifiers")
        
        # Vertex colors option (only for OBJ format)
        if self.file_format == 'OBJ':
            layout.prop(self, "export_vertex_colors")


def register():
    bpy.utils.register_class(ANIM_SEQ_OT_export_sequence)


def unregister():
    bpy.utils.unregister_class(ANIM_SEQ_OT_export_sequence)