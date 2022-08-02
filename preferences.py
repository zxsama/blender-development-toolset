import bpy
import os
from .tool_bar import bar_button

class MZ_Preferences(bpy.types.AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = os.path.basename(os.path.dirname(__file__))

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False
        col = layout.column(align=True)
        box = col.box()
        box.label(text="开启的快捷按键:")
        sub_flow = box.grid_flow(columns=2, align=True)
        scene = context.scene
        custom_prop = scene.mz_custom_prop
        for index, (key, value) in enumerate(bar_button.items()):
            sub_flow.prop(custom_prop, "enable_bar_buttons", index=index, text=value)
            