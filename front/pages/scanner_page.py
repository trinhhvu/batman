
import os
import glob
import datetime
import threading
from datetime import datetime as dt

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QScrollArea, QProgressBar, QMessageBox,
    QFileDialog, QCheckBox, QSpinBox, QGridLayout, QApplication,
    QGraphicsDropShadowEffect, QListView, QComboBox
)
from PyQt5.QtGui import QPixmap, QFont, QCursor, QColor
from PyQt5.QtCore import Qt, pyqtSignal, QThreadPool, QTimer

from front.design import COLORS as C, FONT_HEADLINE, FONT_BODY, BORDER_RADIUS_CARD, action_btn_style, danger_btn_style
from front.pages.analyze_page import CopyButton
from back.tracker import DailymotionTracker
from back.workers import ScannerSignals, ScanDownloadWorker
from back.config import save_download_path
from back.api_client import fetch_thumbnail_data


class ScannerVideoCard(QFrame):
    download_single = pyqtSignal(dict)

    def __init__(self, video_data: dict):
        super().__init__()
        self.video_data = video_data
        self.video_id = video_data.get("id", "")
        self._build_ui()

    def _build_ui(self):
        self.setObjectName("ScannerVideoCard")
        self.setFixedWidth(460)
        # Style is now handled globally in design.py

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Thumbnail Area
        thumb_container = QFrame()
        thumb_container.setFixedHeight(260)
        thumb_container.setObjectName("CardThumb")
        
        thumb_label = QLabel(thumb_container)
        thumb_label.setGeometry(0, 0, 460, 260)
        thumb_label.setAlignment(Qt.AlignCenter)
        
        thumb_url = self.video_data.get('thumbnail')
        if thumb_url:
            try:
                img_data = fetch_thumbnail_data(thumb_url)
                pixmap = QPixmap()
                pixmap.loadFromData(img_data)
                pixmap = pixmap.scaled(460, 260, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                thumb_label.setPixmap(pixmap)
            except: pass

        # Selection Checkbox
        self.checkbox = QCheckBox(thumb_container)
        self.checkbox.move(16, 16)
        self.checkbox.setCursor(Qt.PointingHandCursor)

        # Content Body
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(24, 24, 24, 24)
        body_layout.setSpacing(16)

        title_str = (self.video_data.get('title') or 'Unknown').upper()
        title_label = QLabel(title_str)
        title_label.setWordWrap(True)
        title_label.setFont(QFont(FONT_HEADLINE, 11, QFont.Bold))
        body_layout.addWidget(title_label)

        # Stats
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(8)
        v_24h = int(self.video_data.get('views_last_day') or 0)
        v_1h = int(self.video_data.get('views_last_hour') or 0)
        
        stats_layout.addWidget(self._stat_box("24H", f"{v_24h:,}"))
        stats_layout.addWidget(self._stat_box("1H", f"{v_1h:,}"))
        body_layout.addLayout(stats_layout)

        # Progress / Status
        self.progress = QProgressBar()
        self.progress.setFixedHeight(8)
        self.progress.setTextVisible(False)
        self.progress.hide()
        body_layout.addWidget(self.progress)

        self.status_label = QLabel("READY")
        self.status_label.setObjectName("StatusLabel")
        body_layout.addWidget(self.status_label)
        
        main_layout.addWidget(thumb_container)
        main_layout.addWidget(body)

    def _stat_box(self, label, value):
        box = QFrame()
        box.setObjectName("StatBox")
        l = QVBoxLayout(box)
        l.setContentsMargins(16, 12, 16, 12)
        l.setSpacing(4)
        
        cap = QLabel(label)
        cap.setObjectName("SectionTitle")
        val = QLabel(value)
        val.setFont(QFont(FONT_HEADLINE, 14, QFont.Bold))
        
        l.addWidget(cap)
        l.addWidget(val)
        return box

    def set_progress(self, frac, speed):
        self.progress.show()
        self.progress.setValue(int(frac * 100))
        self.status_label.setText(f"DOWNLOADING {int(frac * 100)}% • {speed}")

    def set_status(self, text, state="normal"):
        self.status_label.setText(text.upper())
        self.status_label.setProperty("state", state)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)


class ScannerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tracker = DailymotionTracker()
        self.signals = ScannerSignals()
        self.threadpool = QThreadPool()
        self.video_widgets: dict[str, ScannerVideoCard] = {}
        self._cancel_event = threading.Event()
        
        max_threads = int(self.tracker.config.get("max_concurrent_syncs", 3))
        self.threadpool.setMaxThreadCount(max_threads)
        self.setObjectName("ScannerPage")
        self._build_ui()
        self._connect_signals()

    def _connect_signals(self):
        s = self.signals
        s.scan_done.connect(self._on_scan_done)
        s.scan_error.connect(self._on_scan_error)
        s.download_progress.connect(self._on_download_progress)
        s.download_status.connect(self._on_download_status)
        s.download_error.connect(self._on_download_error)
        s.download_finished.connect(self._on_download_finished)
        s.all_cancelled.connect(self._on_all_cancelled)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(32)

        header = QVBoxLayout()
        self.title = QLabel("Channel Scanner")
        self.title.setObjectName("PageTitle")
        header.addWidget(self.title)
        self.subtitle = QLabel("Paste a channel URL to scan latest videos and batch download.")
        self.subtitle.setObjectName("SubtitleLabel")
        header.addWidget(self.subtitle)
        layout.addLayout(header)

        # Toolbar
        self.toolbar = QFrame()
        self.toolbar.setObjectName("BentoCard")
        tool_layout = QHBoxLayout(self.toolbar)
        tool_layout.setContentsMargins(20, 10, 20, 10)
        tool_layout.setSpacing(12)
        
        self.url_input = QLineEdit()
        self.url_input.setObjectName("ScannerInput")
        self.url_input.setPlaceholderText("Paste Channel URL...")
        self.url_input.setMinimumHeight(44)
        self.url_input.returnPressed.connect(self._start_scan)
        tool_layout.addWidget(self.url_input, 1)
        
        self.scan_count = QSpinBox()
        self.scan_count.setObjectName("ScannerInput")
        self.scan_count.setRange(1, 100)
        self.scan_count.setValue(20)
        self.scan_count.setMinimumHeight(44)
        tool_layout.addWidget(self.scan_count)
        
        self.scan_btn = QPushButton("SCAN CHANNEL")
        self.scan_btn.setObjectName("ActionButton")
        self.scan_btn.setFixedSize(160, 44)
        self.scan_btn.setCursor(Qt.PointingHandCursor)
        self.scan_btn.clicked.connect(self._start_scan)
        tool_layout.addWidget(self.scan_btn)
        layout.addWidget(self.toolbar)

        # Results Grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(24)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        scroll.setWidget(self.grid_widget)
        layout.addWidget(scroll, 1)

        # Bottom Actions
        actions = QHBoxLayout()
        self.dl_btn = QPushButton("DOWNLOAD SELECTED")
        self.dl_btn.setStyleSheet(action_btn_style())
        self.dl_btn.setFixedSize(220, 48)
        self.dl_btn.setCursor(Qt.PointingHandCursor)
        self.dl_btn.clicked.connect(self._start_download_queue)
        actions.addWidget(self.dl_btn)
        
        self.cancel_dl_btn = QPushButton("STOP")
        self.cancel_dl_btn.setStyleSheet(danger_btn_style())
        self.cancel_dl_btn.setFixedSize(120, 48)
        self.cancel_dl_btn.setVisible(False)
        self.cancel_dl_btn.clicked.connect(self._cancel_downloads)
        actions.addWidget(self.cancel_dl_btn)
        actions.addStretch()
        
        self.status_bar = QLabel("Ready")
        self.status_bar.setObjectName("SubtitleLabel")
        actions.addWidget(self.status_bar)
        layout.addLayout(actions)

    def _start_scan(self):
        url = self.url_input.text().strip()
        if not url: return
        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("...")
        self.status_bar.setText(f"Scanning...")
        threading.Thread(target=self._scan_worker, args=(url, self.scan_count.value()), daemon=True).start()

    def _scan_worker(self, url, count):
        try:
            results = self.tracker.get_latest_videos(url, count)
            self.signals.scan_done.emit(results or [])
        except Exception as e:
            self.signals.scan_error.emit(str(e))

    def _on_scan_done(self, results):
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("SCAN CHANNEL")
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self.video_widgets.clear()
        for i, data in enumerate(results):
            vid = data.get("id", str(i))
            card = ScannerVideoCard(data)
            self.video_widgets[vid] = card
            self.grid_layout.addWidget(card, i // 2, i % 2)
        self.status_bar.setText(f"Found {len(results)} videos")

    def _on_scan_error(self, err):
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("SCAN CHANNEL")
        QMessageBox.warning(self, "Scan Error", err)

    def _cancel_downloads(self):
        self._cancel_event.set()
        self.cancel_dl_btn.setEnabled(False)
        self.status_bar.setText("Stopping...")

    def _on_all_cancelled(self):
        self.dl_btn.setEnabled(True)
        self.cancel_dl_btn.setVisible(False)
        self._cancel_event.clear()
        self.status_bar.setText("Downloads stopped.")

    def _start_download_queue(self):
        selected = [w.video_data for w in self.video_widgets.values() if w.checkbox.isChecked()]
        if not selected: return
        self._cancel_event.clear()
        self.dl_btn.setEnabled(False)
        self.cancel_dl_btn.setVisible(True)
        self.cancel_dl_btn.setEnabled(True)
        for data in selected:
            self.threadpool.start(ScanDownloadWorker(self.tracker, data, self.signals, self._cancel_event))

    def _on_download_finished(self, _vid):
        if self.threadpool.activeThreadCount() == 0:
            self.dl_btn.setEnabled(True)
            self.cancel_dl_btn.setVisible(False)

    def _on_download_progress(self, vid, frac, _pct, speed):
        if vid in self.video_widgets: self.video_widgets[vid].set_progress(frac, speed)

    def _on_download_status(self, vid, status):
        if vid in self.video_widgets: self.video_widgets[vid].set_status(status, "active" if "DOWN" in status else "normal")

    def _on_download_error(self, vid, err):
        if vid in self.video_widgets: self.video_widgets[vid].set_status("ERROR", "error")

    def refresh_theme(self):
        """Standardized refresh handled by QApplication."""
        pass
