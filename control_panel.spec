# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\gui\\control_panel.py'],
    pathex=[],
    binaries=[],
    datas=[('src\\utils\\config.json', 'utils'), ('src\\Doc\\Doc_config.json', 'Doc')],
    hiddenimports=['tkinter', 'PIL', 'PIL.Image', 'PIL.ImageTk', 'PIL.ImageFont', 'PIL.ImageDraw'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='control_panel',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
