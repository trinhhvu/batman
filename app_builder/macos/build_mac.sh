#!/bin/bash
ICON="../../assets/icon.png"
NAME="Batman v2"
MAIN="../../main.py"

# Tìm ffmpeg từ Homebrew hoặc system PATH
FFMPEG_PATH=$(which ffmpeg)
if [ -z "$FFMPEG_PATH" ]; then
    echo "[ERROR] ffmpeg not found! Please run: brew install ffmpeg"
    exit 1
fi
echo "[INFO] Found ffmpeg at: $FFMPEG_PATH"

# Xóa build cũ để tránh cache
echo "[CLEAN] Removing old build artifacts..."
rm -rf ../../dist ../../build ./*.spec

echo "[BUILDING BATMAN V2 FOR MACOS]"
python3 -m PyInstaller --noconfirm --onefile --windowed \
    --icon "$ICON" \
    --name "$NAME" \
    --add-data "../../assets:assets" \
    --add-binary "$FFMPEG_PATH:." \
    --collect-all PyQt5 \
    --collect-all yt_dlp \
    "$MAIN"

echo "[BUILD COMPLETE] → dist/Batman v2.app"
