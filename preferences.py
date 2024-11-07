import bpy
import os
from .bilingual_translator import (BilingualTranslatorData, 
                                   MZ_OT_GenerateBilingualTranslator, 
                                   MZ_OT_RegisterBilingualTranslator,
                                   MZ_OT_OpenBilingualBlackWhiteList,
                                   MZ_OT_DeleteBilingualTranslator,
                                    )
import bl_i18n_utils.settings as setting_lng
import bpy.app.translations as trs

bar_button_sum = 5
class MZ_Preferences(bpy.types.AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    # tor_bar
    enable_bar_buttons: bpy.props.BoolVectorProperty(
        name="enable_bar_buttons",
        size=bar_button_sum,
        default=[False, True, False, True, True],
        description="Boolean array for enabling buttons",
    )
    
    # 双语翻译
    bilingual_lang: bpy.props.EnumProperty(
        items=[(str(i[0]), i[1], i[2]) for i in setting_lng.LANGUAGES],
        name="Bilingual Language",
        default=13,
    )

    custom_delimiter: bpy.props.StringProperty(
        name="custom_delimiter",
        description="Separator symbol in bilingual translation",
        default=" | ",
    )

    is_translation_preceding: bpy.props.EnumProperty(
        items=[
            ("0", trs.pgettext_data("Translation First"), "translation_preceding"),
            ("1", trs.pgettext_data("Translation Last"), "translation_following"),
        ],
        name="is_translation_preceding",
        description="Translation before or after the original text",
        default=1,
    )

    translation_section_all: bpy.props.BoolProperty(
        name="translation_section_all",
        default=True,
        description="Translation area - All",
    )

    translation_section_node: bpy.props.BoolProperty(
        name="translation_section_node",
        default=True,
        description="Translation area - Node",
    )

    translation_section_node_property: bpy.props.BoolProperty(
        name="translation_section_node_property",
        default=True,
        description="Translation area - Node Property",
    )

    translation_section_modifier: bpy.props.BoolProperty(
        name="translation_section_modifier",
        default=True,
        description="Translation area - Modifier",
    )

    translation_section_whitelist: bpy.props.BoolProperty(
        name="translation_section_whitelist",
        default=True,
        description="Translation area - Whitelist",
    )

    translation_section_blacklist: bpy.props.BoolProperty(
        name="translation_section_blacklist",
        default=False,
        description="Translation area - Blacklist",
    )
    
    bilingual_lang_code_current: bpy.props.StringProperty(
        name="bilingual_lang_code_current",
        description="bilingual lang code current",
        default="",
    )
    
    # 语言切换
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
        default = ("0", "None", "")
        languages.insert(0, default)
        return languages

    switch_lang_slot1: bpy.props.EnumProperty(
        items=[(str(i[0]), i[1], i[2]) for i in setting_lng.LANGUAGES],
        name="Language Switch 1",
        default=1,
    )

    switch_lang_slot2: bpy.props.EnumProperty(
        items=get_lang_items_callback,
        name="Language Switch 2",
        default=15,  # 13 offset 2
    )

    switch_lang_slot3: bpy.props.EnumProperty(
        items=get_lang_items_callback,
        name="Language Switch 3",
        default=0,
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False
        row = layout.row()
        row = row.split(factor=0.3)
        
        bar_button = context.scene.mz_bar_button
        box_btn_qucik = row.column(align=True)
        box_btn_qucik.box().label(text="Show/Hide Shortcut Keys")
        sub_flow = box_btn_qucik.box().grid_flow(columns=1, align=True)
        for index, (_, value) in enumerate(bar_button.items()):
            sub_flow.prop(self, "enable_bar_buttons", index=index, text=value[0])
        sub_flow = box_btn_qucik.box().grid_flow(columns=1, align=True)
        sub_flow.label(text="Language Switch Option")
        sub_flow.use_property_split = True
        sub_flow.use_property_decorate = False
        sub_flow_row = sub_flow.row(align=True)
        sub_flow_row.prop(self, "switch_lang_slot1", text="")  
        sub_flow_row.prop(self, "switch_lang_slot2", text="")  
        sub_flow_row.prop(self, "switch_lang_slot3", text="")  
        
        box_trans = row.column(align=True)
        box_trans.box().label(text="Bilingual Translation")
        sub_flow = box_trans.grid_flow(columns=1, align=True)
        sub_flow.use_property_split = True
        sub_flow.use_property_decorate = False
        
        if BilingualTranslatorData().get_bilingual_init_state():            
            sub_box = sub_flow.box()
            sub_flow = sub_box.grid_flow(columns=1, align=True)
            sub_flow.prop(self, "bilingual_lang", text="Bilingual Language")
            sub_flow.prop(self, "custom_delimiter", text="Separator")
            
            sub_flow_row = sub_flow.row()
            sub_flow_row.prop(self, "is_translation_preceding", text="Merge Method", expand=True)
            
            sub_flow_row = sub_flow.row()
            sub_fr_row = sub_flow_row.row(heading="Translation Area", align=True)
            sub_fr_row.prop(self, "translation_section_all", text="ALL", toggle=True)
            sub_fr_row.prop(self, "translation_section_node", text="Node", toggle=True)
            sub_fr_row.prop(self, "translation_section_node_property", text="Node Property", toggle=True)
            sub_fr_row.prop(self, "translation_section_modifier", text="Modifier", toggle=True)
            
            sub_flow_row = sub_flow.row()
            sub_fr_row = sub_flow_row.row(heading="", align=True)
            
            sub_fr_row = sub_fr_row.row()
            sub_fr_row.prop(self, "translation_section_whitelist", text="Whitelist", toggle=True)
            whitelist = sub_fr_row.operator(MZ_OT_OpenBilingualBlackWhiteList.bl_idname, text="Edit")
            whitelist.list_type = True
            
            sub_fr_row = sub_fr_row.row().row(align=True)
            sub_fr_row.prop(self, "translation_section_blacklist", text="Blacklist", toggle=True)
            blacklist = sub_fr_row.operator(MZ_OT_OpenBilingualBlackWhiteList.bl_idname, text="Edit")
            blacklist.list_type = False
            
            sub_flow.separator()
            btn_flow = sub_flow.column(align=True)
            btn_flow.scale_y = 1.75
            btn_flow_row = btn_flow.row()
            btn_flow_row = btn_flow_row.split(factor=0.9, align=True)
            btn_flow_row.operator(MZ_OT_GenerateBilingualTranslator.bl_idname, text="Compile Bilingual Translation", icon="FILE_REFRESH")
            btn_flow_row.operator(MZ_OT_DeleteBilingualTranslator.bl_idname, text="", icon="TRASH")
        else:
            
            btn_flow = sub_flow.box()
            btn_flow.scale_y = 1.5
            btn_flow.operator(MZ_OT_RegisterBilingualTranslator.bl_idname, text="Bilingual Translation Initialization (Auto Restart)")
