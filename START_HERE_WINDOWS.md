# 🚀 START HERE - Build macOS App from Windows

## Quick Start (Copy & Paste These Commands)

### Step 1: Open PowerShell

Press `Win + X` → Click "Windows PowerShell" or "Terminal"

### Step 2: Navigate to Your Project

```powershell
cd "C:\Users\Lenovo\Desktop\Forecasting Project\psi-app"
```

### Step 3: Check Git (Install if Needed)

```powershell
git --version
```

**If it says "command not found":**
- Download: https://git-scm.com/download/win
- Install with default options
- Close and reopen PowerShell
- Run `git --version` again

### Step 4: Initialize Git Repository

```powershell
git init
git add .
git commit -m "Ready for macOS build"
```

### Step 5: Create GitHub Repository

1. Go to: **https://github.com/new**
2. Repository name: `psi-forecast-system`
3. Choose **Private** (or Public)
4. **Don't** check "Initialize with README"
5. Click **"Create repository"**

### Step 6: Connect to GitHub

**Replace `YOUR_USERNAME` with your actual GitHub username:**

```powershell
git remote add origin https://github.com/YOUR_USERNAME/psi-forecast-system.git
git branch -M main
git push -u origin main
```

**When asked for credentials:**
- **Username:** Your GitHub username
- **Password:** Use a **Personal Access Token** (NOT your password)
  - Create token: https://github.com/settings/tokens
  - Click "Generate new token (classic)"
  - Name: "PSI Build"
  - Select scope: ✅ **repo** (check the box)
  - Click "Generate token"
  - **Copy the token** (you won't see it again!)
  - Paste it as the password

### Step 7: Create Release Tag

```powershell
git tag v1.0.0
git push origin v1.0.0
```

### Step 8: Wait for Build

1. Go to: **https://github.com/YOUR_USERNAME/psi-forecast-system**
2. Click the **"Actions"** tab (top menu)
3. You'll see "Build macOS Application" workflow
4. Click on it to see progress
5. Wait **5-10 minutes** (you'll see it building)

### Step 9: Download DMG

1. In your GitHub repo, click **"Releases"** (right sidebar, or go to: `https://github.com/YOUR_USERNAME/psi-forecast-system/releases`)
2. Click on **"v1.0.0"**
3. Scroll down to "Assets"
4. Download **"PSI Forecast System-1.0.0.dmg"** (about 100-150 MB)

### Step 10: Done! 🎉

Transfer the DMG file to a Mac:
- Email it
- Use cloud storage (Google Drive, Dropbox)
- Use USB drive
- Use AirDrop (if you have Mac nearby)

**On Mac:**
1. Double-click DMG to mount
2. Drag app to Applications folder
3. Run the app!

---

## 📋 Complete Command Sequence

Copy and paste this entire block (replace `YOUR_USERNAME`):

```powershell
# Navigate to project
cd "C:\Users\Lenovo\Desktop\Forecasting Project\psi-app"

# Initialize Git
git init
git add .
git commit -m "Ready for macOS build"

# Connect to GitHub (REPLACE YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/psi-forecast-system.git
git branch -M main
git push -u origin main

# Create release tag
git tag v1.0.0
git push origin v1.0.0

# Done! Now go to GitHub and wait for build
```

---

## ⚠️ Troubleshooting

### "git: command not found"
**Solution:** Install Git from https://git-scm.com/download/win

### "Permission denied" or "Authentication failed"
**Solution:** 
1. Create Personal Access Token: https://github.com/settings/tokens
2. Use token as password (not your GitHub password)

### "Repository not found"
**Solution:** 
- Check you created the repository on GitHub first
- Verify the repository name matches
- Check your username is correct

### "GitHub Actions not running"
**Solution:**
- Check `.github/workflows/build-macos.yml` file exists
- Verify you pushed all files: `git add . && git commit -m "Add workflow"`
- Push again: `git push origin main`

### Build fails in Actions
**Solution:**
1. Click on the failed workflow in GitHub
2. Read the error messages
3. Common issues:
   - Missing Python package → Add to `backend/requirements.txt`
   - Syntax error → Fix in your code
   - Missing file → Ensure all files are committed

---

## 📚 More Help

- **Quick Guide:** `QUICK_BUILD_WINDOWS.md`
- **Detailed Guide:** `BUILD_FROM_WINDOWS.md`
- **Checklist:** `WINDOWS_SETUP_CHECKLIST.md`
- **Technical Details:** `STANDALONE_BUILD_SUMMARY.md`

---

## ✅ What Happens Automatically

When you push the tag, GitHub Actions will:

1. ✅ Start a virtual Mac in the cloud
2. ✅ Install Python and Node.js
3. ✅ Build Python backend → Standalone executable
4. ✅ Build React frontend → Production bundle
5. ✅ Package Electron app → macOS DMG
6. ✅ Upload DMG to Releases

**You just wait and download!** No Mac needed on your end.

---

## 🎯 Summary

1. **Install Git** (if needed)
2. **Create GitHub repo**
3. **Push your code**
4. **Create tag** (`v1.0.0`)
5. **Wait 10 minutes**
6. **Download DMG** from Releases
7. **Transfer to Mac** and install

**That's it!** 🚀

