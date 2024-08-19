import bpy
import subprocess
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


def launch_blender(file_path: str = "", steam_app_id: str = "365670"):

    # get blender.exe path
    blender_exe = bpy.app.binary_path

    # launch
    if "steamapps" in blender_exe:
        command = ["steam", "-applaunch", steam_app_id]
    else:
        command = [blender_exe]

    if file_path:
        command.append(file_path)

    subprocess.Popen(command)
