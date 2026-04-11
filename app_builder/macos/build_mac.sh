#!/bin/bash
# ── TRACK Professional — macOS Build Script ──
# This script bundles ffmpeg from Homebrew automatically.
# No manual ffmpeg install needed on the build machine beyond `brew install ffmpeg`.

ICON="../../assets/icon.png"
NAME="BATMAN V3"
MAIN="../../main.py"

# Locate ffmpeg from Homebrew or system PATH
FFMPEG_PATH=$(which ffmpeg)
if [ -z "$FFMPEG_PATH" ]; then
    echo "[ERROR] ffmpeg not found! Please run: brew install ffmpeg"
    exit 1
fi
echo "[INFO] Found ffmpeg at: $FFMPEG_PATH"

# Clean old build artifacts
echo "[CLEAN] Removing old build artifacts..."
rm -rf ../../dist ../../build ./*.spec

echo "[BUILDING TRACK FOR MACOS]"
python3 -m PyInstaller --noconfirm --onefile --windowed \
    --icon "$ICON" \
    --name "$NAME" \
    --add-data "../../assets:assets" \
    --add-data "../../pages:pages" \
    --add-data "../../widgets:widgets" \
    --add-data "../../config.json:." \
    --add-binary "$FFMPEG_PATH:." \
    --collect-all PyQt5 \
    --collect-all yt_dlp \
    --hidden-import pages.analyze_page \
    --hidden-import pages.download_page \
    --hidden-import pages.scanner_page \
    --hidden-import widgets.sidebar \
    "$MAIN"

echo "[BUILD COMPLETE] → dist/$NAME.app"

# ── Create DMG Installer (Requires: brew install create-dmg) ──
echo "[PACKAGING] Checking for DMG packager..."

if command -v create-dmg &> /dev/null; then
    echo "[PACKAGING] Creating DMG Installer..."
    # Ensure dist folder exists
    cd ../../dist
    
    # Remove existing DMG if it exists
    rm -f "Setup_BATMAN_v3.dmg"
    
    create-dmg \
      --volname "BATMAN V3 Installer" \
      --window-pos 200 120 \
      --window-size 600 400 \
      --icon-size 100 \
      --icon "$NAME.app" 150 190 \
      --hide-extension "$NAME.app" \
      --app-drop-link 450 190 \
      "Setup_BATMAN_v3.dmg" \
      "$NAME.app"
      
    echo "[SUCCESS] DMG Installer created at: dist/Setup_BATMAN_v3.dmg"
else
    echo "[WARNING] 'create-dmg' not found! Skipping DMG creation."
    echo "To automatically generate a DMG installer, install it via: brew install create-dmg"
    echo "Then re-run this script."
fi
