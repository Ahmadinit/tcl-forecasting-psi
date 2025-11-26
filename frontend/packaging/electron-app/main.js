const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// Determine if we're in development or production
const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;

// Path to the built frontend
function getFrontendPath() {
  if (isDev) {
    // Development: load from frontend dist
    return path.join(__dirname, '../../../dist/index.html');
  } else {
    // Production: load from app resources
    // In Electron Builder, extraResources are in app.asar.unpacked or resources
    const resourcesPath = process.resourcesPath || app.getAppPath();
    const appPath = path.join(resourcesPath, 'app', 'index.html');
    
    // Fallback: try different paths
    if (!fs.existsSync(appPath)) {
      const altPath = path.join(__dirname, '../app/index.html');
      if (fs.existsSync(altPath)) {
        return altPath;
      }
    }
    
    return appPath;
  }
}

// Path to backend executable
function getBackendPath() {
  if (isDev) {
    // Development: use Python directly
    return path.join(__dirname, '../../../backend');
  } else {
    // Production: use bundled executable
    const resourcesPath = process.resourcesPath || app.getAppPath();
    // Backend executable is in resources
    if (process.platform === 'darwin') {
      // macOS: executable is in app.asar.unpacked or resources
      const backendPath = path.join(resourcesPath, 'backend', 'psi-backend');
      if (fs.existsSync(backendPath)) {
        return backendPath;
      }
      // Fallback: try alternative path
      const altPath = path.join(__dirname, '../backend/psi-backend');
      if (fs.existsSync(altPath)) {
        return altPath;
      }
    }
    return null;
  }
}

let mainWindow;
let backendProcess = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    show: false,  // Don't show until ready
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      webSecurity: true
    },
    icon: path.join(__dirname, 'icons.icns'),
    titleBarStyle: 'hiddenInset',
    backgroundColor: '#ffffff'
  });

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    mainWindow.focus();
    
    // Only open DevTools in development
    if (isDev) {
      mainWindow.webContents.openDevTools();
    }
  });

  // Load the frontend
  const frontendPath = getFrontendPath();
  
  if (fs.existsSync(frontendPath)) {
    mainWindow.loadFile(frontendPath).catch(err => {
      console.error('Failed to load file:', err);
      // Fallback to dev server
      mainWindow.loadURL('http://localhost:5173');
    });
  } else {
    // Fallback: try loading from URL (for development)
    console.log('Frontend file not found, loading from dev server');
    mainWindow.loadURL('http://localhost:5173');
  }

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Start backend server
function startBackend() {
  const backendPath = getBackendPath();
  
  if (!backendPath) {
    console.warn('Backend path not found, backend will not start');
    return;
  }
  
  if (isDev) {
    // Development: use Python uvicorn
    if (fs.existsSync(path.join(backendPath, 'main.py'))) {
      const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
      backendProcess = spawn(pythonCmd, ['-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8000'], {
        cwd: backendPath,
        shell: true,
        stdio: 'pipe'
      });
    } else {
      console.warn('Backend main.py not found');
      return;
    }
  } else {
    // Production: use bundled executable
    if (fs.existsSync(backendPath)) {
      backendProcess = spawn(backendPath, ['--host', '127.0.0.1', '--port', '8000'], {
        shell: false,
        stdio: 'pipe'
      });
    } else {
      console.error(`Backend executable not found at: ${backendPath}`);
      return;
    }
  }
  
  // Handle backend output
  if (backendProcess) {
    backendProcess.stdout.on('data', (data) => {
      const output = data.toString();
      console.log(`[Backend] ${output}`);
      // Check if backend is ready
      if (output.includes('Uvicorn running') || output.includes('Application startup complete')) {
        console.log('✅ Backend server started successfully');
      }
    });
    
    backendProcess.stderr.on('data', (data) => {
      const error = data.toString();
      console.error(`[Backend Error] ${error}`);
    });
    
    backendProcess.on('error', (error) => {
      console.error(`[Backend] Failed to start: ${error.message}`);
      // Show error to user
      if (mainWindow) {
        mainWindow.webContents.send('backend-error', error.message);
      }
    });
    
    backendProcess.on('exit', (code, signal) => {
      console.log(`[Backend] Process exited with code ${code}, signal ${signal}`);
      backendProcess = null;
    });
  }
}

// Stop backend server
function stopBackend() {
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
}

app.whenReady().then(() => {
  startBackend();
  createWindow();
});

app.on('window-all-closed', () => {
  stopBackend();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on('before-quit', () => {
  stopBackend();
});