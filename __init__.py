# -*- coding: UTF-8 -*-

bl_info = {
    "name": "Development Toolset",
    "author": "MIZI",
    "version": (0, 2, 0),
    "blender": (3, 2, 1),
    "location": "right topbar",
    "description": "开发用快捷按钮",
    "wiki_url": "https://github.com/zxsama/blender-development-toolset",
    "doc_url": "https://github.com/zxsama/blender-development-toolset",
	"tracker_url": "https://github.com/zxsama/blender-development-toolset/issues",
    "warning": "仅限windows平台, 依赖于psutil, pywin32库. 第一次点击涉及相关功能的按钮会自动安装, 需重启生效.",
    "category": "Development",
}

import bpy
from .lib import addon_updater_ops
from . import reg_classes as rc

"""
class DemoPreferences(bpy.types.AddonPreferences):
    /"/"/"Demo bare-bones preferences/"/"/"
    bl_idname = __package__

    # Addon updater preferences.

    auto_check_update = bpy.props.BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=False)

    updater_interval_months = bpy.props.IntProperty(
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0)

    updater_interval_days = bpy.props.IntProperty(
        name='Days',
        description="Number of days between checking for updates",
        default=7,
        min=0,
        max=31)

    updater_interval_hours = bpy.props.IntProperty(
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23)

    updater_interval_minutes = bpy.props.IntProperty(
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59)

    def draw(self, context):
        layout = self.layout

        # Works best if a column, or even just self.layout.
        mainrow = layout.row()
        col = mainrow.column()

        # Updater draw function, could also pass in col as third arg.
        addon_updater_ops.update_settings_ui(self, context)

        # Alternate draw function, which is more condensed and can be
        # placed within an existing draw function. Only contains:
        #   1) check for update/update now buttons
        #   2) toggle for auto-check (interval will be equal to what is set above)
        # addon_updater_ops.update_settings_ui_condensed(self, context, col)

        # Adding another column to help show the above condensed ui as one column
        # col = mainrow.column()
        # col.scale_y = 2
        # ops = col.operator("wm.url_open","Open webpage ")
        # ops.url=addon_updater_ops.updater.website
"""

def register():
    addon_updater_ops.register(bl_info)
    for cls in rc.all_classes:
        bpy.utils.register_class(cls)
    for cls in rc.bar_classes:    
        bpy.types.TOPBAR_HT_upper_bar.prepend(cls.draw)
    
    bpy.types.Scene.mz_custom_prop = bpy.props.PointerProperty(type = rc.MZ_CustomProps)
    
    # addon_updater_ops.make_annotations(DemoPreferences)
    # bpy.utils.register_class(DemoPreferences)   


def unregister():
    addon_updater_ops.unregister()
    for cls in rc.all_classes:
        bpy.utils.unregister_class(cls)
    for cls in rc.bar_classes:  
        bpy.types.TOPBAR_HT_upper_bar.remove(cls.draw)
    # bpy.utils.unregister_class(DemoPreferences)   
    
    del bpy.types.Scene.dev_prop