"""
back/utils.py — Cross-platform FFmpeg Utility
==============================================
Returns correct ffmpeg path for both Windows (.exe) and macOS/Linux (binary).
"""

import os
import sys
import platform
import shutil

from back import TRACK_ROOT


def get_ffmpeg_path():
    """Returns the absolute path to ffmpeg, cross-platform."""
    if getattr(sys, 'frozen', False):
        bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        bundle_dir = TRACK_ROOT

    ffmpeg_name = "ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg"
    local_path = os.path.join(bundle_dir, ffmpeg_name)

    if os.path.exists(local_path):
        return local_path

    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg

    return local_path


def check_ffmpeg_exists():
    """Checks if ffmpeg is present at the expected location."""
    path = get_ffmpeg_path()
    return os.path.exists(path), path
