"""macOS-only helper: run as a background "accessory" app.

An accessory app has no Dock icon and never becomes the *active* application, so
popping up a speech bubble or a celebration never steals keyboard focus from
whatever the user is doing (typing in another app, etc.).

Implemented with the Objective-C runtime via ``ctypes`` so it needs no extra
dependencies. It is a best-effort no-op on non-macOS platforms or on failure.
"""
from __future__ import annotations

import ctypes
import ctypes.util
import sys

# NSApplicationActivationPolicyAccessory
_ACCESSORY = 1


def set_accessory_activation_policy() -> None:
    if sys.platform != "darwin":
        return
    try:
        lib = ctypes.util.find_library("objc")
        if not lib:
            return
        objc = ctypes.cdll.LoadLibrary(lib)
        objc.objc_getClass.restype = ctypes.c_void_p
        objc.objc_getClass.argtypes = [ctypes.c_char_p]
        objc.sel_registerName.restype = ctypes.c_void_p
        objc.sel_registerName.argtypes = [ctypes.c_char_p]

        send = objc.objc_msgSend
        send.restype = ctypes.c_void_p
        send.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        app_class = objc.objc_getClass(b"NSApplication")
        shared = send(app_class, objc.sel_registerName(b"sharedApplication"))
        if not shared:
            return

        # -[NSApplication setActivationPolicy:(NSInteger)] -> BOOL
        send.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long]
        send.restype = ctypes.c_bool
        send(shared, objc.sel_registerName(b"setActivationPolicy:"), _ACCESSORY)
    except Exception:
        pass
