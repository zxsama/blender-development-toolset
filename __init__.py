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

    bpy.types.Scene.mz_custom_prop = bpy.props.PointerProperty(type=rc.MZ_CustomProps)
    bpy.types.Scene.mz_bilingual_translator_prop = bpy.props.PointerProperty(
        type=rc.MZ_BilingualTranslatorProps
    )

    # custom icon
    global MZ_CUSTOMICONS
    MZ_CUSTOMICONS = bpy.utils.previews.new()
    icons_dir = os.path.join(os.path.dirname(__file__), "icons", "torbar")
    icons = os.listdir(icons_dir)
    for icon in icons:
        icon_name = os.path.splitext(icon)[0]
        MZ_CUSTOMICONS.load(icon_name, os.path.join(icons_dir, icon), "IMAGE")

    buildin_icons = bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items.items()
    icon_dict = {tup[1].identifier : tup[1].value for tup in buildin_icons}
    bar_button = {
        rc.UI_OT_ConsoleToggle.bl_idname: ["控制台置顶", icon_dict["CONSOLE"], ""],
        rc.UI_OT_RestartSavedBlender.bl_idname: ["保存并重启blender",MZ_CUSTOMICONS["SAVE_RE_BLENDER"].icon_id,""],
        rc.UI_OT_RestartBlender.bl_idname: ["重启全新blender", MZ_CUSTOMICONS["RE_BLENDER"].icon_id, ""],
        rc.UI_OT_OpenAddonPath.bl_idname: ["打开插件路径", MZ_CUSTOMICONS["ADDON_FLODER"].icon_id, ""],
        rc.UI_OT_Switch_ZH_EN.bl_idname: ["中英切换", icon_dict["WORDWRAP_ON"], ""],
    }
    bpy.types.Scene.mz_bar_button = bar_button


def unregister():

    global MZ_CUSTOMICONS
    bpy.utils.previews.remove(MZ_CUSTOMICONS)

    for cls in rc.all_classes:
        bpy.utils.unregister_class(cls)
    for cls in rc.bar_classes:
        bpy.types.TOPBAR_HT_upper_bar.remove(cls.draw)

    del bpy.types.Scene.mz_bar_button
    del bpy.types.Scene.mz_custom_prop
    del bpy.types.Scene.mz_bilingual_translator_prop
