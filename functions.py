import bpy
from bpy.types import bpy_prop_collection

def install_modul(self, *modul_name):
    import os
    import sys
    import subprocess

    bpy.ops.wm.console_toggle()  # TODO: 判断控制台是否开启
    for modul in modul_name:
        python_path = os.path.join(sys.prefix, 'bin', 'python.exe')
        print("-" * 30 + "\n未安装" + modul + "模块，安装中...\n")
        subprocess.call([python_path, "-m", "pip", "install", modul])
    print("\n安装结束.\n" + "重启blender后生效!\n" * 3 + "-" * 30)
    self.report({'WARNING'}, "请手动重启blender!")


def collection_search(ID):
    def users(col):
        ret = tuple(repr(o) for o in col if o.user_of_id(ID))
        return ret if ret else None
    return filter(None, (
        users(getattr(bpy.data, p))
        for p in dir(bpy.data)
        if isinstance(
            getattr(bpy.data, p, None),
            bpy_prop_collection
        )))