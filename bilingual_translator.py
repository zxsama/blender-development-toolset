import re
import shutil
import bpy
import os
import inspect
import bl_i18n_utils.settings as setting_lng
from .lib import polib


class BilingualTranslatorData:
    def __init__(self):
        self.lang_idx = 99
        self.menu_name = "Bilingual (双语显示)"
        self.locale_name = "bilingual"
        bl_res_path = bpy.utils.resource_path("LOCAL")
        data_files = os.path.join(bl_res_path, "datafiles")
        self.locale = os.path.join(data_files, "locale")

    def get_locale_floder(self):
        return self.locale

    def get_cfg_append_data(self):
        return f"\n{self.lang_idx}:{self.menu_name}:{self.locale_name}"

    def get_cfg_file(self):
        return os.path.join(self.locale, "languages")

    def get_bilingual_mo_path(self):
        new_mo_floder = os.path.join(self.locale, self.locale_name)
        new_mo_lcm = os.path.join(new_mo_floder, "LC_MESSAGES")
        new_mo_file = os.path.join(new_mo_lcm, "blender.mo")
        return new_mo_lcm, new_mo_file

    def get_white_list_path(self):
        addon_path = os.path.dirname(__file__)
        return os.path.join(
            addon_path, "resource", "bilingual_translator", "white_list"
        )


class MZ_OT_RegisterBilingualTranslator(bpy.types.Operator):
    bl_idname = "mz.register_bilingual_translator"
    bl_label = "注册双语翻译(自动重启)"
    bl_description = "Data required for bilingual translation registration"
    bl_options = {"REGISTER", "UNDO"}

    def draw(self, context):
        layout = self.layout
        layout.label(text="将会重启blender")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        BTD = BilingualTranslatorData()
        cfg_file = BTD.get_cfg_file()
        cfg_append_data = BTD.get_cfg_append_data()
        mo_floder, _ = BTD.get_bilingual_mo_path()

        with open(cfg_file, "a+", encoding="utf-8") as f:
            lang_data = f.read()
            if not (cfg_append_data in lang_data):
                f.write(cfg_append_data)

        if not os.path.exists(mo_floder):
            os.makedirs(mo_floder)

        self.report({"INFO"}, "双语翻译已注册")
        bpy.ops.mz.restart_saved_blender()
        return {"FINISHED"}


class MZ_OT_GenerateBilingualTranslator(bpy.types.Operator):
    bl_idname = "mz.generate_bilingual_translator"
    bl_label = "生成双语翻译"
    bl_description = "Generate bilingual translation"
    bl_options = {"REGISTER"}

    def merge_txt(self, txt, append_txt, swap):
        """生成双语翻译"""
        if txt == append_txt:
            return txt

        if swap:
            txt, append_txt = append_txt, txt
        custom_delimiter = self.custom_delimiter
        check_print_format = setting_lng.CHECK_PRINTF_FORMAT
        check_bracket_format = r"\{[^{}]*\}"
        replace_str = r"[＊]"

        check_format = rf"{check_print_format}|{check_bracket_format}"
        format = re.compile(check_format).findall

        if format(append_txt):
            append_txt = re.sub(check_format, replace_str, append_txt)

        return f"{txt}{custom_delimiter}{append_txt}"

    def get_bl_rna_name(self, target: str = "Node"):
        set_result = set()
        for li in bpy.types.__dir__():
            type = getattr(bpy.types, li)
            if hasattr(type, "bl_rna"):
                base = type.bl_rna.base
                while base:
                    if base.identifier == target:
                        set_result.add(type.bl_rna.name)
                        break
                    base = base.bl_rna.base
        return set_result

    def get_bl_rna_identifier(self, target: str = "Node"):
        set_result = set()
        for li in bpy.types.__dir__():
            type = getattr(bpy.types, li)
            if hasattr(type, "bl_rna"):
                base = type.bl_rna.base
                while base:
                    if base.identifier == target:
                        set_result.add(type.bl_rna.identifier)
                        break
                    base = base.bl_rna.base
        return set_result

    def invoke(self, context, event):
        context.preferences.view.language = "en_US"
        return self.execute(context)

    def execute(self, context):
        BTD = BilingualTranslatorData()
        _, bili_mo_file = BTD.get_bilingual_mo_path()
        locale_folder = BTD.get_locale_floder()
        white_list_file = BTD.get_white_list_path()
        bili_trans_prop = context.scene.mz_bilingual_translator_prop
        bilingual_lang_idx = int(bili_trans_prop.bilingual_lang)
        language_code = setting_lng.LANGUAGES[bilingual_lang_idx][2]
        self.custom_delimiter = bili_trans_prop.custom_delimiter
        is_translation_preceding = int(bili_trans_prop.is_translation_preceding[0])
        translation_section_all = bili_trans_prop.translation_section_all
        translation_section_node = bili_trans_prop.translation_section_node
        translation_section_modifier = bili_trans_prop.translation_section_modifier
        translation_section_white_list = bili_trans_prop.translation_section_white_list

        # 获取mo数据
        ori_lang_folder = os.path.join(locale_folder, language_code)
        if not os.path.exists(ori_lang_folder):
            language_code = language_code.split("_")[0]
            ori_lang_folder = os.path.join(locale_folder, language_code)
            if not os.path.exists(ori_lang_folder):
                self.report({"WARNING"}, "不存在对应语言包!")
                return {"FINISHED"}
        ori_lang_mo = os.path.join(ori_lang_folder, "LC_MESSAGES", "blender.mo")
        translation_data = polib.mofile(ori_lang_mo, wrapwidth=180)

        # 按选定区域翻译
        section_data = set()
        # Node
        if not translation_section_all and translation_section_node:
            nodes_name = self.get_bl_rna_name(target="Node")
            section_data.update(nodes_name)

            # Modifier
        if not translation_section_all and translation_section_modifier:
            modif_identifier = self.get_bl_rna_identifier(target="Modifier")
            # 无法直接获取显示的UI名称, 字符串处理一下
            format_modifier_name = (
                lambda name: " ".join(
                    re.findall(r"[A-Z][a-z]*", name.replace("Modifier", ""))
                )
                .replace("To", "to")
                .replace("U V", "UV")
            )
            formatted_modif_name = list(map(format_modifier_name, modif_identifier))
            section_data.update(formatted_modif_name)
            modif_name = self.get_bl_rna_name(target="Modifier")
            section_data.update(modif_name)

            # 白名单
        if not translation_section_all and translation_section_white_list:
            with open(white_list_file, "r") as f:
                white_list = [line.strip() for line in f.readlines()]
            section_data.update(white_list)

        for entry in translation_data:
            if translation_section_all or entry.msgid in section_data:
                entry.msgstr = self.merge_txt(
                    entry.msgstr, entry.msgid, is_translation_preceding
                )

        translation_data.save(bili_mo_file)
        context.preferences.view.language = BTD.locale_name
        context.preferences.view.use_translate_new_dataname = False
        self.report({"INFO"}, "双语翻译已生成")
        return {"FINISHED"}


