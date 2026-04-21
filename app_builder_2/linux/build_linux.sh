#!/bin/bash
# ── TRACK — Linux Quick Build Script (app_builder_2) ──
# Tạo binary chạy thẳng trên Linux, không tạo package installer.
# Chạy từ thư mục: app_builder_2/linux/
# Yêu cầu: sudo apt install ffmpeg python3-pip python3-venv libxcb-xinerama0

set -e

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
NAME="BATMAN V3"
MAIN="$ROOT/main.py"
DIST="$ROOT/dist"

# Kiểm tra ffmpeg
FFMPEG_PATH=$(which ffmpeg || true)
if [ -z "$FFMPEG_PATH" ]; then
    echo "[ERROR] ffmpeg not found! Please run: sudo apt install ffmpeg"
    exit 1
fi
echo "[INFO] Found ffmpeg at: $FFMPEG_PATH"

# Clean cũ
echo "[INFO] Cleaning old build artifacts..."
rm -rf "$ROOT/build" "$DIST"

echo "[BUILDING TRACK FOR LINUX — Direct Run Binary]"
python3 -m PyInstaller \
    --noconfirm \
    --onefile \
    --windowed \
    --name "$NAME" \
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

BINARY_PATH="$DIST/$NAME"
if [ -f "$BINARY_PATH" ]; then
    # Cấp quyền execute
    chmod +x "$BINARY_PATH"
    echo ""
    echo "[SUCCESS] Build complete!"
    echo "[OUTPUT]  $BINARY_PATH"
    echo "[TIP]     Chạy luôn bằng lệnh: \"$BINARY_PATH\""
else
    echo "[ERROR] Build failed — binary not found."
    exit 1
fi
