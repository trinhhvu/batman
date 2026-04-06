"""
engine.py — Download Engine with cancellation support
=======================================================
Wraps yt-dlp for video analysis and downloading.
Supports cancel_download() which:
  1. Sets a flag to interrupt the progress hook (raises DownloadCancelled)
  2. Cleans up ALL partial files left by yt-dlp in the download folder
     (.part, .ytdl, frag_* temp files from concurrent fragment downloads)

Dependencies: yt-dlp, utils.py
"""

import yt_dlp
import os
import re
import glob
import threading
from utils import get_ffmpeg_path


# ──────────────────────────────────────────────────────────────
# Custom exception used to abort an in-progress download cleanly
# ──────────────────────────────────────────────────────────────
class DownloadCancelled(Exception):
    """Raised inside the yt-dlp progress hook to abort downloading."""
    pass


class DownloadEngine:
    """
    yt-dlp wrapper with cancellation and temp-file cleanup.
    Thread-safe: cancel_download() can be called from any thread.
    """

    def __init__(self, download_path: str):
        self.download_path = download_path
        self._cancel_event = threading.Event()   # set → cancel is requested
        self._current_outtmpl: str | None = None  # track the current output template

    # ──────────────────────────────────────────────────────────
    # Public control API
    # ──────────────────────────────────────────────────────────

    def cancel_download(self):
        """
        Signal the running download to stop and delete all partial files.
        Safe to call from the UI thread.
        """
        self._cancel_event.set()

    def reset_cancel(self):
        """Clear the cancel flag before starting a new download."""
        self._cancel_event.clear()

    def is_cancelled(self) -> bool:
        return self._cancel_event.is_set()

    # ──────────────────────────────────────────────────────────
    # Temp-file cleanup
    # ──────────────────────────────────────────────────────────

    def cleanup_partial_files(self):
        """
        Delete all yt-dlp temporary / partial files in download_path.
        Covers:
          - *.part              (incomplete download)
          - *.ytdl              (yt-dlp metadata)
          - *.part-Frag*        (fragment files from concurrent download)
          - Frag*               (bare fragment files)
          - *.f*.mp4, *.f*.webm (video/audio streams before merge)
        """
        patterns = [
            "*.part",
            "*.ytdl",
            "*.part-Frag*",
            "Frag*",
            "*.f[0-9]*.mp4",
            "*.f[0-9]*.webm",
            "*.f[0-9]*.m4a",
        ]
        deleted = 0
        for pattern in patterns:
            for path in glob.glob(os.path.join(self.download_path, pattern)):
                try:
                    os.remove(path)
                    deleted += 1
                except Exception:
                    pass
        return deleted

    # ──────────────────────────────────────────────────────────
    # Core methods
    # ──────────────────────────────────────────────────────────

    def analyze_video(self, url: str) -> dict:
        """Extracts video information using yt-dlp (no download)."""
        ydl_opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    def get_ydl_opts(self, quality: str, progress_hook) -> dict:
        """Configures yt-dlp options based on selected quality and hook."""
        q_map = {
            "Best Available": "bestvideo+bestaudio/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
            "720p":  "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
            "480p":  "bestvideo[height<=480]+bestaudio/best[height<=480]/best",
        }
        fmt = q_map.get(quality, "best")

        return {
            'format': fmt,
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'ffmpeg_location': get_ffmpeg_path(),
            'concurrent_fragment_downloads': 16,
            'retries': 20,
            'fragment_retries': 20,
            'quiet': True,
            'no_warnings': True,
        }

    def start_download(self, url: str, quality: str, progress_hook):
        """
        Download a video. Raises DownloadCancelled if cancel_download() is called.
        Automatically cleans up partial files on cancellation.
        """
        if not url:
            raise ValueError("URL is empty or None")

        self.reset_cancel()

        # Wrap the caller's hook to inject the cancel check
        def cancellable_hook(d):
            if self._cancel_event.is_set():
                raise DownloadCancelled("Download cancelled by user")
            progress_hook(d)

        ydl_opts = self.get_ydl_opts(quality, cancellable_hook)
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except DownloadCancelled:
            self.cleanup_partial_files()
            raise
        except Exception:
            # On any error also clean up partials
            self.cleanup_partial_files()
            raise


def parse_progress(d: dict):
    """Parses percent and speed from yt-dlp progress dictionary."""
    if not d or 'status' not in d:
        return None
    if d['status'] == 'downloading':
        p_str = d.get('_percent_str', '0%')
        p_str = re.sub(r'\x1b\[[0-9;]*m', '', p_str).strip().replace('%', '')
        try:
            return float(p_str) / 100, p_str, d.get('_speed_str', 'N/A')
        except Exception:
            return 0.0, "0", "N/A"
    return None
