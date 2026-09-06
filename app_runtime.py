"""Worker commands shared by source and packaged desktop builds"""

import sys
import ctypes
import os
import subprocess
from pathlib import Path
from contextlib import contextmanager

def worker_arguments(worker, arguments):
    arguments = [str(argument) for argument in arguments]

    if getattr(sys, "frozen", False):
        return ["--worker", worker, *arguments]

    entry = Path(__file__).resolve().parent / "app.py"
    return [
        "-u", "-B", "-X", "utf8",
        str(entry), "--worker", worker, *arguments,
    ]

@contextmanager
def external_program_environment():
    """Keep bundled DLL search paths out of external programs"""
    if not getattr(sys, "frozen", False) or sys.platform != "win32":
        yield
        return

    bundle = Path(sys._MEIPASS).resolve()
    original_path = os.environ.get("PATH")
    set_directory = ctypes.windll.kernel32.SetDllDirectoryW
    set_directory.argtypes = [ctypes.c_wchar_p]
    set_directory.restype = ctypes.c_int

    def outside_bundle(value):
        if not value:
            return True
        path = Path(value.strip('"')).resolve()
        return path != bundle and bundle not in path.parents

    try:
        os.environ["PATH"] = os.pathsep.join(
            value
            for value in (original_path or "").split(os.pathsep)
            if outside_bundle(value)
        )
        if not set_directory(None):
            raise ctypes.WinError()
        yield
    finally:
        if original_path is None:
            os.environ.pop("PATH", None)
        else:
            os.environ["PATH"] = original_path
        set_directory(str(bundle))

def run_external(*args, **kwargs):
    if sys.platform == "win32":
        kwargs["creationflags"] = kwargs.get("creationflags", 0) | subprocess.CREATE_NO_WINDOW
    with external_program_environment():
        return subprocess.run(*args, **kwargs)

def application_directory():
    """Writeable portable-app directory or source project directory"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

def resource_directory():
    """Bundled resources live in _internal in the packaged build"""
    return Path(__file__).resolve().parent

def worker_executable():
    if getattr(sys, "frozen", False):
        return str(application_directory() / "R6Worker.exe")
    return sys.executable