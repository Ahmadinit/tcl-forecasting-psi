# Quick Build Guide - Windows to macOS

## 🚀 Fastest Method: GitHub Actions

### Prerequisites
- Git installed: https://git-scm.com/download/win
- GitHub account: https://github.com

---

## Step-by-Step (5 Minutes Setup)

### Step 1: Open PowerShell

Press `Win + X` → Select "Windows PowerShell" or "Terminal"

Navigate to your project:
```powershell
cd "C:\Users\Lenovo\Desktop\Forecasting Project\psi-app"
```

### Step 2: Initialize Git (If Not Done)

```powershell
git init
git add .
git commit -m "Ready for macOS build"
```

### Step 3: Create GitHub Repository

1. Go to: https://github.com/new
2. Repository name: `psi-forecast-system`
3. Choose **Private** or **Public**
4. **Don't** check "Initialize with README"
5. Click **"Create repository"**

### Step 4: Connect to GitHub

Replace `YOUR_USERNAME` with your GitHub username:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/psi-forecast-system.git
git branch -M main
git push -u origin main
```

**If asked for credentials:**
- Username: Your GitHub username
- Password: Use a **Personal Access Token** (not your password)
  - Create token: https://github.com/settings/tokens
  - Select scope: `repo`
  - Copy token and use as password

### Step 5: Create Release Tag

```powershell
git tag v1.0.0
git push origin v1.0.0
```

### Step 6: Wait for Build

1. Go to: `https://github.com/YOUR_USERNAME/psi-forecast-system`
2. Click **"Actions"** tab
3. You'll see "Build macOS Application" running
4. Wait **5-10 minutes**

### Step 7: Download DMG

1. Click **"Releases"** (right sidebar)
2. Click on **"v1.0.0"**
3. Download **"PSI Forecast System-1.0.0.dmg"**

### Step 8: Done! 🎉

Transfer the DMG to a Mac and install:
1. Double-click DMG to mount
2. Drag app to Applications
3. Run the app

---

## Troubleshooting

### "git: command not found"
- Install Git: https://git-scm.com/download/win
- Restart PowerShell after installation

### "Permission denied" when pushing
- Use Personal Access Token instead of password
- Create token: https://github.com/settings/tokens

### GitHub Actions not running
- Check `.github/workflows/build-macos.yml` exists
- Verify you pushed all files: `git add . && git commit -m "Add all files"`

### Build fails in Actions
- Click on the failed workflow
- Check the error log
- Common fixes:
  - Missing dependencies → Add to `requirements.txt`
  - Syntax errors → Fix in your code
  - Missing files → Ensure all files are committed

---

## Alternative: Manual Build (If You Have Mac Access)

If someone with a Mac will build it:

1. **Zip your project folder**
2. **Send to Mac user**
3. **Mac user runs**:
   ```bash
   cd /path/to/psi-app
   chmod +x build-standalone.sh
   ./build-standalone.sh
   ```
4. **Mac user sends DMG back**

---

## What Gets Built Automatically

✅ Python backend → Standalone executable  
✅ React frontend → Production bundle  
✅ Electron app → macOS DMG  
✅ All dependencies bundled  
✅ Database auto-created on first run  

**Total time: 10-15 minutes (mostly waiting)**

---

## Need Help?

Check these files:
- `BUILD_FROM_WINDOWS.md` - Detailed guide
- `STANDALONE_BUILD_SUMMARY.md` - Technical overview
- `frontend/packaging/BUILD_STANDALONE.md` - Build details

