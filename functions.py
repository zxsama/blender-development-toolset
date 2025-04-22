import os
import time
import bpy
import subprocess
from bpy.types import bpy_prop_collection
from .cross_version_support import VersionPlatformManager as VP_Manager

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
        parameter = [file_path] if file_path else []
        VPM = VP_Manager()
        VPM.run_command(is_admin, parameter, program_path=blender_exe)


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
