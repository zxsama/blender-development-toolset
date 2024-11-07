import ctypes
import re
import sys
import time
import bpy
import os
import bl_i18n_utils.settings as setting_lng
import bpy.app.translations as trs
from .lib import polib
from .functions import wait_for_new_file
from .lib.bilingual_tools import register as bil_reg
from .lib.bilingual_tools import remove as bil_remove
from .lib.bilingual_tools import complie as bil_complie


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
        return f"{self.lang_idx}:{self.menu_name}:{self.locale_name}"

    def get_cfg_file(self):
        return os.path.join(self.locale, "languages")

    def get_bilingual_mo_path(self):
        new_mo_floder = os.path.join(self.locale, self.locale_name)
        new_mo_lcm = os.path.join(new_mo_floder, "LC_MESSAGES")
        new_mo_file = os.path.join(new_mo_lcm, "blender.mo")
        return new_mo_lcm, new_mo_file

    def get_whitelist_path(self):
        addon_path = os.path.dirname(__file__)
        return os.path.join(addon_path, "resource", "bilingual_translator", "whitelist")

    def get_blacklist_path(self):
        addon_path = os.path.dirname(__file__)
        return os.path.join(addon_path, "resource", "bilingual_translator", "blacklist")

    def admin_required(self):
        cfg_file = self.get_cfg_file()
        required = False
        try:
            f = open(cfg_file, "a+", encoding="utf-8")
        except PermissionError:
            required = True
        else:
            f.close()
        return required

    def get_bilingual_init_state(self):
        bil_mo_folder, _ = self.get_bilingual_mo_path()
        if os.path.exists(bil_mo_folder):
            return True
        else:
            return False

    def get_bilingual_compile_state(self):
        _, bil_mo_file = self.get_bilingual_mo_path()
        if os.path.exists(bil_mo_file):
            return True
        else:
            return False


class MZ_OT_RegisterBilingualTranslator(bpy.types.Operator):
    bl_idname = "mz.register_bilingual_translator"
    bl_label = "Register Bilingual Translation (Auto Restart)"
    bl_description = trs.pgettext_tip("Data required for bilingual translation registration")
    bl_options = {"REGISTER", "UNDO"}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Blender Will Restart")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        BTD = BilingualTranslatorData()
        cfg_file = BTD.get_cfg_file()
        cfg_append_data = BTD.get_cfg_append_data()
        mo_floder, _ = BTD.get_bilingual_mo_path()

        pyf_register = bil_reg.__file__
        parameter = f'"{pyf_register}" -file "{cfg_file}" -data "\n{cfg_append_data}" -mo_floder "{mo_floder}"'
        operation = "runas" if BTD.admin_required() else "open"
        ctypes.windll.shell32.ShellExecuteW(
            None, operation, sys.executable, parameter, None, 0
        )

        self.report({"INFO"}, "Bilingual Translation Registered")
        bpy.ops.mz.restart_saved_blender()
        return {"FINISHED"}


