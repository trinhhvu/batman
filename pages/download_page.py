"""
download_page.py — Downloader Page (PyQt5 rewrite)
====================================================
Replaces the old customtkinter gui.py with a PyQt5 implementation.
Provides: URL input, video analysis, queue management, download progress.

Backend logic is handled by engine.py and utils.py (unchanged).

Dependencies: PyQt5, requests, PIL, engine.py, utils.py, design.py
Used by: app.py (loaded into QStackedWidget)
"""

import os
import re
import time
import threading
from io import BytesIO

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QProgressBar, QScrollArea, QFrame, QMessageBox,
    QFileDialog, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QFont, QCursor
from PyQt5.QtCore import Qt, pyqtSignal, QObject

import requests
from PIL import Image

from engine import DownloadEngine, parse_progress
from utils import check_ffmpeg_exists
from design import COLORS as C, FONT_HEADLINE, FONT_BODY, BORDER_RADIUS_CARD


# ──────────────────────────────────────────────────────────────
# Helper: Thread-safe signal bridge (PyQt5 requires signals for UI updates)
# ──────────────────────────────────────────────────────────────
class WorkerSignals(QObject):
    """Signals to safely update UI from background threads."""
    update_progress = pyqtSignal(float, str, str)      # (fraction, percent_str, speed_str)
    download_finished = pyqtSignal()                     # one item done
    download_error = pyqtSignal(str)                     # error message
    analysis_done = pyqtSignal(dict)                     # video info dict
    analysis_error = pyqtSignal(str)                     # error message
    status_text = pyqtSignal(str)                        # status label text
    refresh_queue = pyqtSignal()                         # refresh queue display
    all_done = pyqtSignal()                              # entire queue finished


