# -*- coding: UTF-8 -*-

bl_info = {
    "name": "Development Toolset",
    "author": "MIZI",
    "version": (0, 5, 0),
    "blender": (4, 2, 0),
    "location": "right topbar",
    "description": "开发用快捷工具",
    "wiki_url": "https://github.com/zxsama/blender-development-toolset",
    "doc_url": "https://github.com/zxsama/blender-development-toolset",
    "tracker_url": "https://github.com/zxsama/blender-development-toolset/issues",
    "warning": "仅限windows平台, 依赖于pywin32库. 第一次点击涉及相关功能的按钮会自动安装, 需重启生效.",
    "category": "Development",
}

import bpy
from . import reg_classes as rc


def register():
    # class
    for cls in rc.all_classes:
        bpy.utils.register_class(cls)
    for cls in rc.bar_classes:
        bpy.types.TOPBAR_HT_upper_bar.prepend(cls.draw)

    bpy.types.Scene.mz_custom_prop = bpy.props.PointerProperty(type=rc.MZ_CustomProps)
    bpy.types.Scene.mz_bilingual_translator_prop = bpy.props.PointerProperty(type=rc.MZ_BilingualTranslatorProps)


def unregister():
    from .tool_bar import unregister as tb_unregister
    from .bilingual_translator import unregister as bt_unregister
    tb_unregister()
    bt_unregister()

    for cls in rc.all_classes:
        bpy.utils.unregister_class(cls)
    for cls in rc.bar_classes:
        bpy.types.TOPBAR_HT_upper_bar.remove(cls.draw)

    del bpy.types.Scene.mz_custom_prop
    del bpy.types.Scene.mz_bilingual_translator_prop
