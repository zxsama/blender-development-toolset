import bpy
import bl_i18n_utils.settings as setting_lng
from .bilingual_translator import BilingualTranslatorData


class MZ_ToolBarProps(bpy.types.PropertyGroup):
    def get_lang_items_callback(self, context):
        # ["0:无", "1:双语", LANGUAGES]
        languages = list(setting_lng.LANGUAGES)
        BTD = BilingualTranslatorData()
        languages = [(str(i[0] + 2), i[1], i[2]) for i in languages]
        if BTD.get_bilingual_compile_state():
            bilingual = ("1", BTD.menu_name, BTD.locale_name)
        else:
            bilingual = ("1", "[PlaceHolder]", languages[1][2])
        languages.insert(0, bilingual)
        default = ("0", "无", "")
        languages.insert(0, default)
        return languages

    switch_lang_slot1: bpy.props.EnumProperty(
        items=[(str(i[0]), i[1], i[2]) for i in setting_lng.LANGUAGES],
        name="语言切换1",
        default=1,
    )

    switch_lang_slot2: bpy.props.EnumProperty(
        items=get_lang_items_callback,
        name="语言切换2",
        default=15,  # 13 offset 2
    )

    switch_lang_slot3: bpy.props.EnumProperty(
        items=get_lang_items_callback,
        name="语言切换3",
        default=0,
    )


class MZ_BilingualTranslatorProps(bpy.types.PropertyGroup):
    bilingual_lang: bpy.props.EnumProperty(
        items=[(str(i[0]), i[1], i[2]) for i in setting_lng.LANGUAGES],
        name="双语语言",
        default=13,
    )

    custom_delimiter: bpy.props.StringProperty(
        name="custom_delimiter",
        description="双语翻译中间的间隔符号",
        default=" | ",
    )

    is_translation_preceding: bpy.props.EnumProperty(
        items=[
            ("0", "译文在前", "translation_preceding"),
            ("1", "译文在后", "translation_following"),
        ],
        name="is_translation_preceding",
        description="译文在原文前面或者后面",
        default=1,
    )

    translation_section_all: bpy.props.BoolProperty(
        name="translation_section_all",
        default=True,
        description="翻译区域-All",
    )

    translation_section_node: bpy.props.BoolProperty(
        name="translation_section_node",
        default=True,
        description="翻译区域-node",
    )

    translation_section_node_property: bpy.props.BoolProperty(
        name="translation_section_node_property",
        default=True,
        description="翻译区域-node property",
    )

    translation_section_modifier: bpy.props.BoolProperty(
        name="translation_section_modifier",
        default=True,
        description="翻译区域-modifier",
    )

    translation_section_whitelist: bpy.props.BoolProperty(
        name="translation_section_whitelist",
        default=True,
        description="翻译区域-whitelist",
    )

    translation_section_blacklist: bpy.props.BoolProperty(
        name="translation_section_blacklist",
        default=False,
        description="翻译区域-blacklist",
    )
