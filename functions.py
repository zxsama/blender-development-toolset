import os
import time
import bpy
import subprocess
import ctypes
from bpy.types import bpy_prop_collection


def install_modul(self, *modul_name):
    import os
    import sys

    # bpy.ops.wm.console_toggle()  # TODO: 判断控制台是否开启
    python_path = os.path.join(sys.prefix, "bin", "python.exe")
    print("Python Path: ", python_path)
    for modul in modul_name:
        print("-" * 30 + "\n未安装" + modul + "模块，安装中...\n")
        subprocess.call([python_path, "-m", "pip", "install", "-I", modul])
    print("\n安装结束.\n" + "重启blender后生效!\n" * 3 + "-" * 30)
    self.report({"WARNING"}, "重启blender!")


def collection_search(ID):
    def users(col):
        ret = tuple(repr(o) for o in col if o.user_of_id(ID))
        return ret if ret else None

    return filter(
        None,
        (
            users(getattr(bpy.data, p))
            for p in dir(bpy.data)
            if isinstance(getattr(bpy.data, p, None), bpy_prop_collection)
        ),
    )


def launch_blender(
    file_path: str = "", steam_app_id: str = "365670", is_admin: bool = False
):
    """
    启动Blender, 支持steam与常规安装, 支持管理员启动
    """

    # get blender.exe path
    blender_exe = bpy.app.binary_path

    # launch
    if "steamapps" in blender_exe:
        # steam安装
        command = ["steam", "-applaunch", steam_app_id]
        if file_path:
            command.append(file_path)
        subprocess.Popen(command)
    else:
        # 常规安装
        parameter = f'"{file_path}"' if file_path else file_path
        if is_admin:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", blender_exe, parameter, None, 0
            )
        else:
            ctypes.windll.shell32.ShellExecuteW(
                None, "open", blender_exe, parameter, None, 0
            )


def wait_for_new_file(file_path, timestamp, timeout=None):
    """
    等待新文件出现在指定路径
    """
    start_time = time.time()
    while True:
        if os.path.exists(file_path) and os.path.getctime(file_path) > timestamp:
            return True
        elif timeout is not None and (time.time() - start_time) > timeout:
            return False
        else:
            time.sleep(0.1)
