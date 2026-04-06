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

echo "[BUILD COMPLETE] → dist/TRACK Professional.app"
