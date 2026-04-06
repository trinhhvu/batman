@echo off
set ICON=..\..\assets\icon.png
set NAME="BATMAN V3"
set MAIN=..\..\main.py

echo [BUILDING TRACK FOR WINDOWS]
python -m PyInstaller --noconfirm --onefile --windowed ^
    --icon "%ICON%" ^
    --name %NAME% ^
    --add-data "../../assets;assets" ^
    --add-data "../../ffmpeg.exe;." ^
    --add-data "../../pages;pages" ^
    --add-data "../../widgets;widgets" ^
    --add-data "../../config.json;." ^
    --collect-all PyQt5 ^
    --collect-all yt_dlp ^
    --hidden-import pages.analyze_page ^
    --hidden-import pages.download_page ^
    --hidden-import pages.scanner_page ^
    --hidden-import widgets.sidebar ^
    %MAIN%

echo [BUILD COMPLETE]
pause
