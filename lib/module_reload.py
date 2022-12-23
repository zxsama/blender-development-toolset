# -*- coding:UTF-8 -*-

"""A hot reloader for python3.
"""

# __author__ = "KenLee"
# __email__ = "hellokenlee@163.com"


import os
import sys
import time
import types
import inspect
import importlib
from .reset_module import reset_module

_module_timestamps = {}
_previous_scan_time = time.time() - 1.0


def _is_code_module(module):
    """
    """
    try:
        src_path = inspect.getsourcefile(module)
        if src_path is None:
            src_path = inspect.getfile(module)
            if src_path:
                import sys
                src_path = os.path.join(sys.path[0], src_path.replace(".", "/") + ".py")
        return src_path
    except TypeError:
        return ""
    pass


def modified(path=None):
    """
    """
    global _previous_scan_time
    modules = []

    default_time = (_previous_scan_time, False)

    pyc_ext = ".pyc" or ".pyo"

    if path is None:

        for name, module in sys.modules.items():
            filename = _is_code_module(module)
            if not filename:
                continue

            filename = os.path.normpath(filename)

            prev_time, prev_scan = _module_timestamps.setdefault(name, default_time)

            # Get timestamp of .pyc if this is first time checking this module
            if not prev_scan:
                pyc_name = os.path.splitext(filename)[0] + pyc_ext
                try:
                    prev_time = os.path.getmtime(pyc_name)
                except OSError:
                    pass
                _module_timestamps[name] = (prev_time, True)

            # Get timestamp of source file
            try:
                disk_time = os.path.getmtime(filename)
            except OSError:
                disk_time = None

            if disk_time is not None and prev_time < disk_time:
                _module_timestamps[name] = (disk_time, True)
                modules.append(name)
    else:

        filename = os.path.splitext(path)[0]

        name = filename.replace("/", ".")

        prev_time, prev_scan = _module_timestamps.setdefault(name, default_time)

        try:
            disk_time = os.path.getmtime(sys.path[0] + "/" + filename + pyc_ext)
        except OSError:
            disk_time = None

        if disk_time is not None:
            if not prev_scan or prev_time < disk_time:
                _module_timestamps[name] = (disk_time, True)
                modules.append(name)

    _previous_scan_time = time.time()
    return modules


def _function_reloader(oldfunc, newfunc, depth):
    setattr(oldfunc, "__code__", newfunc.__code__)
    setattr(oldfunc, "__defaults__", newfunc.__defaults__)
    setattr(oldfunc, "__doc__", newfunc.__doc__)
    #
    print("  " * depth + "[U] %s : %s" % (oldfunc.__name__, str(oldfunc)))
    pass


def _method_reloader(oldmethod, newmethod, depth):
    _function_reloader(oldmethod.__func__, newmethod.__func__, depth)
    pass


def _class_reloader(oldclass, newclass, depth):
    depth = depth + 1
    for key, val in newclass.__dict__.items():
        #
        if key not in oldclass.__dict__:
            setattr(oldclass, key, val)
            print("  " * depth + "[ADD] %s : %s" % (key, str(val)))
            continue
        #
        oldval = oldclass.__dict__[key]
        #
        if type(oldval) != type(val):
            continue
        #
        reloader = _reloaders.get(type(val))
        #
        if reloader:
            reloader(oldval, val, depth)
        else:
            print("  " * depth + "[IGNORE] %s : %s" % (key, str(val)))
    pass


_reloaders = {
    type: _class_reloader,
    types.MethodType: _method_reloader,
    types.FunctionType: _function_reloader,
}


def reload():
    modnames = modified()
    if len(modnames) > 0:
        print(">" * 10 + " Reload " + ">" * 10)
        for modname in modnames:
            if modname in sys.modules:
                #
                module = sys.modules[modname]
                #
                old_module = {}
                for key, obj in module.__dict__.items():
                    old_module[key] = obj
                #
                print("[UPDATE] %s" % modname)
                reset_module(module)
                new_module = module
                # new_module = importlib.reload(module)
                #
                for key, newobj in new_module.__dict__.items():
                    if key not in old_module:
                        print("  [ADD] %s : %s" % (key, str(newobj)))
                        continue
                    oldobj = old_module[key]
                    if type(newobj) != type(oldobj):
                        new_module.__dict__[key] = oldobj
                        print("  [CHANGE] %s : %s" % (key, str(oldobj)))
                        continue
                    reloader = _reloaders.get(type(oldobj))
                    if reloader:
                        print("  [UPDATE] %s : %s" % (key, str(oldobj)))
                        reloader(oldobj, newobj, 2)
                    new_module.__dict__[key] = oldobj
        # importlib.invalidate_caches()
        print("<" * 10 + " Reload " + "<" * 10)
    pass
