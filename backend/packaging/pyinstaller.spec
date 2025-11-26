# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Get the backend directory
backend_dir = Path(os.getcwd())
sys.path.insert(0, str(backend_dir))

sys.path.insert(0, str(backend_dir))

a = Analysis(
    [str(backend_dir / 'main.py')],
    pathex=[str(backend_dir)],
    binaries=[],
    datas=[
        (str(backend_dir / 'routers'), 'routers'),
        (str(backend_dir / 'utils'), 'utils'),
        (str(backend_dir / 'config.py'), '.'),
        (str(backend_dir / 'database.py'), '.'),
        (str(backend_dir / 'models.py'), '.'),
        (str(backend_dir / 'schemas.py'), '.'),
    ],
    hiddenimports=[
        'uvicorn',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.logging',
        'fastapi',
        'fastapi.middleware',
        'fastapi.middleware.cors',
        'sqlalchemy',
        'sqlalchemy.orm',
        'sqlalchemy.ext.declarative',
        'pydantic',
        'pandas',
        'numpy',
        'sklearn',
        'openpyxl',
        'reportlab',
        'routers.auth',
        'routers.dashboard',
        'routers.export',
        'routers.inventory',
        'routers.models_api',
        'routers.monthly_plan',
        'routers.purchase',
        'routers.sales',
        'routers.settings_api',
        'routers.shipments',
        'utils.calculations',
        'utils.export_excel',
        'utils.export_pdf',
        'utils.forecast',
        'utils.shipments_helper',
        'utils.weekly_po_generator',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='psi-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

