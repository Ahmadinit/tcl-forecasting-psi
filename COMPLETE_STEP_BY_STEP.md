# Complete Step-by-Step Guide: Building Standalone macOS App from Windows

## ✅ Step 1: Verify Prerequisites (COMPLETED)

- [x] Git installed (version 2.51.1)
- [x] Git repository initialized
- [x] All files committed
- [x] Required files verified:
  - [x] `.github/workflows/build-macos.yml` exists
  - [x] `backend/packaging/pyinstaller.spec` exists
  - [x] `frontend/packaging/electron-app/package.json` exists

## 📋 Step 2: Create GitHub Repository

**Action Required:** You need to do this manually in your browser.

1. Go to: **https://github.com/new**
2. Repository name: `psi-forecast-system` (or any name you prefer)
3. Choose **Private** (or Public - your choice)
4. **DO NOT** check "Initialize with README"
5. Click **"Create repository"**

**After creating, note your GitHub username - you'll need it in the next step.**

## 📋 Step 3: Connect Local Repository to GitHub

**Replace `YOUR_USERNAME` with your actual GitHub username:**

```powershell
git remote add origin https://github.com/YOUR_USERNAME/psi-forecast-system.git
git branch -M main
git push -u origin main
```

**If asked for credentials:**
- **Username:** Your GitHub username
- **Password:** Use a **Personal Access Token** (NOT your password)
  - Create token: https://github.com/settings/tokens
  - Click "Generate new token (classic)"
  - Name: "PSI Build"
  - Select scope: ✅ **repo** (check the box)
  - Click "Generate token"
  - **Copy the token** (you won't see it again!)
  - Paste it as the password when pushing

## 📋 Step 4: Create Release Tag

This triggers the GitHub Actions build:

```powershell
git tag v1.0.0
git push origin v1.0.0
```

## 📋 Step 5: Monitor Build Progress

1. Go to: `https://github.com/YOUR_USERNAME/psi-forecast-system`
2. Click the **"Actions"** tab (top menu)
3. You'll see "Build macOS Application" workflow running
4. Click on it to see detailed progress
5. Wait **5-10 minutes** for build to complete

**What happens automatically:**
- ✅ GitHub starts a virtual macOS machine
- ✅ Installs Python 3.11
- ✅ Installs Node.js 18
- ✅ Builds Python backend → Creates `psi-backend-macos` executable
- ✅ Builds React frontend → Creates production bundle
- ✅ Packages Electron app → Creates DMG file
- ✅ Uploads DMG to Releases

## 📋 Step 6: Download DMG File

1. In your GitHub repo, click **"Releases"** (right sidebar)
   - Or go to: `https://github.com/YOUR_USERNAME/psi-forecast-system/releases`
2. Click on **"v1.0.0"** release
3. Scroll down to "Assets"
4. Download **"PSI Forecast System-1.0.0.dmg"** (about 100-150 MB)

## 📋 Step 7: Install and Test on macOS

1. **Transfer DMG to Mac** (email, cloud storage, USB, etc.)
2. **Mount DMG:** Double-click the DMG file
3. **Install:** Drag "PSI Forecast System" app to Applications folder
4. **Run:** Launch from Applications
5. **Verify:**
   - App window opens
   - Backend starts automatically (check Console.app for logs)
   - Database created automatically in: `~/Library/Application Support/PSI Forecast System/data/psi.db`
   - All features work

## 🎯 Summary of All Steps

```
1. ✅ Git initialized
2. ✅ Files committed
3. ⏭️  Create GitHub repo (manual)
4. ⏭️  Connect to GitHub (git remote add + push)
5. ⏭️  Create tag (git tag + push)
6. ⏭️  Wait for build (5-10 min)
7. ⏭️  Download DMG
8. ⏭️  Install on Mac
```

## 📝 Next Commands to Run

Run these commands in order (replace `YOUR_USERNAME`):

```powershell
# Step 3: Connect to GitHub
git remote add origin https://github.com/YOUR_USERNAME/psi-forecast-system.git
git branch -M main
git push -u origin main

# Step 4: Create release tag
git tag v1.0.0
git push origin v1.0.0
```

## ⚠️ Important Notes

1. **You cannot build macOS apps on Windows** - GitHub Actions does it for you
2. **Personal Access Token** is required if you have 2FA enabled
3. **Build takes 5-10 minutes** - be patient
4. **DMG is ~100-150 MB** - includes everything (frontend + backend)
5. **Backend runs automatically** when app launches
6. **Database is persistent** - stored in user's app data directory

## 🔍 Troubleshooting

### "Repository not found"
- Check you created the repository on GitHub first
- Verify the repository name matches
- Check your username is correct

### "Permission denied" when pushing
- Use Personal Access Token instead of password
- Create token: https://github.com/settings/tokens
- Select scope: `repo`

### Build fails in GitHub Actions
- Click on failed workflow
- Read error messages
- Common issues:
  - Missing dependencies → Add to `requirements.txt`
  - Syntax errors → Fix in code
  - Missing files → Ensure all files committed

### Backend not starting in app
- Check Console.app for error messages
- Verify executable exists in app bundle
- Check permissions

## ✅ What's Included in the Standalone App

- ✅ **Frontend:** React app (built with Vite)
- ✅ **Backend:** Python executable (bundled with PyInstaller)
- ✅ **Database:** SQLite (auto-created on first run)
- ✅ **All Dependencies:** Everything bundled, no installation needed

## 📚 Additional Documentation

- `START_HERE_WINDOWS.md` - Quick start guide
- `BUILD_FROM_WINDOWS.md` - Detailed options
- `STANDALONE_BUILD_SUMMARY.md` - Technical overview
- `frontend/packaging/BUILD_STANDALONE.md` - Build details

---

**Current Status:** ✅ Ready to push to GitHub and build!

