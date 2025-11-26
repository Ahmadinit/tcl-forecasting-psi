# Building macOS Application (.dmg) from Windows

## Prerequisites

**Note**: Building macOS applications (.dmg) from Windows requires:
1. A macOS machine (MacBook, iMac, Mac Mini, etc.) OR
2. A macOS virtual machine OR
3. A CI/CD service with macOS runners (GitHub Actions, etc.)

**You cannot build macOS applications directly on Windows** because:
- macOS code signing requires Apple Developer certificates
- DMG creation requires macOS-specific tools
- Electron Builder needs macOS to create .dmg files

## Option 1: Build on macOS Machine

### Steps:

1. **Transfer files to macOS**:
   - Copy the entire `psi-app` folder to your Mac
   - Or use Git to clone/pull the repository

2. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   
   cd packaging/electron-app
   npm install
   ```

3. **Build the frontend**:
   ```bash
   cd ../../  # Back to frontend root
   npm run build
   ```

4. **Build the macOS app**:
   ```bash
   cd packaging/electron-app
   npm run build:mac
   ```

5. **Output**:
   - The `.dmg` file will be in `frontend/packaging/electron-app/dist/`
   - File name: `PSI Forecast System-1.0.0.dmg`

## Option 2: Use GitHub Actions (Recommended for Windows Users)

Create `.github/workflows/build-macos.yml`:

```yaml
name: Build macOS App

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build:
    runs-on: macos-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install Frontend Dependencies
        run: |
          cd frontend
          npm install
      
      - name: Build Frontend
        run: |
          cd frontend
          npm run build
      
      - name: Install Electron Builder Dependencies
        run: |
          cd frontend/packaging/electron-app
          npm install
      
      - name: Build macOS App
        run: |
          cd frontend/packaging/electron-app
          npm run build:mac
      
      - name: Upload DMG
        uses: actions/upload-artifact@v3
        with:
          name: macos-dmg
          path: frontend/packaging/electron-app/dist/*.dmg
```

## Option 3: Use a macOS Virtual Machine

1. Install macOS on VMware/VirtualBox (requires macOS license)
2. Follow Option 1 steps inside the VM

## Current Structure

```
frontend/
  packaging/
    electron-app/
      ├── main.js          # Electron main process
      ├── preload.js       # Preload script
      ├── package.json     # Electron app config
      ├── icons.icns       # App icon (macOS)
      ├── build/           # Build resources
      │   ├── entitlements.mac.plist
      │   └── background.png
      └── dist/            # Output directory (DMG will be here)
```

## Notes

- The app expects the backend to run separately (not bundled)
- For a fully standalone app, you'd need to bundle Python backend (complex)
- The frontend is built and packaged into the Electron app
- Backend should be run separately or use a cloud backend

## Testing

After building, test the app on macOS:
1. Mount the DMG
2. Drag the app to Applications
3. Run the app
4. Make sure backend is running on `http://127.0.0.1:8000`

