# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# Base path relative to spec file
SPEC_DIR = os.path.abspath(SPECPATH)
PROJECT_ROOT = os.path.abspath(os.path.join(SPEC_DIR, "..", ".."))

datas = [
    (os.path.join(PROJECT_ROOT, "src", "lumina", "templates"), os.path.join("lumina", "templates")),
]

hiddenimports = [
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "cv2",
    "numpy",
    "stl",
    "stl.mesh",
] + collect_submodules("lumina")

a = Analysis(
    [os.path.join(PROJECT_ROOT, "src", "lumina", "gui", "main.py")],
    pathex=[os.path.join(PROJECT_ROOT, "src")],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "scipy"],
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
    name="Lumina",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,  # Native arch (arm64 on Apple Silicon, x86_64 on Intel)
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Lumina",
)

app = BUNDLE(
    coll,
    name="Lumina.app",
    icon=os.path.join(PROJECT_ROOT, "assets", "icons", "lumina.icns"),
    bundle_identifier="com.atacan.lumina",
    info_plist={
        "CFBundleName": "Lumina",
        "CFBundleDisplayName": "Lumina Studio",
        "CFBundleIdentifier": "com.atacan.lumina",
        "CFBundleVersion": "1.1.0",
        "CFBundleShortVersionString": "1.1.0",
        "NSHighResolutionCapable": True,
        "LSMinimumSystemVersion": "12.0",
        "NSRequiresAquaSystemAppearance": False,
        "CFBundlePackageType": "APPL",
        "CFBundleDocumentTypes": [
            {
                "CFBundleTypeName": "Image Files",
                "CFBundleTypeRole": "Viewer",
                "LSItemContentTypes": [
                    "public.jpeg",
                    "public.png",
                    "public.image"
                ]
            }
        ]
    },
)
