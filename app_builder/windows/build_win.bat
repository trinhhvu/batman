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
    --add-data "../../front;front" ^
    --add-data "../../back;back" ^
    --add-data "../../config.json;." ^
    --collect-all PyQt5 ^
    --collect-all yt_dlp ^
    --hidden-import front.pages.analyze_page ^
    --hidden-import front.pages.download_page ^
    --hidden-import front.pages.scanner_page ^
    --hidden-import front.pages.research_page ^
    --hidden-import front.pages.upload_page ^
    --hidden-import front.pages.settings_page ^
    --hidden-import front.widgets.sidebar ^
    %MAIN%

echo [BUILD COMPLETE]
pause
