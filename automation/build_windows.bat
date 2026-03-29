@echo off
title batman v1 - Windows Super Build Fix
cd /d "%~dp0\.."

echo [1/5] Xoa sach build cu...
rmdir /s /q venv build dist 2>nul

echo [2/5] Tao moi truong sach se...
python -m venv venv
call venv\Scripts\activate

echo [3/5] Cai dat bo doi ngu...
python -m pip install --upgrade pip
pip install PyQt5 requests pandas beautifulsoup4 openpyxl pyinstaller pywin32 Pillow

echo [4/5] Bat dau dong goi...
pyinstaller --noconfirm --onefile --windowed --name "batman v1" --icon "assets/icon.png" --add-data "assets/icon.png;assets" main.py

echo [5/5] Build hoan tat!
pause
