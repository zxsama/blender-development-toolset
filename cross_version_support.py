import bpy

bl_version = bpy.app.version

def language_zh_code():
    if bl_version >= (4,0,0):
        zh_code = "zh_HANS"
    else:
        zh_code = "zh_CN"
    return zh_code