# ──────────────────────────────────────────────────────────────
# Queue Item Widget
# ──────────────────────────────────────────────────────────────
class QueueItemWidget(QFrame):
    """A single item in the download queue list."""

    def __init__(self, index, item_data, is_active, parent_page):
        super().__init__()
        self.index = index
        self.item_data = item_data
        self.parent_page = parent_page
        self.is_active = is_active
        self._build_ui()

    def _build_ui(self):
        bg = C['surface_container_high'] if self.is_active else C['surface_container']
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 2px solid {C['outline_variant']}20;
                border-radius: 12px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        # Number
        num = QLabel(f"{self.index + 1}")
        num.setFixedWidth(24)
        num.setStyleSheet(f"color: {C['on_surface_variant']}; font-weight: bold; font-size: 12px;")
        num.setAlignment(Qt.AlignCenter)
        layout.addWidget(num)

        # Title
        title_str = str(self.item_data.get('title', 'Video'))
        title = QLabel(title_str[:35] + ("..." if len(title_str) > 35 else ""))
        title.setStyleSheet(f"color: {C['on_surface']}; font-weight: {'800' if self.is_active else '500'}; font-size: 12px;")
        layout.addWidget(title, 1)

        # Status badge
        status = self.item_data.get('status', 'Waiting')
        if status == "Downloading":
            badge_bg = f"{C['secondary']}20"
            badge_color = C['secondary']
            badge_text = "● DOWNLOADING"
        elif status == "Error":
            badge_bg = f"{C['error']}20"
            badge_color = C['error']
            badge_text = "⚠ ERROR"
        else:
            badge_bg = f"{C['on_surface_variant']}15"
            badge_color = C['on_surface_variant']
            badge_text = "○ WAITING"

        badge = QLabel(badge_text)
        badge.setStyleSheet(f"""
            color: {badge_color};
            background-color: {badge_bg};
            font-size: 9px;
            font-weight: bold;
            padding: 3px 8px;
            border-radius: 8px;
            letter-spacing: 1px;
        """)
        layout.addWidget(badge)

        # Action buttons (disabled if active)
        btn_enabled = not self.is_active

        up_btn = QPushButton("▲")
        up_btn.setFixedSize(28, 28)
        up_btn.setEnabled(btn_enabled)
        up_btn.setStyleSheet(self._small_btn_qss())
        up_btn.clicked.connect(lambda: self.parent_page.move_up(self.index))
        layout.addWidget(up_btn)

        down_btn = QPushButton("▼")
        down_btn.setFixedSize(28, 28)
        down_btn.setEnabled(btn_enabled)
        down_btn.setStyleSheet(self._small_btn_qss())
        down_btn.clicked.connect(lambda: self.parent_page.move_down(self.index))
        layout.addWidget(down_btn)

        remove_btn = QPushButton("✕")
        remove_btn.setFixedSize(28, 28)
        remove_btn.setEnabled(btn_enabled)
        remove_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {C['error']}20;
                color: {C['error']};
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: {C['error']}40; }}
        """)
        remove_btn.clicked.connect(lambda: self.parent_page.remove_item(self.index))
        layout.addWidget(remove_btn)

    def _small_btn_qss(self):
        return f"""
            QPushButton {{
                background-color: {C['surface_container_highest']};
                color: {C['on_surface_variant']};
                border: none;
                border-radius: 6px;
                font-size: 11px;
            }}
            QPushButton:hover {{ background-color: {C['surface_bright']}; color: {C['on_surface']}; }}
            QPushButton:disabled {{ opacity: 0.3; }}
        """


# ──────────────────────────────────────────────────────────────
# Download Page (main widget)
# ──────────────────────────────────────────────────────────────
class DownloadPage(QWidget):
    """
    Full download page: URL input → Analyze → Preview → Add to Queue → Download.
    Drop-in replacement for the old customtkinter gui.py.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.queue = []
        self.is_downloading = False
        self.current_video_info = None
        self.engine = DownloadEngine(self.download_path)
        self.signals = WorkerSignals()
        self._thumb_pixmap = None  # prevent garbage collection

        self._connect_signals()
        self._build_ui()
        self._check_ffmpeg()

    def _connect_signals(self):
        """Connect thread-safe signals to UI update slots."""
        self.signals.update_progress.connect(self._on_progress)
        self.signals.download_finished.connect(self._on_download_finished)
        self.signals.download_error.connect(self._on_download_error)
        self.signals.analysis_done.connect(self._on_analysis_done)
        self.signals.analysis_error.connect(self._on_analysis_error)
        self.signals.status_text.connect(self._on_status_text)
        self.signals.refresh_queue.connect(self.refresh_queue_display)
        self.signals.all_done.connect(self._on_all_done)

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Left: Main content area ──
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(30, 20, 20, 20)
        left_layout.setSpacing(20)

        # Header
        header = QLabel("Video Downloader")
        header.setFont(QFont(FONT_HEADLINE, 22, QFont.ExtraBold))
        header.setStyleSheet(f"color: {C['on_surface']};")
        left_layout.addWidget(header)

        sub = QLabel("Paste a Dailymotion URL to analyze and download in high quality.")
        sub.setStyleSheet(f"color: {C['on_surface_variant']}; font-size: 13px;")
        left_layout.addWidget(sub)

        # URL input row
        url_row = QHBoxLayout()
        url_row.setSpacing(10)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste Dailymotion URL here...")
        self.url_input.returnPressed.connect(self._start_analyze)
        url_row.addWidget(self.url_input, 1)

        self.analyze_btn = QPushButton("ANALYZE")
        self.analyze_btn.setObjectName("ActionButton")
        self.analyze_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.analyze_btn.setFixedWidth(120)
        self.analyze_btn.clicked.connect(self._start_analyze)
        url_row.addWidget(self.analyze_btn)

        left_layout.addLayout(url_row)

        # Folder selection
        folder_row = QHBoxLayout()
        folder_row.setSpacing(10)
        self.folder_label = QLabel(f"📁  {os.path.basename(self.download_path)}")
        self.folder_label.setStyleSheet(f"color: {C['secondary']}; font-size: 12px; font-weight: bold;")
        folder_row.addWidget(self.folder_label)
        folder_row.addStretch()
        change_btn = QPushButton("Change Folder")
        change_btn.setFixedWidth(130)
        change_btn.clicked.connect(self._change_folder)
        folder_row.addWidget(change_btn)
        left_layout.addLayout(folder_row)

        # Preview section
        self.preview_frame = QFrame()
        self.preview_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {C['surface_container']};
                border: 2px solid {C['outline_variant']}15;
                border-radius: {BORDER_RADIUS_CARD}px;
            }}
        """)
        preview_layout = QVBoxLayout(self.preview_frame)
        preview_layout.setContentsMargins(20, 20, 20, 20)
        preview_layout.setSpacing(12)

        self.thumb_label = QLabel()
        self.thumb_label.setFixedHeight(180)
        self.thumb_label.setAlignment(Qt.AlignCenter)
        self.thumb_label.setStyleSheet(f"background-color: {C['surface_container_lowest']}; border-radius: 12px;")
        preview_layout.addWidget(self.thumb_label)

        self.title_label = QLabel("No video selected")
        self.title_label.setFont(QFont(FONT_HEADLINE, 14, QFont.Bold))
        self.title_label.setStyleSheet(f"color: {C['on_surface']}; background: transparent; border: none;")
        self.title_label.setWordWrap(True)
        preview_layout.addWidget(self.title_label)

        quality_row = QHBoxLayout()
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Best Available", "1080p", "720p", "480p"])
        self.quality_combo.setFixedWidth(200)
        quality_row.addWidget(self.quality_combo)
        quality_row.addStretch()

        self.add_queue_btn = QPushButton("ADD TO QUEUE")
        self.add_queue_btn.setObjectName("ActionButton")
        self.add_queue_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.add_queue_btn.setEnabled(False)
        self.add_queue_btn.setFixedWidth(160)
        self.add_queue_btn.clicked.connect(self._add_to_queue)
        quality_row.addWidget(self.add_queue_btn)

        preview_layout.addLayout(quality_row)
        left_layout.addWidget(self.preview_frame)

        # Progress section
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setRange(0, 1000)
        self.progress_bar.setValue(0)
        left_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"color: {C['secondary']}; font-size: 12px; font-weight: bold;")
        left_layout.addWidget(self.status_label)

        left_layout.addStretch()

        root.addWidget(left_panel, 3)

        # ── Right: Queue panel ──
        right_panel = QFrame()
        right_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {C['surface_container']};
                border-left: 2px solid {C['outline_variant']}15;
            }}
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)

        queue_header = QLabel("Download Queue")
        queue_header.setFont(QFont(FONT_HEADLINE, 16, QFont.Bold))
        queue_header.setStyleSheet(f"color: {C['on_surface']}; background: transparent; border: none;")
        right_layout.addWidget(queue_header)

        # Scrollable queue list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"background: transparent; border: none;")

        self.queue_container = QWidget()
        self.queue_container.setStyleSheet("background: transparent;")
        self.queue_layout = QVBoxLayout(self.queue_container)
        self.queue_layout.setContentsMargins(0, 0, 0, 0)
        self.queue_layout.setSpacing(8)
        self.queue_layout.setAlignment(Qt.AlignTop)

        scroll.setWidget(self.queue_container)
        right_layout.addWidget(scroll, 1)

        # Start button
        self.start_btn = QPushButton("START QUEUE DOWNLOAD")
        self.start_btn.setObjectName("ActionButton")
        self.start_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.start_btn.setFixedHeight(44)
        self.start_btn.clicked.connect(self._start_queue)
        right_layout.addWidget(self.start_btn)

        root.addWidget(right_panel, 2)

    # ──────────────────────────────────────────────────────────
    # Actions
    # ──────────────────────────────────────────────────────────

    def _check_ffmpeg(self):
        exists, path = check_ffmpeg_exists()
        if not exists:
            QMessageBox.warning(self, "System Warning",
                                f"ffmpeg not found!\nExpected: {path}\n\nOn macOS: brew install ffmpeg\nOn Windows: place ffmpeg.exe in app folder.")

    def _change_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Download Folder", self.download_path)
        if path:
            self.download_path = path
            self.engine.download_path = path
            self.folder_label.setText(f"📁  {os.path.basename(path)}")

    def _start_analyze(self):
        url = self.url_input.text().strip()
        if not url:
            return
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setText("Analyzing...")
        threading.Thread(target=self._analyze_worker, args=(url,), daemon=True).start()

    def _analyze_worker(self, url):
        try:
            info = self.engine.analyze_video(url)
            self.signals.analysis_done.emit(info)
        except Exception as e:
            self.signals.analysis_error.emit(str(e))

    def _on_analysis_done(self, info):
        self.current_video_info = info
        self.title_label.setText(info.get('title', 'Unknown'))
        self.add_queue_btn.setEnabled(True)
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("ANALYZE")

        # Load thumbnail in background
        thumb_url = info.get('thumbnail')
        if thumb_url:
            threading.Thread(target=self._load_thumb, args=(thumb_url,), daemon=True).start()

    def _on_analysis_error(self, msg):
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("ANALYZE")
        QMessageBox.warning(self, "Analysis Error", f"Could not analyze video:\n{msg}")

    def _load_thumb(self, url):
        try:
            data = requests.get(url, timeout=8).content
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            scaled = pixmap.scaled(400, 180, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self._thumb_pixmap = scaled  # prevent GC
            # Update UI on main thread
            from PyQt5.QtCore import QMetaObject, Q_ARG
            QMetaObject.invokeMethod(self.thumb_label, "setPixmap",
                                     Qt.QueuedConnection, Q_ARG(QPixmap, scaled))
        except Exception:
            pass

    def _add_to_queue(self):
        if not self.current_video_info:
            return
        item = {
            "url": self.url_input.text().strip(),
            "title": self.current_video_info.get('title', 'Video'),
            "quality": self.quality_combo.currentText(),
            "status": "Waiting"
        }
        self.queue.append(item)
        self.refresh_queue_display()
        self.url_input.clear()
        self.add_queue_btn.setEnabled(False)
        self.current_video_info = None

    # ── Queue management ──

    def refresh_queue_display(self):
        # Clear existing
        while self.queue_layout.count():
            child = self.queue_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for i, item in enumerate(self.queue):
            is_active = (i == 0 and self.is_downloading)
            widget = QueueItemWidget(i, item, is_active, self)
            self.queue_layout.addWidget(widget)

    def move_up(self, idx):
        if idx > 0:
            self.queue[idx], self.queue[idx - 1] = self.queue[idx - 1], self.queue[idx]
            self.refresh_queue_display()

    def move_down(self, idx):
        if idx < len(self.queue) - 1:
            self.queue[idx], self.queue[idx + 1] = self.queue[idx + 1], self.queue[idx]
            self.refresh_queue_display()

    def remove_item(self, idx):
        self.queue.pop(idx)
        self.refresh_queue_display()

    # ── Download processing ──

    def _start_queue(self):
        if self.is_downloading:
            return
        if not self.queue:
            QMessageBox.information(self, "Queue", "Queue is empty!")
            return
        self.is_downloading = True
        self.start_btn.setEnabled(False)
        self.start_btn.setText("PROCESSING...")
        threading.Thread(target=self._process_queue, daemon=True).start()

    def _process_queue(self):
        while self.queue:
            item = self.queue[0]
            item["status"] = "Downloading"
            self.signals.refresh_queue.emit()

            title_str = str(item.get('title', 'Video'))
            self.signals.status_text.emit(f"Downloading: {title_str[:40]}...")

            def hook(d):
                result = parse_progress(d)
                if result:
                    pf, ps, speed = result
                    self.signals.update_progress.emit(pf, ps, speed)

            try:
                self.engine.start_download(item['url'], item['quality'], hook)
                self.queue.pop(0)
                self.signals.refresh_queue.emit()
            except Exception as e:
                import traceback
                print(f"DEBUG ERROR:\n{traceback.format_exc()}")
                friendly = f"Video không hỗ trợ hoặc bị chặn.\nChi tiết: {str(e)}"
                self.signals.download_error.emit(friendly)
                if self.queue:
                    self.queue.pop(0)
                self.signals.refresh_queue.emit()

            time.sleep(1)

        self.is_downloading = False
        self.signals.all_done.emit()

    # ── Signal slots (run on main thread) ──

    def _on_progress(self, fraction, percent_str, speed_str):
        self.progress_bar.setValue(int(fraction * 1000))
        self.status_label.setText(f"Progress: {percent_str}% | Speed: {speed_str}")

    def _on_download_finished(self):
        pass

    def _on_download_error(self, msg):
        QMessageBox.warning(self, "Download Skip", msg)

    def _on_status_text(self, text):
        self.status_label.setText(text)

    def _on_all_done(self):
        self.progress_bar.setValue(0)
        self.status_label.setText("All tasks finished!")
        self.start_btn.setEnabled(True)
        self.start_btn.setText("START QUEUE DOWNLOAD")
