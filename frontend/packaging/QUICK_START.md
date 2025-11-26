# Quick Start: Building macOS DMG from Windows

## ⚠️ Important Limitation

**You CANNOT build macOS apps (.dmg) on Windows directly.** macOS apps require macOS build tools.

## ✅ Best Solution: GitHub Actions (Free & Automatic)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Prepare for macOS build"
git push origin main
```

### Step 2: Create Release Tag
```bash
git tag v1.0.0
git push origin v1.0.0
```

### Step 3: Wait for Build
- Go to your GitHub repo
- Click "Actions" tab
- Wait for "Build macOS Application" workflow to complete (~5-10 minutes)

### Step 4: Download DMG
- Go to "Releases" in your GitHub repo
- Download the `.dmg` file
- That's it! 🎉

## Alternative: Use a Mac

If you have access to a Mac:

```bash
# 1. Build frontend
cd frontend
npm install
npm run build

# 2. Build macOS app
cd packaging/electron-app
npm install
npm run build:mac

# 3. Find DMG
# Location: frontend/packaging/electron-app/dist/PSI Forecast System-1.0.0.dmg
```

## What's Configured

✅ Electron app structure  
✅ macOS DMG configuration  
✅ GitHub Actions workflow  
✅ App icon support  
✅ Frontend bundling  
✅ Backend integration (runs separately)

## File Structure

```
frontend/packaging/
├── electron-app/
│   ├── main.js              # Electron main process
│   ├── preload.js          # Security script
│   ├── package.json       # Build config
│   ├── icons.icns         # App icon
│   └── build/              # Build resources
├── README.md               # Detailed docs
├── BUILD_MACOS.md          # Full instructions
└── build-instructions.md    # Step-by-step guide
```

## Next Steps

1. **Use GitHub Actions** (recommended) - just push and tag!
2. Or use a Mac to build locally
3. Test the DMG on macOS

The configuration is ready - you just need a macOS environment to build!

