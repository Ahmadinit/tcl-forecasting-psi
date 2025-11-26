#!/bin/bash

# Complete build script for standalone macOS application
# This builds both backend and frontend, then packages them together

set -e

echo "🚀 Building Standalone PSI Forecast System for macOS..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Build Backend
echo -e "${BLUE}📦 Step 1: Building Python Backend...${NC}"
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Build backend
echo "Building backend executable..."
mkdir -p packaging/dist
pyinstaller --clean packaging/pyinstaller.spec

# Copy to packaging directory
if [ -f "dist/psi-backend" ]; then
    cp dist/psi-backend packaging/dist/psi-backend-macos
    chmod +x packaging/dist/psi-backend-macos
    echo -e "${GREEN}✅ Backend built successfully${NC}"
    echo "   Location: backend/packaging/dist/psi-backend-macos"
    echo "   Size: $(du -h packaging/dist/psi-backend-macos | cut -f1)"
else
    echo -e "${YELLOW}❌ Backend build failed!${NC}"
    exit 1
fi

cd ..

# Step 2: Build Frontend
echo ""
echo -e "${BLUE}🎨 Step 2: Building React Frontend...${NC}"
cd frontend

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

# Build frontend
echo "Building frontend..."
npm run build

if [ -d "dist" ]; then
    echo -e "${GREEN}✅ Frontend built successfully${NC}"
    echo "   Location: frontend/dist/"
else
    echo -e "${YELLOW}❌ Frontend build failed!${NC}"
    exit 1
fi

cd ..

# Step 3: Build Electron App
echo ""
echo -e "${BLUE}⚡ Step 3: Building Electron App...${NC}"
cd frontend/packaging/electron-app

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Electron dependencies..."
    npm install
fi

# Build Electron app
echo "Building macOS DMG..."
npm run build:mac

if [ -f "dist/PSI Forecast System-1.0.0.dmg" ]; then
    echo ""
    echo -e "${GREEN}✅✅✅ Build Complete! ✅✅✅${NC}"
    echo ""
    echo "📦 DMG Location: frontend/packaging/electron-app/dist/PSI Forecast System-1.0.0.dmg"
    echo "📊 Size: $(du -h dist/PSI\ Forecast\ System-1.0.0.dmg | cut -f1)"
    echo ""
    echo "🎉 Your standalone macOS app is ready!"
    echo "   Mount the DMG and drag the app to Applications to install."
else
    echo -e "${YELLOW}❌ Electron build failed!${NC}"
    exit 1
fi

cd ../../..