# exe速度更快
# gettext_tools = os.path.join(os.path.dirname(__file__), "lib","gettext_tools")
# msgfmt = os.path.join(gettext_tools,"msgfmt.exe")
# msgunfmt = os.path.join(gettext_tools, "msgunfmt.exe")
# decode_mo2po = [f"{msgunfmt} blender.mo -o blender.po"]
# encode_po2mo = [f"{msgfmt} blender.po -o blender.mo"]


def unregister_bilingual_translator():
    BTD = BilingualTranslatorData()
    cfg_file = BTD.get_cfg_file()
    cfg_append_data = BTD.get_cfg_append_data()
    mo_floder, _ = BTD.get_bilingual_mo_path()

    if os.path.exists(cfg_file):
        with open(cfg_file, "r", encoding="utf-8") as f:
            lang_data = f.read()
            lang_data = lang_data.replace(cfg_append_data, "")
        with open(cfg_file, "w", encoding="utf-8") as f:
            f.writelines(lang_data)

    mo_floder = os.path.dirname(mo_floder)
    if os.path.exists(mo_floder):
        shutil.rmtree(mo_floder)


class MZ_OT_DeleteBilingualTranslator(bpy.types.Operator):
    bl_idname = "mz.delete_bilingual_translator"
    bl_label = "删除双语翻译"
    bl_description = "Delete bilingual translation"
    bl_options = {"REGISTER"}

    def draw(self, context):
        layout = self.layout
        layout.label(text="将会重启blender")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        context.preferences.view.language = "en_US"
        unregister_bilingual_translator()
        self.report({"INFO"}, "双语翻译已删除")
        bpy.ops.mz.restart_saved_blender()
        return {"FINISHED"}


class MZ_OT_OpenBilingualWhiteList(bpy.types.Operator):
    bl_idname = "mz.open_bilingual_white_list"
    bl_label = "双语翻译白名单"
    bl_description = "Edit whitelist"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        BTD = BilingualTranslatorData()
        white_list_file = BTD.get_white_list_path()
        for text in bpy.data.texts:
            if text.filepath == white_list_file:
                self.report({"INFO"}, "参见文本编辑器中的 'white_list'")
                return {"FINISHED"}
        text = bpy.data.texts.load(white_list_file)

        self.report({"INFO"}, "参见文本编辑器中的 'white_list'")
        return {"FINISHED"}


def unregister():
    unregister_bilingual_translator()
