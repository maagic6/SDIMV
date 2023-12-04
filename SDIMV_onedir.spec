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
to_exclude = {'opengl32sw.dll','Qt6Pdf.dll','Qt6OpenGL.dll','Qt6OpenGLWidgets.dll','ffmpegmediaplugin.dll','MSVCP140.dll', 'MSVCP140_1.dll', 'MSVCP140_2.dll', 'libcrypto-1_1.dll', 'VCRUNTIME140.dll', 'VCRUNTIME140_1.dll','mfc140u.dll', 'qt_gl.qm', 'qt_sl.qm', 'qtbase_de.qm', 'qtbase_pt_BR.qm', 'qtbase_ca.qm', 'qtbase_nl.qm', 'qtbase_nn.qm', 'qtbase_tr.qm', 'qtbase_gd.qm', 'qtbase_da.qm', 'qtbase_fi.qm', 'qtbase_cs.qm'}

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
    [],
    exclude_binaries=True,
    name='SDIMV',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SDIMV',
)
