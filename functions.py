import bpy

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