class MZ_OT_GenerateBilingualTranslator(bpy.types.Operator):
    bl_idname = "mz.generate_bilingual_translator"
    bl_label = "Generate Bilingual Translation"
    bl_description = trs.pgettext_tip("Generate Bilingual Translation")
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

    def get_nodes_property(self, identifiers):
        """
        获取所有节点的属性名称, API限制所以先实例化再获取
        https://blender.stackexchange.com/questions/254305/how-to-know-the-input-output-sockets-of-a-node-without-importing-it-into-the
        """

        def get_self_property(node):
            default_props = (
                "dimensions",
                "draw_buttons",
                "draw_buttons_ext",
                "input_template",
                "inputs",
                "internal_links",
                "isAnimationNode",
                "is_registered_node_type",
                "output_template",
                "outputs",
                "poll",
                "poll_instance",
                "rna_type",
                "socket_value_update",
                "type",
                "update",
                "viewLocation",
                "texture_mapping",
                "color_mapping",
                "filepath",
                "cache_point_density",
                "calc_point_density",
                "calc_point_density_minmax",
                "interface",
                "height",
                "show_options",
                "show_preview",
                "show_texture",
                "width_hidden",
                "color",
                "hide",
                "label",
                "location",
                "mute",
                "name",
                "parent",
                "select",
                "use_custom_color",
                "width",
            )
            self_proper = []
            for prop_name in dir(node):
                if prop_name.startswith("_") or prop_name.startswith("bl_"):
                    continue
                if prop_name in default_props:
                    continue
                # 从属性名称生成可能的UI名称组合, 临时方案
                words = prop_name.split("_")
                capitalized_words = [
                    word.capitalize().replace("Uv", "UV") for word in words
                ]
                self_proper.extend([" ".join(capitalized_words)] + capitalized_words)
            return self_proper

        property_set = set()
        tmp_name = "nodes_temporary"
        node_types = [
            "CompositorNodeTree",
            "TextureNodeTree",
            "GeometryNodeTree",
            "ShaderNodeTree",
        ]
        data = bpy.data
        ng = data.node_groups

        for nd_type in node_types:
            tmp_ng = ng.get(tmp_name)
            if not tmp_ng:
                tmp_ng = ng.new(tmp_name, type=nd_type)
            node = tmp_ng.nodes
            for name in identifiers:
                node.clear()
                try:
                    n = node.new(name)
                    socket_name = lambda s: s.label if s.label else s.name
                    inputs = [socket_name(i) for i in n.inputs]
                    outputs = [socket_name(o) for o in n.outputs]
                    selfs = get_self_property(n)
                    property_set.update(inputs)
                    property_set.update(outputs)
                    property_set.update(selfs)
                except Exception as e:
                    ...
            ng.remove(tmp_ng)

        return property_set

    def get_bl_rna_name(self, target: str = "Node"):
        """
        https://blender.stackexchange.com/questions/79784/how-to-get-all-types-of-nodes-dynamically
        """
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
        whitelist_file = BTD.get_whitelist_path()
        blacklist_file = BTD.get_blacklist_path()
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences 
        bilingual_lang_idx = int(addon_prefs.bilingual_lang)
        language_code = setting_lng.LANGUAGES[bilingual_lang_idx][2]
        
        # 重新注册插件翻译, 匹配双语语言, 暂时只有中文
        addon_prefs.bilingual_lang_code_current = language_code
        if language_code == setting_lng.LANGUAGES[13][2]:
            from .translations import translations
            translations["bilingual"] = translations[setting_lng.LANGUAGES[13][2]]
            bpy.app.translations.unregister(__name__)
            bpy.app.translations.register(__name__, translations)
        
        self.custom_delimiter = addon_prefs.custom_delimiter
        is_translation_preceding = int(addon_prefs.is_translation_preceding[0])
        translation_section_all = addon_prefs.translation_section_all
        translation_section_node = addon_prefs.translation_section_node
        translation_section_node_property = (
            addon_prefs.translation_section_node_property
        )
        translation_section_modifier = addon_prefs.translation_section_modifier
        translation_section_whitelist = addon_prefs.translation_section_whitelist
        translation_section_blacklist = addon_prefs.translation_section_blacklist

        # 获取mo数据
        ori_lang_folder = os.path.join(locale_folder, language_code)
        if not os.path.exists(ori_lang_folder):
            language_code = language_code.split("_")[0]
            ori_lang_folder = os.path.join(locale_folder, language_code)
            if not os.path.exists(ori_lang_folder):
                self.report({"WARNING"}, "The corresponding language pack does not exist!")
                return {"FINISHED"}
        ori_lang_mo = os.path.join(ori_lang_folder, "LC_MESSAGES", "blender.mo")
        translation_data = polib.mofile(ori_lang_mo, wrapwidth=180)

        # 按选定区域翻译
        section_data = set()
        # Node
        if not translation_section_all and translation_section_node:
            nodes_name = self.get_bl_rna_name(target="Node")
            section_data.update(nodes_name)

            # Node_Property
        if not translation_section_all and translation_section_node_property:
            modif_identifier = self.get_bl_rna_identifier(target="Node")
            nodes_property = self.get_nodes_property(modif_identifier)
            section_data.update(nodes_property)

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
        whitelist = []
        if not translation_section_all and translation_section_whitelist:
            with open(whitelist_file, "r", encoding="utf-8") as f:
                whitelist = [line.strip() for line in f.readlines()]
            section_data.update(whitelist)

            # 黑名单
        blacklist = []
        if translation_section_blacklist:
            with open(blacklist_file, "r", encoding="utf-8") as f:
                blacklist = [line.strip() for line in f.readlines()]
            section_data.difference_update(blacklist)

        # 合并翻译
        for entry in translation_data:
            if (translation_section_all or entry.msgid in section_data) and (
                not entry.msgid in blacklist
            ):
                entry.msgstr = self.merge_txt(
                    entry.msgstr, entry.msgid, is_translation_preceding
                )

        # 保存为po文件
        addon_dir = os.path.dirname(__file__)
        tmp_po_file = os.path.join(addon_dir, "saved", "blender.po")
        translation_data.save_as_pofile(tmp_po_file)

        # 使用msgfmt.exe转换po文件, 比直接polib save更快
        gettext_tools = os.path.join(addon_dir, "lib", "gettext_tools")
        msgfmt = os.path.join(gettext_tools, "msgfmt.exe")

        # 可能需要管理员权限
        timestamp = time.time()
        pyf_compile = bil_complie.__file__
        parameter = f'"{pyf_compile}" -po "{tmp_po_file}" -mo "{bili_mo_file}" -msgfmt "{msgfmt}"'
        operation = "runas" if BTD.admin_required() else "open"
        ctypes.windll.shell32.ShellExecuteW(
            None, operation, sys.executable, parameter, None, 0
        )

        wait_for_new_file(bili_mo_file, timestamp, timeout=2)
        os.remove(tmp_po_file)

        # 显示双语
        context.preferences.view.language = BTD.locale_name
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        if not (
            addon_prefs.switch_lang_slot2 == "1"
            or addon_prefs.switch_lang_slot3 == "1"
        ):
            addon_prefs.switch_lang_slot2 = "1"  # 语言切换中的双语索引
        context.preferences.view.use_translate_new_dataname = False
        self.report({"INFO"}, "Bilingual Translation Generated")
        return {"FINISHED"}


