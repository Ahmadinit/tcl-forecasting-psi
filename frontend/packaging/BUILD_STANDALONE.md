# Building Fully Standalone macOS Application

This guide explains how to build a fully standalone macOS application that includes both the frontend and backend.

## Overview

The standalone app includes:
- ✅ Electron frontend (React app)
- ✅ Python backend (bundled as executable)
- ✅ SQLite database (stored in user's app data)
- ✅ All dependencies bundled

## Prerequisites

### For Building on macOS:

1. **macOS machine** (required for building macOS apps)
2. **Node.js 18+**
3. **Python 3.8+**
4. **Xcode Command Line Tools**:
   ```bash
   xcode-select --install
   ```

## Build Process

### Step 1: Build the Python Backend

```bash
cd backend/packaging
chmod +x build_backend_macos.sh
./build_backend_macos.sh
```

This creates: `backend/packaging/dist/psi-backend-macos`

### Step 2: Build the Frontend

```bash
cd frontend
npm install
npm run build
```

This creates: `frontend/dist/` (React app bundle)

### Step 3: Build the Electron App

```bash
cd frontend/packaging/electron-app
npm install
npm run build:mac
```

This creates: `frontend/packaging/electron-app/dist/PSI Forecast System-1.0.0.dmg`

## Complete Build Script

Create `build-standalone.sh` in the project root:

```bash
#!/bin/bash
set -e

echo "🔨 Building Standalone PSI Forecast System..."

# Build backend
echo "📦 Step 1: Building Python backend..."
cd backend/packaging
chmod +x build_backend_macos.sh
./build_backend_macos.sh
cd ../..

# Build frontend
echo "🎨 Step 2: Building React frontend..."
cd frontend
npm install
npm run build
cd ..

# Build Electron app
echo "⚡ Step 3: Building Electron app..."
cd frontend/packaging/electron-app
npm install
npm run build:mac
cd ../../..

echo "✅ Build complete!"
echo "📍 DMG location: frontend/packaging/electron-app/dist/PSI Forecast System-1.0.0.dmg"
```

Make it executable and run:
```bash
chmod +x build-standalone.sh
./build-standalone.sh
```

## Using GitHub Actions

The GitHub Actions workflow (`.github/workflows/build-macos.yml`) can be updated to build the backend too:

```yaml
- name: Build Python Backend
  run: |
    cd backend/packaging
    chmod +x build_backend_macos.sh
    ./build_backend_macos.sh
```

## What Gets Bundled

### Frontend
- React app (built with Vite)
- All static assets
- Electron main process

### Backend
- Python executable (`psi-backend`)
- All Python dependencies
- FastAPI application
- All routers and utilities

### Database
- SQLite database stored in:
  - `~/Library/Application Support/PSI Forecast System/data/psi.db`
- Created automatically on first run
- Persists between app launches

## App Structure (Bundled)

```
PSI Forecast System.app/
├── Contents/
│   ├── MacOS/
│   │   └── PSI Forecast System (Electron)
│   └── Resources/
│       ├── app/              # Frontend bundle
│       └── backend/
│           └── psi-backend   # Python backend executable
└── ...
```

## Testing the Standalone App

1. **Mount the DMG**: Double-click `PSI Forecast System-1.0.0.dmg`
2. **Install**: Drag app to Applications folder
3. **Run**: Launch from Applications
4. **Verify**:
   - App window opens
   - Backend starts automatically (check Console.app for logs)
   - Database is created in app data directory
   - All features work

## Troubleshooting

### Backend Not Starting

- Check Console.app for error messages
- Verify executable exists: `ls -lh "~/Library/Application Support/PSI Forecast System/"`
- Check permissions: `chmod +x` on backend executable

### Database Issues

- Database location: `~/Library/Application Support/PSI Forecast System/data/psi.db`
- Check if directory exists and is writable
- Delete database to reset (if needed)

### Import Errors

- Ensure all Python dependencies are in `requirements.txt`
- Check `pyinstaller.spec` for missing `hiddenimports`
- Rebuild backend after adding dependencies

## Distribution

The DMG file can be distributed to users. They can:
1. Download the DMG
2. Mount it
3. Drag app to Applications
4. Run the app (no Python/Node.js installation needed)

## Size Considerations

- Frontend bundle: ~5-10 MB
- Backend executable: ~50-100 MB (includes Python runtime)
- Total app size: ~100-150 MB

## Security Notes

- Backend runs on `127.0.0.1` (localhost only)
- Database stored in user's app data directory
- No external network access required
- All data stays on user's machine

