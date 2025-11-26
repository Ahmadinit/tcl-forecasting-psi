# Step-by-Step Guide: Building macOS App from Windows

Since you're on Windows and want to build a macOS app, here are your options:

## ⚠️ Important: You Cannot Build macOS Apps on Windows

macOS apps require macOS build tools. However, you have these options:

---

## Option 1: GitHub Actions (Recommended - Easiest) ⭐

This is the **easiest and free** way to build from Windows.

### Step 1: Prepare Your Code

1. **Open PowerShell** (or Command Prompt) in your project folder:
   ```
   cd "C:\Users\Lenovo\Desktop\Forecasting Project\psi-app"
   ```

2. **Check if you have Git installed**:
   ```powershell
   git --version
   ```
   If not installed, download from: https://git-scm.com/download/win

3. **Initialize Git repository** (if not already done):
   ```powershell
   git init
   git add .
   git commit -m "Initial commit - ready for macOS build"
   ```

### Step 2: Push to GitHub

1. **Create a GitHub account** (if you don't have one): https://github.com

2. **Create a new repository** on GitHub:
   - Go to https://github.com/new
   - Name it: `psi-forecast-system`
   - Make it **Private** (or Public, your choice)
   - **Don't** initialize with README
   - Click "Create repository"

3. **Push your code to GitHub**:
   ```powershell
   git remote add origin https://github.com/YOUR_USERNAME/psi-forecast-system.git
   git branch -M main
   git push -u origin main
   ```
   (Replace `YOUR_USERNAME` with your GitHub username)

### Step 3: Create Release Tag

1. **Create a release tag**:
   ```powershell
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Wait for GitHub Actions to build**:
   - Go to your GitHub repository
   - Click the **"Actions"** tab
   - You'll see "Build macOS Application" workflow running
   - Wait 5-10 minutes for it to complete

### Step 4: Download DMG

1. **Go to Releases**:
   - In your GitHub repo, click **"Releases"** (on the right side)
   - Or go to: `https://github.com/YOUR_USERNAME/psi-forecast-system/releases`

2. **Download the DMG**:
   - Click on the release (v1.0.0)
   - Download `PSI Forecast System-1.0.0.dmg`

3. **Done!** 🎉
   - Transfer the DMG to a Mac
   - Mount it and install the app

---

## Option 2: Manual Build Script (For Mac User)

If you'll have someone with a Mac build it, prepare these files:

### Step 1: Ensure All Files Are Ready

Check that these files exist:
- ✅ `backend/packaging/pyinstaller.spec`
- ✅ `backend/packaging/build_backend_macos.sh`
- ✅ `frontend/packaging/electron-app/package.json`
- ✅ `build-standalone.sh` (root directory)

### Step 2: Create Instructions for Mac User

Create a file `INSTRUCTIONS_FOR_MAC_USER.txt` with:

```
STEPS TO BUILD ON MAC:

1. Open Terminal
2. Navigate to project folder:
   cd /path/to/psi-app

3. Make build script executable:
   chmod +x build-standalone.sh

4. Run build script:
   ./build-standalone.sh

5. Wait for build to complete (10-15 minutes)

6. Find DMG at:
   frontend/packaging/electron-app/dist/PSI Forecast System-1.0.0.dmg

7. Send DMG back to Windows user
```

### Step 3: Transfer Files to Mac

- Use USB drive, cloud storage (Google Drive, Dropbox), or Git
- Ensure all files are transferred

---

## Option 3: WSL (Windows Subsystem for Linux) - Advanced

If you have WSL installed, you can prepare the build but still need macOS to actually build.

### Step 1: Install WSL (if not installed)

1. Open PowerShell as Administrator:
   ```powershell
   wsl --install
   ```

2. Restart your computer

3. Open Ubuntu (or your Linux distribution)

### Step 2: Prepare in WSL

```bash
# Navigate to your project (mount Windows drive)
cd /mnt/c/Users/Lenovo/Desktop/Forecasting\ Project/psi-app

# Make scripts executable
chmod +x build-standalone.sh
chmod +x backend/packaging/build_backend_macos.sh
```

**Note**: You still can't build macOS apps in WSL. This just prepares the scripts.

---

## Option 4: Use a Mac VM (Complex)

If you have a Mac license, you can:
1. Install macOS in VMware/VirtualBox
2. Follow the Mac build instructions
3. This is complex and requires macOS license

---

## Recommended: GitHub Actions Workflow

Here's what happens automatically when you push to GitHub:

### Automatic Build Process:

1. **GitHub Actions detects** your push/tag
2. **Starts macOS runner** (virtual Mac in the cloud)
3. **Builds Python backend**:
   - Installs Python dependencies
   - Creates executable with PyInstaller
4. **Builds React frontend**:
   - Installs Node.js dependencies
   - Builds production bundle
5. **Packages Electron app**:
   - Bundles frontend + backend
   - Creates DMG file
6. **Uploads DMG** to Releases

### What You Need to Do:

1. ✅ Push code to GitHub
2. ✅ Create release tag
3. ✅ Wait for build
4. ✅ Download DMG

That's it! No Mac needed on your end.

---

## Troubleshooting

### Git Not Found
- Download: https://git-scm.com/download/win
- Install with default options
- Restart PowerShell

### GitHub Push Fails
- Check your internet connection
- Verify GitHub credentials
- Use Personal Access Token if 2FA is enabled

### GitHub Actions Not Running
- Check `.github/workflows/build-macos.yml` exists
- Verify you pushed the file
- Check Actions tab for errors

### Build Fails in GitHub Actions
- Check the Actions log for errors
- Common issues:
  - Missing dependencies in `requirements.txt`
  - Syntax errors in Python/JavaScript
  - Missing files

---

## Quick Start (GitHub Actions)

**Fastest way from Windows:**

```powershell
# 1. Navigate to project
cd "C:\Users\Lenovo\Desktop\Forecasting Project\psi-app"

# 2. Initialize Git (if needed)
git init
git add .
git commit -m "Ready for macOS build"

# 3. Add GitHub remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/psi-forecast-system.git
git branch -M main
git push -u origin main

# 4. Create release tag
git tag v1.0.0
git push origin v1.0.0

# 5. Wait 10 minutes, then download DMG from GitHub Releases
```

---

## File Checklist

Before building, ensure these files exist:

### Backend:
- ✅ `backend/packaging/pyinstaller.spec`
- ✅ `backend/packaging/build_backend_macos.sh`
- ✅ `backend/requirements.txt`
- ✅ `backend/main.py` (updated with CORS)
- ✅ `backend/database.py` (updated for app data)

### Frontend:
- ✅ `frontend/packaging/electron-app/package.json`
- ✅ `frontend/packaging/electron-app/main.js` (updated for backend)
- ✅ `frontend/packaging/electron-app/preload.js`
- ✅ `frontend/package.json`

### Build:
- ✅ `build-standalone.sh`
- ✅ `.github/workflows/build-macos.yml`

---

## Next Steps

1. **Choose your method** (GitHub Actions recommended)
2. **Follow the steps** above
3. **Wait for build** to complete
4. **Download and test** the DMG on a Mac

---

## Summary

**Best Option for Windows Users:**
1. Push code to GitHub
2. Create release tag
3. GitHub Actions builds automatically
4. Download DMG from Releases

**No Mac needed!** 🎉

