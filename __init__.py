bl_info = {
    "name": "MZ Development Toolset",
    "author": "MIZI",
    "version": (0, 5, 5),
    "blender": (3, 3, 0),
    "location": "Right Topbar",
    "description": "快捷工具, 快速重启, 双语切换, 双语翻译",
    "wiki_url": "https://github.com/zxsama/blender-development-toolset",
    "doc_url": "https://github.com/zxsama/blender-development-toolset",
    "tracker_url": "https://github.com/zxsama/blender-development-toolset/issues",
    "category": "Development",
}

import os
import bpy
import bpy.utils.previews
from . import reg_classes as rc

MZ_CUSTOMICONS = None


def register():
    # class
    for cls in rc.all_classes:
        bpy.utils.register_class(cls)
    for cls in rc.bar_classes:
        bpy.types.TOPBAR_HT_upper_bar.prepend(cls.draw)

    bpy.types.Scene.mz_bilingual_translator_prop = bpy.props.PointerProperty(
        type=rc.MZ_BilingualTranslatorProps
    )
    bpy.types.Scene.mz_tool_bar_props = bpy.props.PointerProperty(
        type=rc.MZ_ToolBarProps
    )

    # custom icon
    global MZ_CUSTOMICONS
    MZ_CUSTOMICONS = bpy.utils.previews.new()
    icons_dir = os.path.join(os.path.dirname(__file__), "resource", "icons", "torbar")
    icons = os.listdir(icons_dir)
    for icon in icons:
        icon_name = os.path.splitext(icon)[0]
        MZ_CUSTOMICONS.load(icon_name, os.path.join(icons_dir, icon), "IMAGE")

    buildin_icons = bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items.items()
    icon_dict = {tup[1].identifier : tup[1].value for tup in buildin_icons}
    bar_button = {
        rc.UI_OT_ConsoleToggle.bl_idname: ["Console Pin to Top", icon_dict["CONSOLE"], ""],
        rc.UI_OT_RestartSavedBlender.bl_idname: ["Save and Restart Blender",MZ_CUSTOMICONS["SAVE_RE_BLENDER"].icon_id,""],
        rc.UI_OT_RestartBlender.bl_idname: ["Restart Fresh Blender", MZ_CUSTOMICONS["RE_BLENDER"].icon_id, ""],
        rc.UI_OT_OpenAddonPath.bl_idname: ["Open Addon Path", MZ_CUSTOMICONS["ADDON_FLODER"].icon_id, ""],
        rc.UI_OT_Switch_Language.bl_idname: ["Language Switch", icon_dict["WORDWRAP_ON"], ""],
    }
    bpy.types.Scene.mz_bar_button = bar_button

    # translate
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[__package__].preferences
    from .translations import translations
    import bl_i18n_utils.settings as setting_lng
    # 匹配双语语言, 暂时只有中文
    if addon_prefs.bilingual_lang_code_current == setting_lng.LANGUAGES[13][2]:
        translations["bilingual"] = translations[setting_lng.LANGUAGES[13][2]]
    bpy.app.translations.register(__name__, translations)
    

def unregister():

    bpy.app.translations.unregister(__name__)

    global MZ_CUSTOMICONS
    bpy.utils.previews.remove(MZ_CUSTOMICONS)

    for cls in rc.all_classes:
        bpy.utils.unregister_class(cls)
    for cls in rc.bar_classes:
        bpy.types.TOPBAR_HT_upper_bar.remove(cls.draw)

    del bpy.types.Scene.mz_bar_button
    del bpy.types.Scene.mz_bilingual_translator_prop
