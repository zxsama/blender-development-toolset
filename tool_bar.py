import sys
import tempfile
import bpy
import os
import ctypes
import bl_i18n_utils.settings as setting_lng
import bpy.app.translations as trs
from ctypes import wintypes
from .functions import launch_blender


class UI_OT_Switch_Language(bpy.types.Operator):
    """
    语言切换
    """

    bl_idname = "mz.language_switch"
    bl_label = "Language Switch"
    bl_description = trs.pgettext_tip("Language Switch")
    bl_options = {"UNDO"}

    def execute(self, context):

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        language_items = addon_prefs.get_lang_items_callback(context)

        code1 = setting_lng.LANGUAGES[int(addon_prefs.switch_lang_slot1)][2]
        code2 = language_items[int(addon_prefs.switch_lang_slot2)][2]
        code3 = language_items[int(addon_prefs.switch_lang_slot3)][2]
        language_codes = [code1, code2, code3]
        language_codes = list(dict.fromkeys(language_codes))
        current_lan = context.preferences.view.language

        try:
            current_idx = language_codes.index(current_lan)
            next_language = language_codes[(current_idx + 1) % len(language_codes)]
            while next_language == "":
                current_idx += 1
                next_language = language_codes[current_idx % len(language_codes)]
            context.preferences.view.language = next_language
        except:
            context.preferences.view.language = code1
            
        context.preferences.view.use_translate_new_dataname = False
            
        return {"FINISHED"}


class UI_OT_OpenAddonPath(bpy.types.Operator):
    """
    打开用户插件文件夹, 并判断窗口是否已打开, 已打开则复原, 未打开则打开
    """

    bl_idname = "mz.open_addon_path"
    bl_label = "Open Addon Path"
    bl_description = trs.pgettext_tip("Open the addon folder where the current addon is located")

    def execute(self, context):

        # addon_path = bpy.utils.script_path_user() + r"\addons"
        addon_path = os.path.dirname(os.path.dirname(__file__))
        bpy.ops.wm.path_open(filepath=addon_path)
        return {"FINISHED"}


class UI_OT_RestartSavedBlender(bpy.types.Operator):
    """
    保存并重启blender (保存当前工作区域, 基于当前blender窗口路径打开保存的blender文件)
    """

    bl_idname = "mz.restart_saved_blender"
    bl_label = "Save&Restart Blender"
    bl_description = trs.pgettext_tip("Save the current workspace and restart Blender")
    bl_options = {"REGISTER"}

    run_admin: bpy.props.BoolProperty(
        name="run_admin",
        description="Whether to restart with administrator (not effective for Steam version)",
        default=False,
    )

    def execute(self, context):
        # save
        if bpy.data.filepath and os.path.exists(bpy.data.filepath):
            save_path = bpy.data.filepath
        else:
            # tmp save
            tmp_dir = tempfile.mkdtemp() # 会残存垃圾文件
            save_path = os.path.join(tmp_dir, r"bl_temp.blend")
            if os.path.exists(save_path):
                os.remove(save_path)
        bpy.ops.wm.save_as_mainfile(filepath=save_path, check_existing=False, copy=True)

        # launch and quit
        launch_blender(file_path=save_path, is_admin=self.run_admin)
        self.report({"INFO"}, "Restart Blender")
        bpy.ops.wm.quit_blender()

        return {"FINISHED"}


class UI_OT_RestartBlender(bpy.types.Operator):
    """
    重启blender (关闭当前blender进程, 基于当前blender进程路径打开全新的blender进程)
    """

    bl_idname = "mz.restart_blender"
    bl_label = "Restart Blender"
    bl_description = trs.pgettext_tip("Restart and open a new Blender")
    bl_options = {"REGISTER"}

    run_admin: bpy.props.BoolProperty(
        name="run_admin",
        description="Whether to restart with administrator (not effective for Steam version)",
        default=False,
    )

    def execute(self, context):
        # launch and quit
        launch_blender(is_admin=self.run_admin)
        self.report({"INFO"}, "Restart Blender")
        bpy.ops.wm.quit_blender()

        return {"FINISHED"}


class UI_OT_ConsoleToggle(bpy.types.Operator):
    """
    切换系统控制台窗口, 无论窗口状态, 点击就会将窗口前置一次
    """

    bl_idname = "mz.console_toggle_custom"
    bl_label = "Console Toggle(Only Windows)"
    bl_description = trs.pgettext_tip("Console Pin to Top(Only Windows)")
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        
        if sys.platform == "win32":
            return True
        else:
            return False

    console_handles: bpy.props.IntProperty(
        name="console_handles",
        default=0,
        description="Store window handle",
    )

    def execute(self, context):
        user32 = ctypes.WinDLL('user32')
        kernel32 = ctypes.WinDLL('kernel32')

        # 类型定义
        WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        user32.GetWindowThreadProcessId.restype = wintypes.DWORD

        # 获取当前进程 ID
        current_pid = kernel32.GetCurrentProcessId()
        
        def enum_windows_proc(hwnd, lParam):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)

                if buff.value == bpy.app.binary_path:
                    pid = wintypes.DWORD()
                    tid = user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))  # 获取进程ID,不能删
                    if pid.value == current_pid:
                        self.console_handles = hwnd
                        return False
            return True

        # 仅第一次切换控制台
        if not self.console_handles:
            bpy.ops.wm.console_toggle()

        # 枚举所有窗口
        enum_func = WNDENUMPROC(enum_windows_proc)
        user32.EnumWindows(enum_func, 0)

        if self.console_handles:
            # 强制窗口置顶组合技
            user32.ShowWindow(self.console_handles, 9)  # 先恢复
            user32.SetWindowPos(
                self.console_handles, -1, 0, 0, 0, 0, 0x0003
            )  # HWND_TOPMOST|SWP_NOMOVE|SWP_NOSIZE
            user32.SetForegroundWindow(self.console_handles)
        else:
            bpy.ops.wm.console_toggle()

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
