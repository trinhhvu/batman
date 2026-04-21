@echo off
setlocal
REM ── TRACK — Windows Quick Build Script (app_builder_2) ──
REM Tạo file .exe chạy thẳng, không tạo installer.
REM Chạy từ thư mục: app_builder_2\windows\

set ROOT=..\..
set ICON=%ROOT%\assets\icon.png
set NAME=BATMAN V3
set MAIN=%ROOT%\main.py
set DIST=%ROOT%\dist

echo [INFO] Cleaning old build artifacts...
if exist "%ROOT%\build" rmdir /s /q "%ROOT%\build"
if exist "%DIST%"        rmdir /s /q "%DIST%"

echo [BUILDING TRACK FOR WINDOWS — Direct Run EXE]
python -m PyInstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name "%NAME%" ^
    --icon "%ICON%" ^
    --distpath "%DIST%" ^
    --add-data "%ROOT%\assets;assets" ^
    --add-data "%ROOT%\ffmpeg.exe;." ^
    --add-data "%ROOT%\config.json;." ^
    --add-data "%ROOT%\front;front" ^
    --add-data "%ROOT%\back;back" ^
    --collect-all PyQt5 ^
    --collect-all yt_dlp ^
    --hidden-import front.gui ^
    --hidden-import front.design ^
    --hidden-import front.pages.analyze_page ^
    --hidden-import front.pages.download_page ^
    --hidden-import front.pages.scanner_page ^
    --hidden-import front.pages.research_page ^
    --hidden-import front.widgets.sidebar ^
    --hidden-import back.api_client ^
    --hidden-import back.config ^
    --hidden-import back.engine ^
    --hidden-import back.tracker ^
    --hidden-import back.utils ^
    --hidden-import back.workers ^
    "%MAIN%"

echo.
if exist "%DIST%\%NAME%.exe" (
    echo [SUCCESS] Build complete!
    echo [OUTPUT]  %DIST%\%NAME%.exe
) else (
    echo [ERROR] Build failed — executable not found.
    exit /b 1
)
pause
endlocal
