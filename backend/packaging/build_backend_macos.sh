#!/bin/bash

# Build script for macOS Python backend
# This creates a standalone executable using PyInstaller

set -e

echo "🔨 Building PSI Backend for macOS..."

# Get the backend directory
BACKEND_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BACKEND_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Create packaging directory
mkdir -p packaging/dist

# Build with PyInstaller
echo "🏗️  Building executable..."
pyinstaller --clean packaging/pyinstaller.spec

# Check if build was successful
if [ -f "dist/psi-backend" ]; then
    echo "✅ Build successful!"
    echo "📦 Executable: $BACKEND_DIR/dist/psi-backend"
    echo "📁 Size: $(du -h dist/psi-backend | cut -f1)"
else
    echo "❌ Build failed!"
    exit 1
fi

# Copy to packaging/dist for Electron
echo "📋 Copying to packaging directory..."
cp dist/psi-backend packaging/dist/psi-backend-macos
chmod +x packaging/dist/psi-backend-macos

echo "✅ Backend build complete!"
echo "📍 Location: $BACKEND_DIR/packaging/dist/psi-backend-macos"
