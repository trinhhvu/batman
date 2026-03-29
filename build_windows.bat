@echo off
title batman v1 - Windows Build (Final Icon Fix)
cd /d "%~dp0"

echo [1/5] Xoa sach build cu...
rmdir /s /q venv build dist 2>nul

echo [2/5] Tao moi truong sach se...
python -m venv venv
call venv\Scripts\activate

echo [3/5] Cai dat bo doi ngu (Co Pillow de ho tro Icon)...
python -m pip install --upgrade pip
pip install PyQt5 requests pandas beautifulsoup4 openpyxl pyinstaller pywin32 Pillow

echo [4/5] Bat dau dong goi VOI ICON BATMAN...
pyinstaller --noconfirm --onefile --windowed --name "batman v1" --icon "icon.png" --add-data "icon.png;." main.py

echo [5/5] Kiem tra ket qua...
if exist dist\"batman v1.exe" (
    echo.
    echo BUILD HOAN TAT 100%%! DA CO ICON BATMAN.
) else (
    echo.
    echo LOI: Khong tim thay file dist/batman v1.exe.
)

pause
