# Windows Setup Checklist - Before Building

Use this checklist to ensure everything is ready before building the macOS app.

## ✅ Pre-Build Checklist

### 1. Git Installation
- [ ] Git installed: https://git-scm.com/download/win
- [ ] Git version checked: `git --version` in PowerShell
- [ ] Git configured: `git config --global user.name "Your Name"`
- [ ] Git configured: `git config --global user.email "your.email@example.com"`

### 2. GitHub Account
- [ ] GitHub account created: https://github.com
- [ ] Personal Access Token created (if using 2FA): https://github.com/settings/tokens
  - Token scope: `repo` (full control)
  - Token saved securely (you'll need it)

### 3. Project Files Check
Verify these files exist in your project:

#### Backend Files:
- [ ] `backend/packaging/pyinstaller.spec` exists
- [ ] `backend/packaging/build_backend_macos.sh` exists
- [ ] `backend/requirements.txt` exists
- [ ] `backend/main.py` exists (with CORS updates)
- [ ] `backend/database.py` exists (with app data directory)

#### Frontend Files:
- [ ] `frontend/packaging/electron-app/package.json` exists
- [ ] `frontend/packaging/electron-app/main.js` exists (with backend auto-start)
- [ ] `frontend/packaging/electron-app/preload.js` exists
- [ ] `frontend/package.json` exists

#### Build Files:
- [ ] `build-standalone.sh` exists (root directory)
- [ ] `.github/workflows/build-macos.yml` exists

### 4. Code Quality Check
- [ ] No syntax errors in Python files
- [ ] No syntax errors in JavaScript files
- [ ] All imports are correct
- [ ] All dependencies listed in `requirements.txt`

### 5. Git Repository
- [ ] Project folder is a Git repository: `git status` works
- [ ] All files are committed: `git status` shows "nothing to commit"
- [ ] Or ready to commit: `git add .` and `git commit -m "Ready for build"`

---

## 🚀 Build Process Checklist

### Step 1: Prepare Repository
- [ ] Navigate to project: `cd "C:\Users\Lenovo\Desktop\Forecasting Project\psi-app"`
- [ ] Check Git status: `git status`
- [ ] Add all files: `git add .`
- [ ] Commit: `git commit -m "Ready for macOS build"`

### Step 2: Connect to GitHub
- [ ] GitHub repository created
- [ ] Remote added: `git remote add origin https://github.com/YOUR_USERNAME/psi-forecast-system.git`
- [ ] Branch renamed: `git branch -M main`
- [ ] Code pushed: `git push -u origin main`

### Step 3: Create Release
- [ ] Tag created: `git tag v1.0.0`
- [ ] Tag pushed: `git push origin v1.0.0`

### Step 4: Monitor Build
- [ ] GitHub repository opened
- [ ] Actions tab checked
- [ ] Build workflow running
- [ ] Waiting for completion (5-10 minutes)

### Step 5: Download Result
- [ ] Releases page opened
- [ ] v1.0.0 release found
- [ ] DMG file downloaded
- [ ] DMG file size checked (should be ~100-150 MB)

---

## 🔍 Verification Commands

Run these in PowerShell to verify setup:

```powershell
# Check Git
git --version

# Check if in Git repo
git status

# Check if remote is set
git remote -v

# Check if workflow file exists
Test-Path .github\workflows\build-macos.yml

# Check if backend packaging exists
Test-Path backend\packaging\pyinstaller.spec

# Check if frontend packaging exists
Test-Path frontend\packaging\electron-app\package.json
```

All should return `True` or show valid output.

---

## ❌ Common Issues & Fixes

### Issue: "git: command not found"
**Fix:** Install Git from https://git-scm.com/download/win

### Issue: "Permission denied" when pushing
**Fix:** Use Personal Access Token instead of password

### Issue: "Repository not found"
**Fix:** Check repository name and your GitHub username

### Issue: GitHub Actions not running
**Fix:** 
- Verify `.github/workflows/build-macos.yml` exists
- Check you pushed all files
- Verify workflow file syntax is correct

### Issue: Build fails in Actions
**Fix:**
- Click on failed workflow
- Read error messages
- Fix issues in code
- Push fixes and create new tag

---

## 📋 Quick Reference

### Essential Commands:
```powershell
# Navigate to project
cd "C:\Users\Lenovo\Desktop\Forecasting Project\psi-app"

# Check status
git status

# Add all files
git add .

# Commit
git commit -m "Your message"

# Push to GitHub
git push origin main

# Create and push tag
git tag v1.0.0
git push origin v1.0.0
```

### GitHub URLs:
- Create repo: https://github.com/new
- Create token: https://github.com/settings/tokens
- Your repos: https://github.com/YOUR_USERNAME?tab=repositories

---

## ✅ Ready to Build?

If all checkboxes are checked, you're ready! Follow:
- `QUICK_BUILD_WINDOWS.md` for fast steps
- `BUILD_FROM_WINDOWS.md` for detailed guide

Good luck! 🚀

