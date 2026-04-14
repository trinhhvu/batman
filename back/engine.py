"""
back/engine.py — Download Engine with cancellation support
============================================================
Wraps yt-dlp for video analysis and downloading.
"""

import yt_dlp
import os
import re
import glob
import threading

from back.utils import get_ffmpeg_path


class DownloadCancelled(Exception):
    """Raised inside the yt-dlp progress hook to abort downloading."""
    pass


class DownloadEngine:
    """yt-dlp wrapper with cancellation and temp-file cleanup."""

    def __init__(self, download_path: str):
        self.download_path = download_path
        self._cancel_event = threading.Event()

    def cancel_download(self):
        self._cancel_event.set()

    def reset_cancel(self):
        self._cancel_event.clear()

    def is_cancelled(self) -> bool:
        return self._cancel_event.is_set()

    def cleanup_partial_files(self):
        patterns = [
            "*.part", "*.ytdl", "*.part-Frag*", "Frag*",
            "*.f[0-9]*.mp4", "*.f[0-9]*.webm", "*.f[0-9]*.m4a",
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

    def analyze_video(self, url: str) -> dict:
        """Extracts video information using yt-dlp (no download)."""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'legacyserverconnect': True,
            'force_ipv4': True,
            'referer': 'https://www.dailymotion.com/',
            'socket_timeout': 30,
            'retries': 10
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    def get_ydl_opts(self, quality: str, progress_hook) -> dict:
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
            'nocheckcertificate': True,
            'legacyserverconnect': True,
            'force_ipv4': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.dailymotion.com/',
            'socket_timeout': 30
        }

    def start_download(self, url: str, quality: str, progress_hook):
        if not url:
            raise ValueError("URL is empty or None")
        self.reset_cancel()

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
            self.cleanup_partial_files()
            raise


def parse_progress(d: dict):
    """Parses percent and speed from yt-dlp progress dictionary."""
    if not d or 'status' not in d:
        return None
    if d['status'] == 'downloading':
        def clean_ansi(s):
            return re.sub(r'\x1b\[[0-9;]*m', '', str(s)).strip()

        p_str = clean_ansi(d.get('_percent_str', '0%')).replace('%', '')
        s_str = clean_ansi(d.get('_speed_str', 'N/A'))

        try:
            return float(p_str) / 100, p_str, s_str
        except Exception:
            return 0.0, "0", "N/A"
    return None
