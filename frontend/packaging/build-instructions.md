# Build Instructions for macOS Application

## Important: Building from Windows

**You cannot build macOS applications (.dmg) directly on Windows.** macOS apps require:
- macOS-specific build tools
- Apple code signing certificates
- macOS file system

## Solutions for Windows Users

### Option 1: GitHub Actions (Recommended - Free)

1. **Push your code to GitHub**
2. **Create a release tag**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. **GitHub Actions will automatically build the DMG**
4. **Download from Releases page**: Go to your GitHub repo → Releases → Download the `.dmg` file

The workflow file is already created at `.github/workflows/build-macos.yml`

### Option 2: Use a Mac (Physical or VM)

If you have access to a Mac:

1. **Transfer project to Mac** (via Git, USB, etc.)

2. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   
   cd packaging/electron-app
   npm install
   ```

3. **Build frontend**:
   ```bash
   cd ../../  # Back to frontend root
   npm run build
   ```

4. **Build macOS app**:
   ```bash
   cd packaging/electron-app
   npm run build:mac
   ```

5. **Find the DMG**: `frontend/packaging/electron-app/dist/PSI Forecast System-1.0.0.dmg`

### Option 3: macOS Virtual Machine

1. Install macOS on VMware/VirtualBox (requires macOS license)
2. Follow Option 2 steps inside the VM

## Project Structure

```
psi-app/
├── frontend/
│   ├── dist/                    # Built frontend (created by npm run build)
│   └── packaging/
│       └── electron-app/
│           ├── main.js          # Electron main process
│           ├── preload.js       # Security preload script
│           ├── package.json     # Electron config
│           ├── icons.icns       # App icon
│           ├── build/           # Build resources
│           │   ├── entitlements.mac.plist
│           │   └── background.png
│           └── dist/            # Output: DMG will be here
├── backend/                     # Backend runs separately
└── .github/
    └── workflows/
        └── build-macos.yml      # GitHub Actions workflow
```

## Next Steps

1. **If using GitHub Actions**: Just push and tag - it's automatic!
2. **If using a Mac**: Follow Option 2 above
3. **Test the DMG**: Mount it, install the app, ensure backend is running

## Notes

- Backend runs separately (not bundled in the app)
- Users need to start backend manually: `cd backend && uvicorn main:app`
- For fully standalone app, you'd need to bundle Python backend (complex)

