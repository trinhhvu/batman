#!/bin/bash
# ── TRACK — macOS Quick Build Script (app_builder_2) ──
# Tạo file .app chạy thẳng trên macOS, không tạo DMG installer.
# Chạy từ thư mục: app_builder_2/macos/
# Yêu cầu: brew install ffmpeg

set -e

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
NAME="BATMAN V3"
ICON="$ROOT/assets/icon.png"
MAIN="$ROOT/main.py"
DIST="$ROOT/dist"

# Kiểm tra ffmpeg
FFMPEG_PATH=$(which ffmpeg || true)
if [ -z "$FFMPEG_PATH" ]; then
    echo "[ERROR] ffmpeg not found! Please run: brew install ffmpeg"
    exit 1
fi
echo "[INFO] Found ffmpeg at: $FFMPEG_PATH"

# Clean cũ
echo "[INFO] Cleaning old build artifacts..."
rm -rf "$ROOT/build" "$DIST"

echo "[BUILDING TRACK FOR MACOS — Direct Run .app]"
python3 -m PyInstaller \
    --noconfirm \
    --onefile \
    --windowed \
    --name "$NAME" \
    --icon "$ICON" \
    --distpath "$DIST" \
    --add-data "$ROOT/assets:assets" \
    --add-data "$ROOT/config.json:." \
    --add-data "$ROOT/front:front" \
    --add-data "$ROOT/back:back" \
    --add-binary "$FFMPEG_PATH:." \
    --collect-all PyQt5 \
    --collect-all yt_dlp \
    --hidden-import front.gui \
    --hidden-import front.design \
    --hidden-import front.pages.analyze_page \
    --hidden-import front.pages.download_page \
    --hidden-import front.pages.scanner_page \
    --hidden-import front.pages.research_page \
    --hidden-import front.widgets.sidebar \
    --hidden-import back.api_client \
    --hidden-import back.config \
    --hidden-import back.engine \
    --hidden-import back.tracker \
    --hidden-import back.utils \
    --hidden-import back.workers \
    "$MAIN"

APP_PATH="$DIST/$NAME.app"
if [ -e "$APP_PATH" ]; then
    echo ""
    echo "[SUCCESS] Build complete!"
    echo "[OUTPUT]  $APP_PATH"
    echo "[TIP]     Kéo '$NAME.app' vào Applications hoặc chạy thẳng."
    open "$DIST"
else
    echo "[ERROR] Build failed — .app not found."
    exit 1
fi
