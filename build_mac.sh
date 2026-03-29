#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Xóa venv cũ để xây lại sạch sẽ
rm -rf venv
python3 -m venv venv
source venv/bin/activate

echo "[INFO] Đang cài đặt bộ chuyển đổi hình ảnh (Pillow)..."
pip install --upgrade pip
pip install Pillow requests pandas beautifulsoup4 PyQt5 openpyxl pyinstaller

rm -rf build dist
pyinstaller --noconfirm --onedir --windowed \
  --name "batman v1" \
  --icon "icon.png" \
  --add-data "icon.png:." \
  main.py

echo "Build complete. Check dist/ folder."
