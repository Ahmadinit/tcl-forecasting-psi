# PSI Forecast System - macOS Packaging

This directory contains the Electron packaging configuration for creating a macOS standalone application (.dmg).

## Structure

```
packaging/
  electron-app/
    ├── main.js              # Electron main process
    ├── preload.js          # Preload script (security)
    ├── package.json        # Electron app configuration
    ├── icons.icns          # macOS app icon
    ├── build/              # Build resources
    │   ├── entitlements.mac.plist  # macOS entitlements
    │   └── background.png  # DMG background image (optional)
    └── dist/               # Output directory (DMG will be here)
```

## Prerequisites

1. **macOS Machine Required**: You cannot build macOS apps on Windows. You need:
   - A physical Mac, OR
   - A macOS virtual machine, OR
   - GitHub Actions with macOS runner

2. **Node.js 18+** installed

3. **Dependencies**:
   ```bash
   cd frontend/packaging/electron-app
   npm install
   ```

## Building the macOS App

### Step 1: Build the Frontend

```bash
cd frontend
npm install
npm run build
```

This creates the production build in `frontend/dist/`

### Step 2: Build the macOS DMG

```bash
cd frontend/packaging/electron-app
npm run build:mac
```

The `.dmg` file will be created in `frontend/packaging/electron-app/dist/`

## Building from Windows

Since you cannot build macOS apps on Windows, use one of these options:

### Option 1: GitHub Actions (Recommended)

1. Push your code to GitHub
2. Create a release tag: `git tag v1.0.0 && git push origin v1.0.0`
3. GitHub Actions will automatically build the DMG
4. Download the DMG from the release page

### Option 2: macOS Virtual Machine

1. Set up macOS on VMware/VirtualBox
2. Transfer your project to the VM
3. Follow the build steps above

### Option 3: Physical Mac

1. Transfer project to Mac (via Git, USB, etc.)
2. Follow the build steps above

## Configuration

### App Information

Edit `package.json` to customize:
- `name`: App name
- `version`: App version
- `appId`: Unique identifier (e.g., `com.psi.forecast.system`)
- `productName`: Display name

### Icon

Replace `icons.icns` with your app icon (512x512 PNG converted to .icns)

### DMG Customization

Edit `package.json` → `build.dmg` section to customize:
- Background image
- Window size
- Icon positions

## Backend Integration

**Important**: The Electron app loads the frontend, but the backend runs separately.

**Options**:
1. **Separate Backend**: User runs backend separately (current setup)
2. **Bundled Backend**: Package Python backend with Electron (complex, requires PyInstaller)
3. **Cloud Backend**: Use a hosted backend API

For production, consider:
- Providing backend installer separately
- Using a cloud-hosted backend
- Bundling backend with PyInstaller (advanced)

## Testing

After building:
1. Mount the DMG file
2. Drag app to Applications folder
3. Run the app
4. Ensure backend is running on `http://127.0.0.1:8000`

## Troubleshooting

- **"Cannot build on Windows"**: Use GitHub Actions or macOS VM
- **"Icon not found"**: Ensure `icons.icns` exists
- **"Frontend not loading"**: Check that `frontend/dist` was built
- **"Backend connection failed"**: Start backend separately

