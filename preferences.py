import bpy
import os
from .tool_bar import BarUI

bar_button = BarUI.get_bar_data()


class MZ_Preferences(bpy.types.AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = os.path.basename(os.path.dirname(__file__))

    enable_bar_buttons: bpy.props.BoolVectorProperty(
        name="enable_bar_buttons",
        size=len(bar_button),
        default=[True] * len(bar_button),
        description="是否开启按钮的bool数组",
        # update=update_bar_ops,
    )

    def update_bar_ops(self, context):
        for index, (_, _) in enumerate(bar_button.items()):
            if not self.enable_bar_buttons[index]:
                ...
                # TODO: unregist class

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False
        col = layout.column(align=True)
        box = col.box()
        box.label(text="开启的快捷按键:")
        sub_flow = box.grid_flow(columns=2, align=True)
        for index, (_, value) in enumerate(bar_button.items()):
            sub_flow.prop(self, "enable_bar_buttons", index=index, text=value[0])
