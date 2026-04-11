#!/bin/bash
# ── TRACK Professional — Ubuntu Linux Build Script ──
# This script configures the PyInstaller build for Ubuntu.
# Ensure ffmpeg is installed via: sudo apt install ffmpeg
# Ensure required build dependencies are installed:
# sudo apt install python3-pip python3-venv libxcb-xinerama0

ICON="../../assets/icon.png"
NAME="BATMAN V3"
MAIN="../../main.py"

# Locate ffmpeg from system PATH
FFMPEG_PATH=$(which ffmpeg)
if [ -z "$FFMPEG_PATH" ]; then
    echo "[ERROR] ffmpeg not found! Please run: sudo apt install ffmpeg"
    exit 1
fi
echo "[INFO] Found ffmpeg at: $FFMPEG_PATH"

# Clean old build artifacts
echo "[CLEAN] Removing old build artifacts..."
rm -rf ../../dist ../../build ./*.spec

echo "[BUILDING TRACK FOR UBUNTU LINUX]"
python3 -m PyInstaller --noconfirm --onefile --windowed \
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

echo "[BUILD COMPLETE] → dist/BATMAN V3"
