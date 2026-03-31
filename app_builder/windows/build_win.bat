@echo off
set ICON=..\..\assets\icon.png
set NAME="Batman v2"
set MAIN=..\..\main.py

echo [BUILDING BATMAN V2 FOR WINDOWS]
pyinstaller --noconfirm --onefile --windowed ^
    --icon "%ICON%" ^
    --name %NAME% ^
    --add-data "../../assets;assets" ^
    --add-data "../../ffmpeg.exe;." ^
    --collect-all PyQt5 ^
    --collect-all yt_dlp ^
    %MAIN%

echo [BUILD COMPLETE]
pause
