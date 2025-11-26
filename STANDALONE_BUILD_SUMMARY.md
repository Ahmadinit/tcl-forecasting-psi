# Fully Standalone macOS Application - Complete Setup ✅

## Overview

Your PSI Forecast System is now configured to build as a **fully standalone macOS application** that includes:
- ✅ Electron frontend (React app)
- ✅ Python backend (bundled as executable)
- ✅ SQLite database (stored in user's app data)
- ✅ All dependencies bundled
- ✅ No external dependencies required

## What Was Configured

### 1. Backend Packaging (`backend/packaging/`)

- **`pyinstaller.spec`**: PyInstaller configuration to bundle Python backend
- **`build_backend_macos.sh`**: Build script for macOS backend executable
- **`README.md`**: Documentation for backend packaging

### 2. Database Configuration (`backend/database.py`)

- Updated to detect if running as bundled executable
- Uses user's app data directory for database:
  - macOS: `~/Library/Application Support/PSI Forecast System/data/psi.db`
- Automatically creates directories if needed

### 3. CORS Configuration (`backend/main.py`)

- Updated to allow all origins (for Electron app)
- Supports both development and production modes
- Added command-line argument support for host/port

### 4. Electron Integration (`frontend/packaging/electron-app/`)

- **`main.js`**: Updated to:
  - Auto-start bundled backend executable
  - Handle backend lifecycle (start/stop)
  - Proper error handling and logging
  - Support both dev and production modes

- **`package.json`**: Updated to include backend executable in bundle

### 5. Build Scripts

- **`build-standalone.sh`**: Complete build script (root directory)
- **`.github/workflows/build-macos.yml`**: Updated GitHub Actions workflow

### 6. Documentation

- **`frontend/packaging/BUILD_STANDALONE.md`**: Complete standalone build guide
- **`backend/packaging/README.md`**: Backend packaging documentation

## How to Build

### Option 1: Complete Build Script (Recommended)

```bash
chmod +x build-standalone.sh
./build-standalone.sh
```

This will:
1. Build Python backend executable
2. Build React frontend
3. Package everything into DMG

### Option 2: Step-by-Step

```bash
# 1. Build backend
cd backend/packaging
chmod +x build_backend_macos.sh
./build_backend_macos.sh

# 2. Build frontend
cd ../../frontend
npm install
npm run build

# 3. Build Electron app
cd packaging/electron-app
npm install
npm run build:mac
```

### Option 3: GitHub Actions

1. Push to GitHub
2. Create release tag: `git tag v1.0.0 && git push origin v1.0.0`
3. GitHub Actions will build automatically
4. Download DMG from Releases page

## File Structure (After Build)

```
PSI Forecast System.app/
├── Contents/
│   ├── MacOS/
│   │   └── PSI Forecast System (Electron executable)
│   └── Resources/
│       ├── app/                    # Frontend bundle
│       │   ├── index.html
│       │   └── assets/
│       └── backend/
│           └── psi-backend         # Python backend executable
└── ...

Database Location:
~/Library/Application Support/PSI Forecast System/data/psi.db
```

## Key Features

### ✅ Fully Standalone
- No Python installation required
- No Node.js installation required
- All dependencies bundled

### ✅ Auto-Start Backend
- Backend starts automatically when app launches
- Runs on `127.0.0.1:8000` (localhost only)
- Stops automatically when app closes

### ✅ Persistent Database
- Database stored in user's app data directory
- Persists between app launches
- Automatically created on first run

### ✅ Cross-Architecture Support
- Builds for both Intel (x64) and Apple Silicon (ARM64)
- Universal binary support

## Testing

1. **Mount DMG**: Double-click `PSI Forecast System-1.0.0.dmg`
2. **Install**: Drag app to Applications
3. **Run**: Launch from Applications
4. **Verify**:
   - App window opens
   - Backend starts (check Console.app for logs)
   - Database created automatically
   - All features work

## Troubleshooting

### Backend Not Starting
- Check Console.app: `Console.app` → Search for "psi-backend"
- Verify executable exists in app bundle
- Check permissions: `chmod +x` on backend executable

### Database Issues
- Location: `~/Library/Application Support/PSI Forecast System/data/psi.db`
- Check directory permissions
- Delete database to reset (if needed)

### Import Errors
- Ensure all dependencies in `requirements.txt`
- Check `pyinstaller.spec` for missing `hiddenimports`
- Rebuild after adding dependencies

## Distribution

The DMG file can be distributed to users:
1. Users download DMG
2. Mount and drag to Applications
3. Run app (no setup required)
4. Database created automatically on first run

## Size

- Frontend: ~5-10 MB
- Backend: ~50-100 MB (includes Python runtime)
- Total: ~100-150 MB

## Security

- Backend runs on localhost only (`127.0.0.1`)
- No external network access
- All data stored locally
- No cloud dependencies

## Next Steps

1. ✅ Configuration complete
2. ⏭️ Build on macOS (use GitHub Actions or Mac)
3. ⏭️ Test the standalone app
4. ⏭️ Distribute DMG to users

## Files Created/Updated

### New Files:
- `backend/packaging/pyinstaller.spec`
- `backend/packaging/build_backend_macos.sh`
- `backend/packaging/README.md`
- `frontend/packaging/BUILD_STANDALONE.md`
- `build-standalone.sh`
- `STANDALONE_BUILD_SUMMARY.md`

### Updated Files:
- `backend/database.py` - User data directory support
- `backend/main.py` - CORS and CLI args
- `frontend/packaging/electron-app/main.js` - Backend auto-start
- `frontend/packaging/electron-app/package.json` - Include backend
- `.github/workflows/build-macos.yml` - Backend build step

## Status: READY TO BUILD 🚀

Everything is configured for a fully standalone macOS application. Build using GitHub Actions or on a Mac!

