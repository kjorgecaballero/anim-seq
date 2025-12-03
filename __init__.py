bl_info = {
    "name": "anim_sequence_io",
    "author": "Siruka",
    "version": (0, 0, 1),  
    "blender": (4, 0, 0),
    "location": "File > Import",
    "description": "Import mesh sequences (FBX/OBJ) as shapekeys with animation",
    "warning": "Early alpha version - API may change",
    "category": "Import-Export",
}

import bpy
from bpy.types import AddonPreferences
from bpy.props import BoolProperty, IntProperty

from . import addon_updater_ops
from . import operators, ui, utils


# UPDATE PREFERENCES
class AnimSequenceIO_UpdatePreferences(AddonPreferences):
    """Addon update preferences"""
    bl_idname = __package__

    # Auto-update settings
    auto_check_update: BoolProperty(
        name="Auto-check for updates",
        description="If enabled, automatically check for updates on startup",
        default=False,
    )

    updater_interval_months: IntProperty(
        name='Months',
        description="Months between update checks",
        default=0,
        min=0
    )
    updater_interval_days: IntProperty(
        name='Days',
        description="Days between update checks",
        default=1,
        min=0,
    )
    updater_interval_hours: IntProperty(
        name='Hours',
        description="Hours between update checks",
        default=0,
        min=0,
        max=23
    )
    updater_interval_minutes: IntProperty(
        name='Minutes',
        description="Minutes between update checks",
        default=0,
        min=0,
        max=59
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Update Settings:")
        addon_updater_ops.update_settings_ui(self, context, layout)


# REGISTRATION

def register():
    """Register all modules with updater integration"""
    

    addon_updater_ops.register(bl_info)
    

    bpy.utils.register_class(AnimSequenceIO_UpdatePreferences)
    

    operators.register()
    ui.register()


def unregister():
    """Unregister all modules"""
  
    ui.unregister()
    operators.unregister()
    

    bpy.utils.unregister_class(AnimSequenceIO_UpdatePreferences)
    

    addon_updater_ops.unregister()


if __name__ == "__main__":
    register()