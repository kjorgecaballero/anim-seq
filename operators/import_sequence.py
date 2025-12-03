import bpy
from pathlib import Path
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    StringProperty,
    EnumProperty,
)
from bpy_extras.io_utils import ImportHelper

from ..utils.mesh_utils import extract_number, import_mesh_file


class ANIM_SEQ_OT_import_sequence(bpy.types.Operator, ImportHelper):
    """Import a mesh sequence (FBX/OBJ) as shapekeys or separate objects"""
    
    bl_idname = "import_scene.meshseq"
    bl_label = "Import Mesh Sequence"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".*"
    filter_glob: StringProperty(default="*.fbx;*.obj", options={"HIDDEN"})

    files: CollectionProperty(
        name="File Path",
        description="Files to import the sequence",
        type=bpy.types.OperatorFileListElement,
    )
    directory: StringProperty()

    create_collection: BoolProperty(
        name="Create Collection",
        description="Organize objects in a separate collection",
        default=True,
    )
    
    collection_name: StringProperty(
        name="Collection Name",
        description="Name for the collection",
        default="Mesh_Sequence",
    )
    
    collection_color: EnumProperty(
        name="Collection Color",
        description="Color to identify the collection",
        items=[
            ('NONE', "None", "No color"),
            ('COLOR_01', "Red", "Red color"),
            ('COLOR_02', "Orange", "Orange color"),
            ('COLOR_03', "Yellow", "Yellow color"),
            ('COLOR_04', "Green", "Green color"),
            ('COLOR_05', "Blue", "Blue color"),
            ('COLOR_06', "Violet", "Violet color"),
            ('COLOR_07', "Pink", "Pink color"),
            ('COLOR_08', "Brown", "Brown color"),
        ],
        default='COLOR_01',
    )

    import_method: EnumProperty(
        name="Import Method",
        description="How to import the sequence",
        items=[
            ('SHAPEKEYS', "ShapeKeys", "Import as ShapeKeys in a single object (no vertex colors)"),
            ('SEPARATE', "Separate Objects", "Import each frame as separate object (with vertex colors)"),
        ],
        default='SHAPEKEYS',
    )

    relative_shapekey: BoolProperty(
        name="Relative ShapeKeys",
        description="Import shapekeys as relative",
        default=True,
    )

    def draw(self, context):
        layout = self.layout
        
        # Collection options at the top
        layout.prop(self, "create_collection")
        
        if self.create_collection:
            col = layout.column()
            col.prop(self, "collection_name")
            col.prop(self, "collection_color")
        
        # Import method
        layout.separator()
        layout.prop(self, "import_method")
        
        if self.import_method == 'SHAPEKEYS':
            layout.prop(self, "relative_shapekey")

    def execute(self, context):
        filepaths = [Path(self.directory, f.name) for f in self.files]
        if not filepaths:
            filepaths.append(Path(self.directory, self.filename))

        filepaths.sort(key=extract_number)
        
        # Create collection if enabled
        collection = None
        if self.create_collection:
            collection = self.create_sequence_collection(context)
        
        if self.import_method == 'SEPARATE':
            return self.import_as_separate_objects(filepaths, collection, context)
        else:
            return self.create_shapekeys(filepaths, collection, context)

    def create_sequence_collection(self, context):
        """Create a collection to organize the sequence"""
        collection_name = self.collection_name
        
        # If it already exists, add a number
        original_name = collection_name
        counter = 1
        while collection_name in bpy.data.collections:
            collection_name = f"{original_name}_{counter:03d}"
            counter += 1
        
        # Create new collection
        collection = bpy.data.collections.new(collection_name)
        
        # Add color to the collection
        if self.collection_color != 'NONE':
            collection.color_tag = self.collection_color
        
        # Add collection to the scene
        context.scene.collection.children.link(collection)
        
        return collection

    def create_shapekeys(self, filepaths, collection=None, context=None):
        """Original method for shapekeys (no vertex colors)"""
        if not filepaths:
            self.report({'ERROR'}, "No files selected")
            return {"CANCELLED"}

        # Import first file
        main_obj = import_mesh_file(filepaths[0])
        if not main_obj:
            self.report({'ERROR'}, f"Failed to import {filepaths[0]}")
            return {"CANCELLED"}

        main_obj.location = (0, 0, 0)
        main_obj.rotation_euler = (1.5708, 0, 0)

        # Move to collection if it exists
        if collection:
            self.move_to_collection(main_obj, collection, context)
            main_obj.name = f"{self.collection_name}_Base"

        if not main_obj.data.shape_keys:
            main_obj.shape_key_add(name="Basis")

        # Import the rest as shapekeys
        for filepath in filepaths[1:]:
            current_obj = import_mesh_file(filepath)
            if not current_obj:
                continue
                
            current_obj.location = (0, 0, 0)
            current_obj.rotation_euler = (1.5708, 0, 0)

            context.view_layer.objects.active = main_obj
            bpy.ops.object.join_shapes()
            bpy.data.objects.remove(current_obj, do_unlink=True)

        # Count shapekeys (excluding Basis)
        shapekey_count = len(main_obj.data.shape_keys.key_blocks) - 1
        
        # Name shapekeys according to the frame
        for i, key_block in enumerate(main_obj.data.shape_keys.key_blocks):
            if key_block.name == "Basis":
                continue
            key_block.name = f"Frame_{i:04d}"

        # Animate shapekeys
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

        # Configure timeline
        context.scene.frame_start = 0
        context.scene.frame_end = max(shapekey_count, 1)

        self.report({'INFO'}, f"Imported {len(filepaths)} frames as ShapeKeys")
        return {"FINISHED"}

    def import_as_separate_objects(self, filepaths, collection=None, context=None):
        """Import each frame as separate object with visibility animation"""
        if not filepaths:
            self.report({'ERROR'}, "No files selected")
            return {"CANCELLED"}

        objects = []
        for i, filepath in enumerate(filepaths):
            obj = import_mesh_file(filepath)
            if obj:
                obj.location = (0, 0, 0)
                obj.rotation_euler = (1.5708, 0, 0)
                obj.name = f"Frame_{i:04d}"
                
                # Move to collection if it exists
                if collection:
                    self.move_to_collection(obj, collection, context)
                
                objects.append(obj)
                
                # Animate visibility
                obj.hide_viewport = True
                obj.hide_render = True
                obj.keyframe_insert("hide_viewport", frame=0)
                obj.keyframe_insert("hide_render", frame=0)
                
                # Show in current frame
                obj.hide_viewport = False
                obj.hide_render = False
                obj.keyframe_insert("hide_viewport", frame=i)
                obj.keyframe_insert("hide_render", frame=i)
                
                # Hide in next frame
                obj.hide_viewport = True
                obj.hide_render = True
                obj.keyframe_insert("hide_viewport", frame=i+1)
                obj.keyframe_insert("hide_render", frame=i+1)

        # Configure timeline
        context.scene.frame_start = 0
        context.scene.frame_end = len(objects) - 1

        self.report({'INFO'}, f"Imported {len(objects)} frames as separate objects")
        return {"FINISHED"}

    def move_to_collection(self, obj, collection, context):
        """Move an object to a specific collection"""
        # Remove from all current collections
        for coll in obj.users_collection:
            coll.objects.unlink(obj)
        
        # Add to the new collection
        collection.objects.link(obj)


def register():
    bpy.utils.register_class(ANIM_SEQ_OT_import_sequence)


def unregister():
    bpy.utils.unregister_class(ANIM_SEQ_OT_import_sequence)