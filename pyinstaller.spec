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

# Admin privilege manifest
manifest_content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="1.0.0.0"
    processorArchitecture="*"
    name="AiFilePrefetcher"
    type="win32"
  />
  <description>AI File Prefetcher - Intelligent File Prefetching</description>

  <dependency>
    <dependentAssembly>
      <assemblyIdentity
        type="win32"
        name="Microsoft.Windows.Common-Controls"
        version="6.0.0.0"
        processorArchitecture="*"
        publicKeyToken="6595b64144ccf1df"
        language="*"
      />
    </dependentAssembly>
  </dependency>

  <!-- REQUEST ADMINISTRATOR PRIVILEGES -->
  <requestedPrivileges>
    <requestedExecutionLevel level="requireAdministrator" uiAccess="false"/>
  </requestedPrivileges>

  <!-- DPI Awareness for modern Windows -->
  <asmv3:application xmlns:asmv3="http://schemas.microsoft.com/compatibility/windows/1">
    <asmv3:windowsSettings xmlns="http://schemas.microsoft.com/compatibility/windows/1">
      <dpiAware>true</dpiAware>
    </asmv3:windowsSettings>
  </asmv3:application>

</assembly>
"""

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
        'psutil',
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
    manifest=manifest_content,  # Enable admin privilege request
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
