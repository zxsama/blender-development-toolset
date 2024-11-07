import bpy
import os
from .bilingual_translator import (BilingualTranslatorData, 
                                   MZ_OT_GenerateBilingualTranslator, 
                                   MZ_OT_RegisterBilingualTranslator,
                                   MZ_OT_OpenBilingualBlackWhiteList,
                                   MZ_OT_DeleteBilingualTranslator,
                                    )
import bl_i18n_utils.settings as setting_lng


bar_button_sum = 5
class MZ_Preferences(bpy.types.AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    enable_bar_buttons: bpy.props.BoolVectorProperty(
        name="enable_bar_buttons",
        size=bar_button_sum,
        default=[False, True, False, True, True],
        description="是否开启按钮的bool数组",
    )
    
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

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False
        row = layout.row()
        row = row.split(factor=0.3)
        
        bar_button = context.scene.mz_bar_button
        box_btn_qucik = row.column(align=True)
        box_btn_qucik.box().label(text="快捷按键显示/关闭")
        sub_flow = box_btn_qucik.box().grid_flow(columns=1, align=True)
        for index, (_, value) in enumerate(bar_button.items()):
            sub_flow.prop(self, "enable_bar_buttons", index=index, text=value[0])
        sub_flow = box_btn_qucik.box().grid_flow(columns=1, align=True)
        sub_flow.label(text="语言切换项")
        sub_flow.use_property_split = True
        sub_flow.use_property_decorate = False
        sub_flow_row = sub_flow.row(align=True)
        sub_flow_row.prop(self, "switch_lang_slot1", text="")  
        sub_flow_row.prop(self, "switch_lang_slot2", text="")  
        sub_flow_row.prop(self, "switch_lang_slot3", text="")  
        
        
        bili_trans_prop = context.scene.mz_bilingual_translator_prop
        box_trans = row.column(align=True)
        box_trans.box().label(text="双语翻译")
        sub_flow = box_trans.grid_flow(columns=1, align=True)
        sub_flow.use_property_split = True
        sub_flow.use_property_decorate = False
        
        if BilingualTranslatorData().get_bilingual_init_state():            
            sub_box = sub_flow.box()
            sub_flow = sub_box.grid_flow(columns=1, align=True)
            sub_flow.prop(bili_trans_prop, "bilingual_lang", text="双语语言")
            sub_flow.prop(bili_trans_prop, "custom_delimiter", text="间隔符")
            
            sub_flow_row = sub_flow.row()
            sub_flow_row.prop(bili_trans_prop, "is_translation_preceding", text="合并方式", expand=True)
            
            sub_flow_row = sub_flow.row()
            sub_fr_row = sub_flow_row.row(heading="翻译区域", align=True)
            sub_fr_row.prop(bili_trans_prop, "translation_section_all", text="ALL", toggle=True)
            sub_fr_row.prop(bili_trans_prop, "translation_section_node", text="节点", toggle=True)
            sub_fr_row.prop(bili_trans_prop, "translation_section_node_property", text="节点属性", toggle=True)
            sub_fr_row.prop(bili_trans_prop, "translation_section_modifier", text="修改器", toggle=True)
            
            sub_flow_row = sub_flow.row()
            sub_fr_row = sub_flow_row.row(heading="", align=True)
            
            sub_fr_row = sub_fr_row.row()
            sub_fr_row.prop(bili_trans_prop, "translation_section_whitelist", text="白名单", toggle=True)
            whitelist = sub_fr_row.operator(MZ_OT_OpenBilingualBlackWhiteList.bl_idname, text="编辑")
            whitelist.list_type = True
            
            sub_fr_row = sub_fr_row.row().row(align=True)
            sub_fr_row.prop(bili_trans_prop, "translation_section_blacklist", text="黑名单", toggle=True)
            blacklist = sub_fr_row.operator(MZ_OT_OpenBilingualBlackWhiteList.bl_idname, text="编辑")
            blacklist.list_type = False
            
            sub_flow.separator()
            btn_flow = sub_flow.column(align=True)
            btn_flow.scale_y = 1.75
            btn_flow_row = btn_flow.row()
            btn_flow_row = btn_flow_row.split(factor=0.9, align=True)
            btn_flow_row.operator(MZ_OT_GenerateBilingualTranslator.bl_idname, text="编译双语翻译", icon="FILE_REFRESH")
            btn_flow_row.operator(MZ_OT_DeleteBilingualTranslator.bl_idname, text="", icon="TRASH")
        else:
            
            btn_flow = sub_flow.box()
            btn_flow.scale_y = 1.5
            btn_flow.operator(MZ_OT_RegisterBilingualTranslator.bl_idname, text="双语翻译初始化(自动重启)")
