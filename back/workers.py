"""
back/workers.py — Background Workers (QThread / QRunnable)
===========================================================
All background processing threads live here.
Only imports QThread/QObject/pyqtSignal from PyQt5 — NO widget imports.
"""

import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, QRunnable

from back.api_client import (
    fetch_video_details, search_videos, extract_video_id, fetch_thumbnail_data,
)


# ──────────────────────────────────────────────────────────────
# Research Worker
# ──────────────────────────────────────────────────────────────
class ResearchWorker(QThread):
    """Searches Dailymotion then fetches granular details for each result."""
    card_ready = pyqtSignal(dict)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, query: str, sort_mode: str):
        super().__init__()
        self.query = query
        self.sort_mode = sort_mode
        self._is_running = True

    def run(self):
        try:
            vid_id = extract_video_id(self.query)
            if vid_id and ' ' not in self.query:
                video_ids = [vid_id]
            else:
                video_ids = search_videos(self.query, self.sort_mode, limit=20)

            if not self._is_running or not video_ids:
                self.finished.emit()
                return

            def _fetch_single(vid):
                try:
                    return fetch_video_details(vid)
                except Exception:
                    return None

            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(_fetch_single, vid) for vid in video_ids]
                for future in as_completed(futures):
                    if not self._is_running:
                        break
                    result = future.result()
                    if result:
                        self.card_ready.emit(result)

            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    def stop(self):
        self._is_running = False


# ──────────────────────────────────────────────────────────────
# Thumbnail Loader Worker
# ──────────────────────────────────────────────────────────────
class ThumbnailWorker(QThread):
    """Loads a thumbnail image in the background."""
    loaded = pyqtSignal(bytes)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        try:
            data = fetch_thumbnail_data(self.url)
            self.loaded.emit(data)
        except Exception:
            pass


# ──────────────────────────────────────────────────────────────
# Download Page Signals
# ──────────────────────────────────────────────────────────────
class DownloadWorkerSignals(QObject):
    update_progress = pyqtSignal(float, str, str)
    download_finished = pyqtSignal()
    download_error = pyqtSignal(str)
    download_cancelled = pyqtSignal()
    analysis_done = pyqtSignal(dict)
    analysis_error = pyqtSignal(str)
    status_text = pyqtSignal(str)
    refresh_queue = pyqtSignal()
    all_done = pyqtSignal()


# ──────────────────────────────────────────────────────────────
# Scanner Signals
# ──────────────────────────────────────────────────────────────
class ScannerSignals(QObject):
    scan_done = pyqtSignal(list)
    scan_error = pyqtSignal(str)
    download_progress = pyqtSignal(str, float, str, str)
    download_status = pyqtSignal(str, str)
    download_finished = pyqtSignal(str)
    download_error = pyqtSignal(str, str)
    all_cancelled = pyqtSignal()
    status_msg = pyqtSignal(str)


# ──────────────────────────────────────────────────────────────
# Scanner Download Worker (QRunnable for thread pool)
# ──────────────────────────────────────────────────────────────
class ScanDownloadWorker(QRunnable):
    """Downloads a single video from the scanner batch."""

    def __init__(self, tracker, video_data: dict,
                 signals: ScannerSignals, cancel_event: threading.Event):
        super().__init__()
        self.tracker = tracker
        self.video_data = video_data
        self.signals = signals
        self.cancel_event = cancel_event
        self.vid = video_data.get("id", "")

    @pyqtSlot()
    def run(self):
        if self.cancel_event.is_set():
            self.signals.download_finished.emit(self.vid)
            return
        try:
            def on_progress(vid, frac, pct, speed):
                if self.cancel_event.is_set():
                    raise Exception("Download cancelled by user")
                self.signals.download_progress.emit(vid, frac, pct, speed)

            self.tracker.download_video(self.video_data, progress_callback=on_progress)
            self.signals.download_status.emit(self.vid, "DOWNLOADED")
            self.signals.status_msg.emit(f"✅ Downloaded: {self.video_data['title'][:40]}")
        except Exception as e:
            err_str = str(e)
            if "cancelled" in err_str.lower():
                self.signals.download_status.emit(self.vid, "CANCELLED")
            else:
                self.signals.download_error.emit(self.vid, err_str)
                self.signals.status_msg.emit(f"❌ Error: {self.video_data['title'][:30]}")
        finally:
            self.signals.download_finished.emit(self.vid)
