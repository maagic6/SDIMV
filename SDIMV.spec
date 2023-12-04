# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['SDIMV.py'],
    pathex=[],
    binaries=[],
    datas=[('icon/add.png', 'icon'),
       ('icon/clear.png', 'icon'),
       ('icon/remove.png', 'icon'),
       ('icon/icon.ico', 'icon'),
       ('icon/about.png','icon')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5','numpy','numpy.libs','win32ui','PyQt6.Qt6OpenGL','PyQt6.Qt6OpenGLWidgets','Pythonwin'],
    noarchive=False,
)

to_keep = []
to_exclude = {'opengl32sw.dll','Qt6Pdf.dll','Qt6OpenGL.dll','Qt6OpenGLWidgets.dll','QtOpenGL.pyd','QtOpenGLWidgets.pyd','ffmpegmediaplugin.dll','MSVCP140.dll', 'MSVCP140_1.dll', 'MSVCP140_2.dll', 'libcrypto-1_1.dll', 'VCRUNTIME140.dll', 'VCRUNTIME140_1.dll','mfc140u.dll'}

for (dest, source, kind) in a.binaries:
    if os.path.split(dest)[1] in to_exclude:
        continue
    to_keep.append((dest, source, kind))

# Replace list of data files with filtered one.
a.binaries = to_keep

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SDIMV',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon/icon.ico']
)