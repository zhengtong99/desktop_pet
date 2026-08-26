# PyInstaller spec: builds a standalone, double-clickable Desktop Pet app.
#
#   macOS   -> dist/Desktop Pet.app
#   Windows -> dist/Desktop Pet/Desktop Pet.exe  (one-folder)
#
# Build with:
#   pyinstaller build/desktop_pet.spec --noconfirm
#
# End users never need Python or any of the dev tools installed.

import glob
import os
import sys

from PyInstaller.utils.hooks import collect_all

project_root = os.path.abspath(os.path.join(SPECPATH, ".."))

# Bundle the transparent pet PNGs, the cute font, and sample photos (so the
# first-run seed can copy them into the user's editable folder).
datas = [
    (os.path.join(project_root, "assets", "pets"), "assets/pets"),
    (os.path.join(project_root, "assets", "fonts"), "assets/fonts"),
]
# Seed sample photos AND live-photo videos so their pets aren't pruned.
for _ext in ("*.jpg", "*.mp4", "*.mov", "*.m4v"):
    datas += [(f, "pic") for f in glob.glob(os.path.join(project_root, "pic", _ext))]

# Bundle the AI cut-out engine so users can drop their OWN photos into the
# app's picture folder and have the background removed automatically.
# (The ~176 MB model is downloaded once, on first use, into the user's home.)
binaries = []
hiddenimports = ["lunardate"]
for _pkg in ("rembg", "onnxruntime", "PIL", "imageio", "imageio_ffmpeg"):
    try:
        _d, _b, _h = collect_all(_pkg)
        datas += _d
        binaries += _b
        hiddenimports += _h
    except Exception:
        pass

icon_icns = os.path.join(project_root, "build", "icon.icns")
icon_ico = os.path.join(project_root, "build", "icon.ico")

if sys.platform == "darwin":
    icon = icon_icns if os.path.exists(icon_icns) else None
elif sys.platform.startswith("win"):
    icon = icon_ico if os.path.exists(icon_ico) else None
else:
    icon = None

block_cipher = None

a = Analysis(
    [os.path.join(project_root, "run.py")],
    pathex=[project_root],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["matplotlib", "pyinstaller", "tkinter"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Desktop Pet",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # no terminal window
    disable_windowed_traceback=False,
    argv_emulation=True,     # lets macOS open documents / double-click work well
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Desktop Pet",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="Desktop Pet.app",
        icon=icon,
        bundle_identifier="com.opensource.desktoppet",
        info_plist={
            "CFBundleName": "Desktop Pet",
            "CFBundleDisplayName": "Desktop Pet",
            "CFBundleShortVersionString": "1.0.0",
            "NSHighResolutionCapable": True,
            # Run as a background agent: no Dock icon, no menu bar clutter.
            "LSUIElement": True,
        },
    )
