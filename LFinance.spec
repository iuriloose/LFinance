# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

block_cipher = None
project_dir = Path.cwd()


a = Analysis(
    ['main.py'],
    pathex=[str(project_dir)],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# O Windows já fornece as DLLs de "API set" e o runtime UCRT. Empacotá-las
# junto com o aplicativo faz o carregador do Windows preferi-las às DLLs do
# sistema e impede o Qt de iniciar em alguns computadores.
def manter_binario(binary):
    nome = Path(binary[0]).name.lower()
    bloqueadas = {'ucrtbase.dll', 'icudt78.dll', 'icuuc.dll', 'libcrypto-3-x64.dll', 'libssl-3-x64.dll'}
    return nome not in bloqueadas and not nome.startswith('api-ms-win-')


binarios_necessarios = [binary for binary in a.binaries if manter_binario(binary)]

exe = EXE(
    pyz,
    a.scripts,
    [],
    name='LFinance',
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
    icon='assets/logo.ico',
    version='version_info.txt',
)

coll = COLLECT(
    exe,
    binarios_necessarios,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LFinance',
)
