"""
engine.py — Download Engine with anti-bot bypass + cancellation support
=========================================================================
Wraps yt-dlp for video analysis and downloading.

Key features:
  1. Browser impersonation — giả lập Chrome để qua được Dailymotion 401
  2. Cookie extraction — dùng cookie của Chrome/Firefox nếu có
  3. Cancel support — raises DownloadCancelled + cleanup partial files
  4. Retry & fragment resilience — 20 retries, 16 concurrent fragments

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


# ──────────────────────────────────────────────────────────────
# Browser-like headers to trick Dailymotion into thinking
# we are a real Chrome browser (bypasses 401 Unauthorized)
# ──────────────────────────────────────────────────────────────
_BROWSER_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Referer': 'https://www.dailymotion.com/',
    'Origin': 'https://www.dailymotion.com',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Base yt-dlp options shared by analyze AND download
_BASE_YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'http_headers': _BROWSER_HEADERS,

    # Tell yt-dlp to pretend to be Chrome (uses yt-dlp's built-in impersonation)
    # This sets proper TLS fingerprint + QUIC headers
    'impersonate': 'chrome',

    # Add slight delay between requests to look more human
    'sleep_interval': 1,
    'max_sleep_interval': 3,

    # Retry aggressively
    'retries': 20,
    'fragment_retries': 20,
    'retry_sleep_functions': {'http': lambda n: min(4 * n, 30)},

    # Try to extract cookies from browser (helps with age-restricted or
    # geo-restricted content — comment out if not needed)
    # 'cookiesfrombrowser': ('chrome',),   # uncomment if still getting 401
}


def _get_base_opts() -> dict:
    """Return a fresh copy of base options."""
    return dict(_BASE_YDL_OPTS)


class DownloadEngine:
    """
    yt-dlp wrapper with browser impersonation, cancellation, and temp-file cleanup.
    Thread-safe: cancel_download() can be called from any thread.
    """

    def __init__(self, download_path: str):
        self.download_path = download_path
        self._cancel_event = threading.Event()
        self._current_outtmpl: str | None = None

    # ──────────────────────────────────────────────────────────
    # Public control API
    # ──────────────────────────────────────────────────────────

    def cancel_download(self):
        """Signal the running download to stop. Safe to call from UI thread."""
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
        Covers: *.part, *.ytdl, fragment files, unmuxed streams.
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
        """
        Extracts video metadata using yt-dlp.
        Uses browser headers + impersonation to bypass 401 errors.
        """
        opts = _get_base_opts()
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception as e:
            # If impersonate target fails, try without it
            if "Impersonate target" in str(e):
                opts.pop('impersonate', None)
                opts['quiet'] = False # for debugging if it still fails
                try:
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        return ydl.extract_info(url, download=False)
                except Exception:
                    pass
            
            # Final fallback: try with cookies from browser
            if '401' in str(e) or 'Unauthorized' in str(e):
                fallback_opts = _get_base_opts()
                fallback_opts.pop('impersonate', None)
                try:
                    fallback_opts['cookiesfrombrowser'] = ('chrome',)
                    with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                        return ydl.extract_info(url, download=False)
                except Exception:
                    pass
            raise

    def get_ydl_opts(self, quality: str, progress_hook) -> dict:
        """Configures yt-dlp download options with browser bypass."""
        q_map = {
            "Best Available": "bestvideo+bestaudio/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
            "720p":  "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
            "480p":  "bestvideo[height<=480]+bestaudio/best[height<=480]/best",
        }
        fmt = q_map.get(quality, "best")

        opts = _get_base_opts()
        opts.update({
            'format': fmt,
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'ffmpeg_location': get_ffmpeg_path(),
            'concurrent_fragment_downloads': 16,
            # Merge into mp4 always
            'merge_output_format': 'mp4',
            # Keep partial files visible so cleanup can grab them
            'keepvideo': False,
        })
        return opts

    def start_download(self, url: str, quality: str, progress_hook):
        """
        Download a video.
        Raises DownloadCancelled if cancel_download() is called mid-download.
        Automatically cleans up partial files on cancellation or error.
        """
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
        except Exception as e:
            # Fallback if impersonate target is missing during download too
            if "Impersonate target" in str(e):
                ydl_opts.pop('impersonate', None)
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                        return
                except DownloadCancelled:
                    self.cleanup_partial_files()
                    raise
                except Exception:
                    pass
            
            if isinstance(e, DownloadCancelled):
                self.cleanup_partial_files()
                raise
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
