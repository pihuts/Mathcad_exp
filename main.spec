# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Mathcad Automator - Production Build

Build with: pyinstaller main.spec --clean
Output: dist/MathcadAutomator/
"""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import os

# Collect all uvicorn submodules
uvicorn_imports = collect_submodules('uvicorn')

# Collect pywebview submodules
webview_imports = collect_submodules('webview')

# Additional hidden imports
additional_imports = [
    # pywin32/COM support
    'win32timezone',
    'win32com',
    'win32com.client',
    'comtypes',
    'comtypes.client',

    # Pydantic
    'pydantic',
    'pydantic_core',

    # FastAPI and dependencies
    'fastapi',
    'starlette',
    'starlette.staticfiles',
    'starlette.routing',
    'anyio',
    'anyio._backends',
    'anyio._backends._asyncio',

    # tkinter for file dialogs
    'tkinter',
    'tkinter.filedialog',

    # MathcadPy
    'MathcadPy',

    # pywebview dependencies
    'webview',
    'clr',
    'System',
    'System.Windows.Forms',
    'System.Drawing',
    'System.Threading',

    # psutil for process management
    'psutil',
]

# Collect pywebview data files
webview_datas = collect_data_files('webview')

# Check if icon exists
icon_path = 'assets/icon.ico' if os.path.exists('assets/icon.ico') else None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('frontend/dist', 'frontend/dist'),
        ('src', 'src'),
    ] + webview_datas,
    hiddenimports=uvicorn_imports + webview_imports + additional_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'numpy.testing',
        'pytest',
        'IPython',
        'jupyter',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MathcadAutomator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # PRODUCTION: No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,  # Application icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MathcadAutomator',
)
