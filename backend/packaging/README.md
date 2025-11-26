# Backend Packaging for macOS

This directory contains scripts and configuration for bundling the Python backend into a standalone executable.

## Overview

The backend is packaged using PyInstaller to create a standalone executable that can be bundled with the Electron app.

## Structure

```
backend/packaging/
├── pyinstaller.spec      # PyInstaller configuration
├── build_backend_macos.sh # Build script for macOS
└── dist/                 # Output directory (executable will be here)
```

## Building the Backend

### Prerequisites

- Python 3.8+ installed
- All backend dependencies installed

### Build Steps

1. **Run the build script**:
   ```bash
   cd backend/packaging
   chmod +x build_backend_macos.sh
   ./build_backend_macos.sh
   ```

2. **Output**:
   - Executable: `backend/packaging/dist/psi-backend-macos`
   - This will be bundled with the Electron app

### Manual Build

If you prefer to build manually:

```bash
cd backend

# Create virtual environment (if not exists)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# Build
pyinstaller --clean packaging/pyinstaller.spec

# Copy to packaging directory
cp dist/psi-backend packaging/dist/psi-backend-macos
chmod +x packaging/dist/psi-backend-macos
```

## Integration with Electron

The bundled backend executable is automatically included in the Electron app build:

1. **Location in Electron app**: `resources/backend/psi-backend`
2. **Auto-start**: The Electron app automatically starts the backend when launched
3. **Database**: Stored in user's app data directory:
   - macOS: `~/Library/Application Support/PSI Forecast System/data/psi.db`

## Testing the Executable

You can test the standalone backend executable:

```bash
cd backend/packaging/dist
./psi-backend-macos --host 127.0.0.1 --port 8000
```

Then visit `http://127.0.0.1:8000` in your browser.

## Troubleshooting

### Build Fails

- Ensure all dependencies are installed
- Check Python version (3.8+)
- Verify PyInstaller is installed: `pip install pyinstaller`

### Executable Not Found

- Check that build completed successfully
- Verify file exists: `ls -lh packaging/dist/psi-backend-macos`
- Ensure file is executable: `chmod +x packaging/dist/psi-backend-macos`

### Import Errors

- Check `hiddenimports` in `pyinstaller.spec`
- Add missing modules to `hiddenimports` list
- Rebuild after adding imports

## Notes

- The executable is platform-specific (macOS only)
- For Windows/Linux, create separate build scripts
- Database is stored in user's app data directory for persistence
- Backend runs on `127.0.0.1:8000` by default

