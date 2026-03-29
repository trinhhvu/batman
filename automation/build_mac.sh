#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR/.."

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q pyinstaller requests pandas beautifulsoup4 PyQt5 openpyxl Pillow

rm -rf build dist
pyinstaller --noconfirm --onedir --windowed \
  --name "batman v1" \
  --icon "assets/icon.png" \
  --add-data "assets/icon.png:assets" \
  main.py

echo "Build complete. Check dist/ folder in the project root."
