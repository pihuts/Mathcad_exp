# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Mathcad Automator

Build with: pyinstaller main.spec --clean
Output: dist/MathcadAutomator/
"""

from PyInstaller.utils.hooks import collect_submodules

# Collect all uvicorn submodules (many are dynamically imported)
uvicorn_imports = collect_submodules('uvicorn')

# Additional hidden imports required for the application
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
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('frontend/dist', 'frontend/dist'),  # Frontend static files
        ('src', 'src'),  # Source modules
    ],
    hiddenimports=uvicorn_imports + additional_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'numpy.testing',
        'pytest',
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
    console=True,  # Keep True for debugging; set False in 05-04
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
    name='MathcadAutomator',
)
