"""
engine.py — Download Engine with anti-bot bypass + cancellation support
=========================================================================
Wraps yt-dlp for video analysis and downloading.

Key features:
  1. Browser headers — giả lập Chrome user-agent để qua Dailymotion 401
  2. Auto-detect impersonation — chỉ dùng nếu curl_cffi có sẵn
  3. Cancel support — raises DownloadCancelled + cleanup partial files
  4. Retry & fragment resilience — 20 retries, 16 concurrent fragments

Dependencies: yt-dlp, utils.py
Optional: curl_cffi (for TLS impersonation — install with: pip install curl_cffi)
"""

import yt_dlp
import os
import re
import glob
import threading
from utils import get_ffmpeg_path


# ──────────────────────────────────────────────────────────────
# Auto-detect: can we use yt-dlp's impersonate feature?
# ──────────────────────────────────────────────────────────────
_CAN_IMPERSONATE = False
try:
    import curl_cffi  # noqa: F401
    _CAN_IMPERSONATE = True
except ImportError:
    pass


# ──────────────────────────────────────────────────────────────
# Custom exception
# ──────────────────────────────────────────────────────────────
class DownloadCancelled(Exception):
    """Raised inside the yt-dlp progress hook to abort downloading."""
    pass


# ──────────────────────────────────────────────────────────────
# Browser-like headers (always used, no extra deps needed)
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


def _get_base_opts() -> dict:
    """Build base yt-dlp options. Only adds 'impersonate' if curl_cffi exists."""
    opts = {
        'quiet': True,
        'no_warnings': True,
        'http_headers': dict(_BROWSER_HEADERS),
        'sleep_interval': 1,
        'max_sleep_interval': 3,
        'retries': 20,
        'fragment_retries': 20,
    }
    if _CAN_IMPERSONATE:
        opts['impersonate'] = 'chrome'
    return opts


class DownloadEngine:
    """
    yt-dlp wrapper with browser headers, cancellation, and temp-file cleanup.
    Thread-safe: cancel_download() can be called from any thread.
    """

    def __init__(self, download_path: str):
        self.download_path = download_path
        self._cancel_event = threading.Event()

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
        """Delete all yt-dlp temporary / partial files in download_path."""
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

    # ──────────────────────────────────────────────────────────
    # Core methods
    # ──────────────────────────────────────────────────────────

    def analyze_video(self, url: str) -> dict:
        """Extract video metadata. Falls back gracefully on 401."""
        opts = _get_base_opts()
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception as e:
            err = str(e)
            # Fallback: try with browser cookies
            if '401' in err or 'Unauthorized' in err:
                fallback = _get_base_opts()
                fallback.pop('impersonate', None)
                fallback['cookiesfrombrowser'] = ('chrome',)
                try:
                    with yt_dlp.YoutubeDL(fallback) as ydl:
                        return ydl.extract_info(url, download=False)
                except Exception:
                    pass
            raise

    def get_ydl_opts(self, quality: str, progress_hook) -> dict:
        """Configure yt-dlp download options with browser bypass."""
        q_map = {
            "Best Available": "bestvideo+bestaudio/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
            "720p":  "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
            "480p":  "bestvideo[height<=480]+bestaudio/best[height<=480]/best",
        }
        opts = _get_base_opts()
        opts.update({
            'format': q_map.get(quality, "best"),
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'ffmpeg_location': get_ffmpeg_path(),
            'concurrent_fragment_downloads': 16,
            'merge_output_format': 'mp4',
        })
        return opts

    def start_download(self, url: str, quality: str, progress_hook):
        """
        Download a video.
        Raises DownloadCancelled if cancel_download() was called.
        Cleans up partial files on cancellation or error.
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
        p_str = d.get('_percent_str', '0%')
        p_str = re.sub(r'\x1b\[[0-9;]*m', '', p_str).strip().replace('%', '')
        try:
            return float(p_str) / 100, p_str, d.get('_speed_str', 'N/A')
        except Exception:
            return 0.0, "0", "N/A"
    return None
