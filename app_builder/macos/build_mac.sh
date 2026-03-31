#!/bin/bash
ICON="../../assets/icon.png"
NAME="Batman v2"
MAIN="../../main.py"

echo "[BUILDING BATMAN V2 FOR MACOS]"
pyinstaller --noconfirm --onefile --windowed \
    --icon "$ICON" \
    --name "$NAME" \
    --add-data "../../assets:assets" \
    --collect-all PyQt5 \
    --collect-all yt_dlp \
    "$MAIN"

echo "[BUILD COMPLETE]"
chmod +x "dist/$NAME.app"
