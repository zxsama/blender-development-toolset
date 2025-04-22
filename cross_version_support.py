import sys
import bpy
import subprocess
import ctypes


class VersionPlatformManager:
    def __init__(self):
        self.platform = sys.platform
        self.bl_version = bpy.app.version

    def run_command(
        self,
        needs_admin,
        parameter: list,
        program_path=sys.executable,
    ):

        if sys.platform == "win32":
            operation = "runas" if needs_admin else "open"
            parameter = subprocess.list2cmdline(parameter)
            ctypes.windll.shell32.ShellExecuteW(
                None, operation, program_path, parameter, None, 0
            )

        elif sys.platform == "darwin":
            args = [program_path]
            if parameter:
                args.extend(parameter)
            # if needs_admin:
            #     # 把参数列表转成带引号的字符串，用 shlex 处理特殊字符
            #     quoted_args = [f'"{arg}"' for arg in args]
            #     cmd = f'do shell script "{" ".join(quoted_args)}" with administrator privileges'
            #     subprocess.Popen(["osascript", "-e", cmd])
            # else:
            subprocess.Popen(args)

        elif sys.platform.startswith("linux"):
            # command = ["pkexec", program_path] if needs_admin else [program_path]
            command = [program_path]
            if parameter:
                command.extend(parameter)
            subprocess.Popen(command)


# def language_zh_code():
#     if bl_version < (4,0,0):
#         zh_code = "zh_CN"
#     else:
#         zh_code = "zh_HANS"
#     return zh_code
