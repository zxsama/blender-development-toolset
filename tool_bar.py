import bpy
import os
from .functions import install_modul

bar_button = {
    'UI_OT_Switch_ZH_EN':"中英文切换",
    'UI_OT_OpenAddonPath':"打开插件路径",
    'UI_OT_ReloadAddon':"重新载入插件(仅__init__)",
    'UI_OT_RestartSavedBlender':"保存并重新启动bl",
    'UI_OT_RestartBlender':"不保存重启bl",
    'UI_OT_ConsoleToggle':"打开控制台",
}

'''
    中英文切换
'''
class UI_OT_Switch_ZH_EN(bpy.types.Operator):
    bl_idname = 'wm.zh_en_switch'
    bl_label = 'zh/en Switch'
    bl_description = "中英文切换"
    bl_options = {'UNDO'}

    def execute(self, context):
        lan = context.preferences.view.language
        if lan == 'en_US':
            context.preferences.view.language = 'zh_CN'
            context.preferences.view.use_translate_new_dataname = False
        else:
            context.preferences.view.language = 'en_US'
        return {'FINISHED'}

    def draw(self, context):
        region = context.region
        custom_prop = context.scene.mz_custom_prop
        enable_bar = custom_prop.enable_bar_buttons[0]
        if region.alignment == 'RIGHT' and enable_bar:
            self.layout.operator(operator=UI_OT_Switch_ZH_EN.bl_idname,
                                 icon='WORDWRAP_ON', text=context.preferences.view.language)


'''
    打开用户插件文件夹, 并判断窗口是否已打开, 已打开则复原, 未打开则打开
'''
class UI_OT_OpenAddonPath(bpy.types.Operator):
    bl_idname = 'wm.open_addon_path'
    bl_label = 'open user addon folder'
    bl_description = "打开当前插件所在的插件文件夹"

    def execute(self, context):
        
        # addon_path = bpy.utils.script_path_user() + r"\addons"
        addon_path = os.path.dirname(os.path.dirname(__file__))
        bpy.ops.wm.path_open(filepath = addon_path)
        
        # try:
        #     # pywin32
        #     import win32gui
        # except ImportError:
        #     install_modul(self, "pywin32")
        #     return {'CANCELLED'}

        # hWnd_all_list = []
        # hWnd_child_list = []
        # hWnd_list = []
        # target_handle = 0
        # right_window = False

        # # get all handle, check name:"addons"
        # win32gui.EnumWindows(
        #     lambda hWnd, param: param.append(hWnd), hWnd_all_list)
        # for hwnd in hWnd_all_list:
        #     h_title = win32gui.GetWindowText(hwnd)
        #     if h_title == "addons":
        #         hWnd_list.append(hwnd)
        # # target_handle = win32gui.FindWindow("CabinetWClass", "scripts")

        # # get child handle, find target handle
        # for handle in hWnd_list:
        #     win32gui.EnumChildWindows(
        #         handle, lambda hWnd_1, param: param.append(hWnd_1), hWnd_child_list)
        #     ''' TODO: 
        #         bug: hWnd_child_list 会获取到所有名称(h_title)相同的文件窗口的子句柄.
        #         如果有相同名称的文件夹同时打开, 导致后续窗口的判断失效.
        #         临时的解决方法: 只取后60个子句柄.
        #     '''
        #     for hwnd_c in hWnd_child_list[-60:]:
        #         h_c_title = win32gui.GetWindowText(hwnd_c)
        #         if h_c_title[-15:-1] == addon_path[-15:-1]:
        #             # print(h_c_title)
        #             right_window = True
        #             target_handle = handle
        #             break

        ## show window or open window
        # if target_handle and right_window:
        #     if(win32gui.IsIconic(target_handle)):
        #         win32gui.ShowWindow(target_handle, 9)  # 9:win32con.SW_RESTORE
        #     win32gui.SetForegroundWindow(target_handle)
        # else:
        #     os.system("explorer.exe %s" % addon_path)

        # hWnd_all_list.clear()
        # hWnd_child_list.clear()
        # hWnd_list.clear()

        return {'FINISHED'}

    def draw(self, context):
        region = context.region
        custom_prop = context.scene.mz_custom_prop
        enable_bar = custom_prop.enable_bar_buttons[1]
        if region.alignment == 'RIGHT' and enable_bar:
            self.layout.operator(
                operator=UI_OT_OpenAddonPath.bl_idname, icon='WORKSPACE', text='')


'''
    刷新插件，不会刷新已导入模块的全局字典
'''
class UI_OT_ReloadAddon(bpy.types.Operator):
    bl_idname = "wm.reload_addon"
    bl_label = "reload addon"
    bl_description = '刷新插件'
    bl_options = {'REGISTER'}

    def execute(self, context):
        bpy.ops.preferences.addon_refresh()
        result = bpy.ops.script.reload()
        self.report({'INFO'}, "插件刷新完成")
        return {'FINISHED'}

    def draw(self, context):
        region = context.region
        custom_prop = context.scene.mz_custom_prop
        enable_bar = custom_prop.enable_bar_buttons[2]
        if region.alignment == 'RIGHT' and enable_bar:
            self.layout.operator(
                operator=UI_OT_ReloadAddon.bl_idname, icon='FILE_REFRESH', text='')


