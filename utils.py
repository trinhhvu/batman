"""
utils.py — Cross-platform FFmpeg Utility
=========================================
Returns correct ffmpeg path for both Windows (.exe) and macOS/Linux (binary).
Works in both development mode and PyInstaller frozen bundles.

Dependencies: None (stdlib only)
Used by: engine.py, download_page.py
"""

import os
import sys
import platform
import shutil


def get_ffmpeg_path():
    """Returns the absolute path to ffmpeg, cross-platform."""
    if getattr(sys, 'frozen', False):
        # PyInstaller --onefile extracts bundled files to sys._MEIPASS (temp dir)
        # sys.executable points to the actual binary, NOT where bundled files live
        bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        # Running as normal Python script
        bundle_dir = os.path.dirname(os.path.abspath(__file__))

    # Platform-specific binary name
    ffmpeg_name = "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg"
    local_path = os.path.join(bundle_dir, ffmpeg_name)

    # Check local bundled ffmpeg first
    if os.path.exists(local_path):
        return local_path

    # Fallback: check system PATH (works on macOS with brew install ffmpeg)
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg

    # Return local path anyway (will trigger warning in UI)
    return local_path


def check_ffmpeg_exists():
    """Checks if ffmpeg is present at the expected location."""
    path = get_ffmpeg_path()
    return os.path.exists(path), path
