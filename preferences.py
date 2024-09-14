import bpy
import os
from .bilingual_translator import (BilingualTranslatorData, 
                                   MZ_OT_GenerateBilingualTranslator, 
                                   MZ_OT_RegisterBilingualTranslator,
                                   MZ_OT_OpenBilingualWhiteList,
                                   MZ_OT_DeleteBilingualTranslator,
                                    )


bar_button_sum = 5
class MZ_Preferences(bpy.types.AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    enable_bar_buttons: bpy.props.BoolVectorProperty(
        name="enable_bar_buttons",
        size=bar_button_sum,
        default=[True] * bar_button_sum,
        description="是否开启按钮的bool数组",
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False
        row = layout.row()
        row = row.split(factor=0.3)
        
        bar_button = context.scene.mz_bar_button
        box_btn_qucik = row.column(align=True)
        box_btn_qucik.box().label(text="快捷按键开关")
        sub_flow = box_btn_qucik.box().grid_flow(columns=1, align=True)
        for index, (_, value) in enumerate(bar_button.items()):
            sub_flow.prop(self, "enable_bar_buttons", index=index, text=value[0])
        
        bili_trans_prop = context.scene.mz_bilingual_translator_prop
        box_trans = row.column(align=True)
        box_trans.box().label(text="双语翻译")
        sub_flow = box_trans.grid_flow(columns=1, align=True)
        sub_flow.use_property_split = True
        sub_flow.use_property_decorate = False
        
        bil_mo_folder, _ = BilingualTranslatorData().get_bilingual_mo_path()
        if os.path.exists(bil_mo_folder):            
            sub_box = sub_flow.box()
            sub_flow = sub_box.grid_flow(columns=1, align=True)
            sub_flow.prop(bili_trans_prop, "bilingual_lang", text="双语语言")
            sub_flow.prop(bili_trans_prop, "custom_delimiter", text="间隔符")
            sub_row = sub_flow.row()
            sub_row.prop(bili_trans_prop, "is_translation_preceding", text="合并方式", expand=True)
            sub_row = sub_flow.row()
            
            sub_col = sub_row.row(heading="翻译区域", align=True)
            sub_col.prop(bili_trans_prop, "translation_section_all", text="ALL")
            sub_col.prop(bili_trans_prop, "translation_section_node", text="节点")
            sub_col.prop(bili_trans_prop, "translation_section_node_property", text="节点属性")
            sub_col.prop(bili_trans_prop, "translation_section_modifier", text="修改器")
            sub_col.prop(bili_trans_prop, "translation_section_white_list", text="白名单")
            sub_col.operator(MZ_OT_OpenBilingualWhiteList.bl_idname, text="编辑白名单")
            
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