'''
    保存当前工作区域, 基于当前blender窗口路径打开, 保存的blender文件
'''
class UI_OT_RestartSavedBlender(bpy.types.Operator):
    bl_idname = "wm.restart_saved_blender"
    bl_label = "restart blender"
    bl_description = '保存当前工作区域, 并重启blender\n注意: 会改变工作路径'
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            # pywin32
            import win32gui
            import win32api
            import win32process
            from psutil import Process
        except ImportError:
            install_modul(self, "pywin32", "psutil")
            return {'CANCELLED'}

        # get blender.exe path
        blender_handle = win32gui.GetForegroundWindow()
        _, blender_PID = win32process.GetWindowThreadProcessId(blender_handle)
        blender_path = Process(blender_PID).exe()

        # open and kill
        # save_path = bpy.utils.script_path_user() + r"\addons\DevelopmentToolset\saved\temp.blend"
        save_path = os.path.join(os.path.dirname(__file__), r"saved\temp.blend")
        if os.path.exists(save_path):
            os.remove(save_path)
        bpy.ops.wm.save_as_mainfile(filepath = save_path, check_existing = False , copy = True)
        
        # os.system("\"" + blender_path + "\"")
        win32api.ShellExecute(0, 'open', blender_path, "\"" + save_path + "\"" , '', 1)
        self.report({'INFO'}, "重启Blender")
        
        # os.kill(blender_PID, 0)
        bpy.ops.wm.quit_blender()
        return {'FINISHED'}

    def draw(self, context):
        region = context.region
        custom_prop = context.scene.mz_custom_prop
        enable_bar = custom_prop.enable_bar_buttons[3]
        if region.alignment == 'RIGHT' and enable_bar:
            self.layout.operator(
                operator=UI_OT_RestartSavedBlender.bl_idname, icon='X', text='')

  
'''
    关闭当前blender窗口, 基于当前blender窗口路径打开新的blender窗口
'''
class UI_OT_RestartBlender(bpy.types.Operator):
    bl_idname = "wm.restart_blender"
    bl_label = "restart blender"
    bl_description = '重启blender\n注意: 会强行终止进程并重启'
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            # pywin32
            import win32gui
            import win32api
            import win32process
            from psutil import Process
        except ImportError:
            install_modul(self, "pywin32", "psutil")
            return {'CANCELLED'}

        # get blender.exe path
        blender_handle = win32gui.GetForegroundWindow()
        _, blender_PID = win32process.GetWindowThreadProcessId(blender_handle)
        blender_path = Process(blender_PID).exe()

        # os.system("\"" + blender_path + "\"")
        # open and kill
        win32api.ShellExecute(0, 'open', blender_path, '', '', 1)
        os.kill(blender_PID, 0)
        self.report({'INFO'}, "重启Blender")
        return {'FINISHED'}

    def draw(self, context):
        region = context.region
        custom_prop = context.scene.mz_custom_prop
        enable_bar = custom_prop.enable_bar_buttons[4]
        if region.alignment == 'RIGHT' and enable_bar:
            self.layout.operator(
                operator=UI_OT_RestartBlender.bl_idname, icon='CANCEL', text='')


'''
    切换系统控制台窗口, 无论窗口状态, 点击就会将窗口前置
'''
class UI_OT_ConsoleToggle(bpy.types.Operator):
    bl_idname = "wm.console_toggle_custom"
    bl_label = "console_toggle"
    bl_description = '系统控制台(点击显示)'
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            # pywin32
            import win32gui
            import win32process
            import win32con
            from psutil import Process
        except ImportError:
            install_modul(self, "pywin32", "psutil")
            return {'CANCELLED'}

        hWnd_all_list = []
        console_handle_list = []
        true_console_handle = None

        # get blender path
        blender_handle = win32gui.GetForegroundWindow()
        blender_TID, blender_PID = win32process.GetWindowThreadProcessId(
            blender_handle)
        blender_path = Process(blender_PID).exe()

        # find all blender console
        win32gui.EnumWindows(
            lambda hWnd, param: param.append(hWnd), hWnd_all_list)
        for hwnd in hWnd_all_list:
            h_title = win32gui.GetWindowText(hwnd)
            if h_title == blender_path:
                console_handle_list.append(hwnd)
                
        # find current blender console
        for handle in console_handle_list:
            _, console_blender_PID = win32process.GetWindowThreadProcessId(
                handle)
            if console_blender_PID == blender_PID:
                true_console_handle = handle

        # Show Window
        if true_console_handle is None:
            bpy.ops.wm.console_toggle()
        else:
            # 先激活一次, 让blender设置console窗口状态
            bpy.ops.wm.console_toggle()
            win32gui.ShowWindow(true_console_handle, win32con.SW_SHOW)
            if(win32gui.IsIconic(true_console_handle)):  
                win32gui.ShowWindow(true_console_handle, 9) # 9:win32con.SW_RESTORE
            win32gui.SetForegroundWindow(true_console_handle)

        hWnd_all_list.clear()
        console_handle_list.clear()

        return {'FINISHED'}

    def draw(self, context):
        region = context.region
        custom_prop = context.scene.mz_custom_prop
        enable_bar = custom_prop.enable_bar_buttons[5]
        if region.alignment == 'RIGHT' and enable_bar:
            self.layout.operator(
                operator=UI_OT_ConsoleToggle.bl_idname, icon='CONSOLE', text='')