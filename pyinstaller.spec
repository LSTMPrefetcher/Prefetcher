# pyinstaller.spec
# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for AI File Prefetcher executable.

Usage:
    pyinstaller pyinstaller.spec --noconfirm
    
This will create:
    dist/AiFilePrefetcher.exe       (executable)
    dist/AiFilePrefetcher/          (one-folder bundle with dependencies)
"""

import os
from pathlib import Path

# Project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Data files and directories to include in the bundle
datas = [
    # Pre-trained models
    (os.path.join(PROJECT_ROOT, 'data', 'models'), 'data/models'),
    # Processed data (vocabularies, etc.)
    (os.path.join(PROJECT_ROOT, 'data', 'processed'), 'data/processed'),
    # Configuration
    (os.path.join(PROJECT_ROOT, 'config', 'config.yaml'), 'config/'),
]

# PyInstaller analysis
a = Analysis(
    ['app_standalone.py'],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # Core dependencies
        'torch',
        'torch.nn',
        'torch.nn.modules',
        'torch.nn.functional',
        'torch.optim',
        'torch.utils',
        'torch.utils.data',
        'yaml',
        'numpy',
        'sqlite3',
        'json',
        'os',
        'sys',
        'subprocess',
        'argparse',
        'logging',
        'pathlib',
        'uuid',
        'datetime',
        'time',
        # Application modules
        'src',
        'src.collector',
        'src.preprocessor',
        'src.trainer',
        'src.prefetcher',
        'src.evaluator',
        'src.model',
        'src.utils',
        'src.first_run',
        'src.persistence',
        'src.lifecycle',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# PYZ archive (Python bytecode)
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None,
)

# EXE (one-file mode)
exe_onefile = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AiFilePrefetcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Show console window (set to False for no console)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# COLLECT (one-folder mode - faster loading than one-file)
coll = COLLECT(
    exe_onefile,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AiFilePrefetcher'
)

# Alternative: For one-file EXE without folder, comment out COLLECT and use exe_onefile directly
# This will be slower to start but easier to distribute (single file)