# exe速度更快
# gettext_tools = os.path.join(os.path.dirname(__file__), "lib","gettext_tools")
# msgfmt = os.path.join(gettext_tools,"msgfmt.exe")
# msgunfmt = os.path.join(gettext_tools, "msgunfmt.exe")
# decode_mo2po = [f"{msgunfmt} blender.mo -o blender.po"]
# encode_po2mo = [f"{msgfmt} blender.po -o blender.mo"]


class MZ_OT_DeleteBilingualTranslator(bpy.types.Operator):
    bl_idname = "mz.delete_bilingual_translator"
    bl_label = "Delete Bilingual Translation"
    bl_description = trs.pgettext_tip("Delete Bilingual Translation")
    bl_options = {"REGISTER"}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Blender Will Restart")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        BTD = BilingualTranslatorData()
        cfg_file = BTD.get_cfg_file()
        cfg_append_data = BTD.get_cfg_append_data()
        mo_floder, _ = BTD.get_bilingual_mo_path()

        context.preferences.view.language = "en_US"

        pyf_remove = bil_remove.__file__
        parameter = f'"{pyf_remove}" -file "{cfg_file}" -data "\n{cfg_append_data}" -mo_floder "{mo_floder}"'
        operation = "runas" if BTD.admin_required() else "open"
        ctypes.windll.shell32.ShellExecuteW(
            None, operation, sys.executable, parameter, None, 0
        )

        # 恢复语言切换, "0:空, 1:双语索引, 15:简中索引"
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        if addon_prefs.switch_lang_slot2 == "1":
            addon_prefs.switch_lang_slot2 = "15"
        if addon_prefs.switch_lang_slot3 == "1":
            addon_prefs.switch_lang_slot3 = "0"

        self.report({"INFO"}, "Bilingual Translation Deleted")
        bpy.ops.mz.restart_saved_blender()
        return {"FINISHED"}


class MZ_OT_OpenBilingualBlackWhiteList(bpy.types.Operator):
    bl_idname = "mz.open_bilingual_black_white_list"
    bl_label = "Open Bilingual Translation Blacklist/Whitelist"
    bl_description = trs.pgettext_tip("Edit black/whitelist")
    bl_options = {"REGISTER", "UNDO"}

    list_type: bpy.props.BoolProperty(
        name="list_type",
        default=True,
        description="True: Whitelist, False: Blacklist",
    )  # type: ignore

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        BTD = BilingualTranslatorData()
        whitelist_file = BTD.get_whitelist_path()
        blacklist_file = BTD.get_blacklist_path()
        list_file = whitelist_file if self.list_type else blacklist_file
        list_name = os.path.basename(list_file)
        for text in bpy.data.texts:
            if text.filepath == list_file:
                self.report({"INFO"}, trs.pgettext("See '%s' in the text editor") % list_name)
                return {"FINISHED"}
        text = bpy.data.texts.load(list_file)

        self.report({"INFO"}, trs.pgettext("See '%s' in the text editor") % list_name)
        return {"FINISHED"}
