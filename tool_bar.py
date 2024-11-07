import bpy
import os
from .functions import install_modul, launch_blender
import bl_i18n_utils.settings as setting_lng


class UI_OT_Switch_Language(bpy.types.Operator):
    """
    语言切换
    """

    bl_idname = "mz.language_switch"
    bl_label = "language Switch"
    bl_description = "语言切换"
    bl_options = {"UNDO"}

    def execute(self, context):

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        language_items = addon_prefs.get_lang_items_callback(context)

        code1 = setting_lng.LANGUAGES[int(addon_prefs.switch_lang_slot1)][2]
        code2 = language_items[int(addon_prefs.switch_lang_slot2)][2]
        code3 = language_items[int(addon_prefs.switch_lang_slot3)][2]
        language_codes = [code1, code2, code3]
        language_codes = list(set(language_codes))
        current_lan = context.preferences.view.language

        try:
            current_idx = language_codes.index(current_lan)
            next_language = language_codes[(current_idx + 1) % len(language_codes)]
            while next_language == "":
                current_idx += 1
                next_language = language_codes[current_idx % len(language_codes)]
            context.preferences.view.language = next_language
            if not current_lan == "en_US":
                context.preferences.view.use_translate_new_dataname = False
        except:
            context.preferences.view.language = code1

        return {"FINISHED"}


class UI_OT_OpenAddonPath(bpy.types.Operator):
    """
    打开用户插件文件夹, 并判断窗口是否已打开, 已打开则复原, 未打开则打开
    """

    bl_idname = "mz.open_addon_path"
    bl_label = "open user addon folder"
    bl_description = "打开当前插件所在的插件文件夹"

    def execute(self, context):

        # addon_path = bpy.utils.script_path_user() + r"\addons"
        addon_path = os.path.dirname(os.path.dirname(__file__))
        bpy.ops.wm.path_open(filepath=addon_path)
        return {"FINISHED"}


# class UI_OT_ReloadAddon(bpy.types.Operator):
#     """
#     刷新插件，不会刷新已导入模块的全局字典
#     """

#     bl_idname = "wm.reload_addon"
#     bl_label = "reload addon"
#     bl_description = "刷新插件"
#     bl_options = {"REGISTER"}

#     def execute(self, context):
#         # module_reload() #TODO
#         bpy.ops.preferences.addon_refresh()
#         bpy.ops.script.reload()

#         self.report({"INFO"}, "插件刷新完成")
#         return {"FINISHED"}


class UI_OT_RestartSavedBlender(bpy.types.Operator):
    """
    保存并重启blender (保存当前工作区域, 基于当前blender窗口路径打开保存的blender文件)
    """

    bl_idname = "mz.restart_saved_blender"
    bl_label = "save&restart blender"
    bl_description = "保存当前工作区域后重启blender"
    bl_options = {"REGISTER"}

    run_admin: bpy.props.BoolProperty(
        name="run_admin",
        description="是否以管理员权限重启(steam版不生效)",
        default=False,
    )

    def execute(self, context):
        # save
        if bpy.data.filepath:
            save_path = bpy.data.filepath
        else:
            # tmp save
            save_path = os.path.join(os.path.dirname(__file__), r"saved\temp.blend")
            if os.path.exists(save_path):
                os.remove(save_path)
        bpy.ops.wm.save_as_mainfile(filepath=save_path, check_existing=False, copy=True)

        # launch and quit
        launch_blender(file_path=save_path, is_admin=self.run_admin)
        self.report({"INFO"}, "重启Blender")
        bpy.ops.wm.quit_blender()

        return {"FINISHED"}


class UI_OT_RestartBlender(bpy.types.Operator):
    """
    重启blender (关闭当前blender进程, 基于当前blender进程路径打开全新的blender进程)
    """

    bl_idname = "mz.restart_blender"
    bl_label = "restart blender"
    bl_description = "重启打开全新的blender"
    bl_options = {"REGISTER"}

    run_admin: bpy.props.BoolProperty(
        name="run_admin",
        description="是否以管理员权限重启(steam版不生效)",
        default=False,
    )

    def execute(self, context):
        # launch and quit
        launch_blender(is_admin=self.run_admin)
        self.report({"INFO"}, "重启Blender")
        bpy.ops.wm.quit_blender()

        return {"FINISHED"}


class UI_OT_ConsoleToggle(bpy.types.Operator):
    """
    切换系统控制台窗口, 无论窗口状态, 点击就会将窗口前置
    """

    bl_idname = "mz.console_toggle_custom"
    bl_label = "console_toggle"
    bl_description = "控制台置顶"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout
        layout.label(text="第一次使用需要安装pywin32库, 确认安装并重启")

    def invoke(self, context, event):
        try:
            import win32gui, win32process, win32con

            return self.execute(context)
        except ImportError:
            return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        try:
            # pywin32
            import win32gui, win32process, win32con
        except ImportError:
            install_modul(self, "pywin32")
            bpy.ops.mz.restart_saved_blender()
            return {"CANCELLED"}

        hWnd_all_list = []
        console_handle_list = []
        true_console_handle = None

        # get blender path
        blender_handle = win32gui.GetForegroundWindow()
        blender_TID, blender_PID = win32process.GetWindowThreadProcessId(blender_handle)
        blender_path = bpy.app.binary_path

        # find all blender console
        win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd), hWnd_all_list)
        for hwnd in hWnd_all_list:
            h_title = win32gui.GetWindowText(hwnd)
            if h_title == blender_path:
                console_handle_list.append(hwnd)

        # find current blender console
        for handle in console_handle_list:
            _, console_blender_PID = win32process.GetWindowThreadProcessId(handle)
            if console_blender_PID == blender_PID:
                true_console_handle = handle

        # Show Window
        if true_console_handle is None:
            bpy.ops.wm.console_toggle()
        else:
            # 先激活一次, 让blender设置console窗口状态
            bpy.ops.wm.console_toggle()
            win32gui.ShowWindow(true_console_handle, win32con.SW_SHOW)
            if win32gui.IsIconic(true_console_handle):
                win32gui.ShowWindow(true_console_handle, 9)  # 9:win32con.SW_RESTORE
            win32gui.SetForegroundWindow(true_console_handle)

        hWnd_all_list.clear()
        console_handle_list.clear()

        return {"FINISHED"}


class MZ_HT_BarUI(bpy.types.Header):
    bl_space_type = "TOPBAR"

    def draw(self, context):
        region = context.region
        bar_button = context.scene.mz_bar_button
        bar_button[UI_OT_Switch_Language.bl_idname][
            2
        ] = context.preferences.view.language

        addon_name = __package__
        prefs = context.preferences.addons[addon_name].preferences

        enable_bars = prefs.enable_bar_buttons
        for idx, (bl_id, data) in enumerate(bar_button.items()):
            if enable_bars[idx] and region.alignment == "RIGHT":
                self.layout.operator(operator=bl_id, icon_value=data[1], text=data[2])
