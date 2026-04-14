"""
front/pages/scanner_page.py — Channel Scanner (PURE UI)
========================================================
Scans channels and displays bento cards. All workers in back/workers.py.
"""

import os
import glob
import datetime
import threading
from datetime import datetime as dt

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QScrollArea, QProgressBar, QMessageBox,
    QFileDialog, QCheckBox, QSpinBox, QGridLayout, QApplication
)
from PyQt5.QtGui import QPixmap, QFont, QCursor
from PyQt5.QtCore import Qt, pyqtSignal, QThreadPool, QTimer

from front.design import COLORS as C, FONT_HEADLINE, FONT_BODY, BORDER_RADIUS_CARD
from front.pages.analyze_page import CopyButton
from back.tracker import DailymotionTracker
from back.workers import ScannerSignals, ScanDownloadWorker
from back.config import save_download_path
from back.api_client import fetch_thumbnail_data


# ──────────────────────────────────────────────────────────────
# ScannerVideoCard — Bento card with checkbox overlay
# ──────────────────────────────────────────────────────────────
class ScannerVideoCard(QFrame):
    download_single = pyqtSignal(dict)

    def __init__(self, video_data: dict):
        super().__init__()
        self.video_data = video_data
        self.video_id = video_data.get("id", "")
        self._build_ui()

    def _build_ui(self):
        self.setObjectName("ScannerCard")
        self.setFixedWidth(480)
        self.setStyleSheet(f"""
            QFrame#ScannerCard {{
                background-color: #1a1a2a;
                border: 2px solid {C['outline_variant']}30;
                border-radius: {BORDER_RADIUS_CARD}px;
            }}
            QFrame#ScannerCard:hover {{
                background-color: #1e1e2e;
            }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Thumbnail
        thumb_container = QFrame()
        thumb_container.setFixedHeight(270)
        thumb_container.setStyleSheet(
            f"background-color: #000; "
            f"border-top-left-radius: {BORDER_RADIUS_CARD}px; "
            f"border-top-right-radius: {BORDER_RADIUS_CARD}px;"
        )

        thumb_label = QLabel()
        thumb_label.setAlignment(Qt.AlignCenter)
        thumb_url = self.video_data.get('thumbnail')
        if thumb_url:
            try:
                img_data = fetch_thumbnail_data(thumb_url)
                pixmap = QPixmap()
                pixmap.loadFromData(img_data)
                pixmap = pixmap.scaled(480, 270, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                thumb_label.setPixmap(pixmap)
            except Exception:
                thumb_label.setText("")

        thumb_label.setParent(thumb_container)
        thumb_label.setGeometry(0, 0, 480, 270)

        self.checkbox = QCheckBox()
        self.checkbox.setParent(thumb_container)
        self.checkbox.move(12, 12)
        self.checkbox.setCursor(QCursor(Qt.PointingHandCursor))
        self.checkbox.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 24px; height: 24px; border-radius: 6px;
                border: 2px solid {C['primary']}; background: #00000080;
            }}
            QCheckBox::indicator:checked {{
                background: {C['primary']}; border: 2px solid {C['primary']};
            }}
        """)

        dl_overlay = QPushButton("⬇")
        dl_overlay.setFixedSize(36, 36)
        dl_overlay.setCursor(QCursor(Qt.PointingHandCursor))
        dl_overlay.setToolTip("Download this video")
        dl_overlay.setStyleSheet(f"""
            QPushButton {{ background-color: {C['primary']}; color: {C['on_primary']}; border: none; border-radius: 18px; font-size: 16px; font-weight: bold; }}
            QPushButton:hover {{ background-color: {C['primary_dim']}; }}
        """)
        dl_overlay.setParent(thumb_container)
        dl_overlay.move(480 - 46, 10)
        dl_overlay.clicked.connect(lambda: self.download_single.emit(self.video_data))

        # Body
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 20, 20, 20)
        body_layout.setSpacing(12)

        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        title_str = (self.video_data.get('title') or 'Unknown').upper()
        title_label = QLabel(title_str)
        title_label.setWordWrap(True)
        title_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        title_label.setStyleSheet(f"color: {C['on_surface']}; font-size: 15px; font-weight: 800; font-family: '{FONT_HEADLINE}';")
        copy_title_btn = CopyButton(title_str, "TITLE")
        copy_title_btn.setFixedWidth(80)
        title_row.addWidget(title_label, 1)
        title_row.addWidget(copy_title_btn, 0)

        channel_name = self.video_data.get('channel') or self.video_data.get('uploader') or 'N/A'
        owner_name = self.video_data.get('owner') or self.video_data.get('uploader_id') or 'N/A'
        identity = QLabel(
            f"<span style='color: {C['primary']}; font-weight: bold;'>{channel_name}</span>"
            f" <span style='color: {C['outline_variant']};'>•</span> "
            f"<span style='color: {C['on_surface']};'>{owner_name}</span>"
        )
        identity.setStyleSheet("font-size: 12px;")
        identity.setTextInteractionFlags(Qt.TextSelectableByMouse)

        title_box = QVBoxLayout()
        title_box.setSpacing(5)
        title_box.addLayout(title_row)
        title_box.addWidget(identity)

        # Stats
        stats_frame = QFrame()
        stats_frame.setStyleSheet("padding: 5px 0px;")
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 5, 0, 5)
        stats_layout.setSpacing(8)
        v_24h = int(self.video_data.get('views_last_day') or 0)
        v_1h = int(self.video_data.get('views_last_hour') or 0)
        v_total = max(int(self.video_data.get('views_total') or self.video_data.get('view_count') or 0), v_24h, v_1h)
        stats_layout.addWidget(self._stat_box("Total", f"{v_total:,}", C['on_surface']))
        stats_layout.addWidget(self._stat_box("24h", f"{v_24h:,}", C['secondary']))
        stats_layout.addWidget(self._stat_box("1h", f"{v_1h:,}", C['primary']))

        # Geoblock
        geoblock = str(self.video_data.get('geoblocking') or 'allow')
        geo_frame = QFrame()
        if "deny" in geoblock:
            geo_frame.setStyleSheet(f"background-color: {C['error']}15; border-radius: 8px;")
            geo_layout = QVBoxLayout(geo_frame)
            geo_layout.addWidget(QLabel("STATUS: DENY"))
            geo_layout.addWidget(QLabel("Geoblocking active."))
        else:
            geo_frame.setStyleSheet(f"background-color: {C['secondary']}25; border-radius: 8px; border: 1px solid {C['secondary']}40;")
            geo_layout = QVBoxLayout(geo_frame)
            gs = QLabel("STATUS: NO GEOBLOCK")
            gs.setStyleSheet(f"color: {C['secondary']}; font-size: 11px; font-weight: bold; background: transparent; border: none;")
            gd = QLabel("Signal clear. Content is available globally.")
            gd.setStyleSheet(f"color: {C['on_surface']}; font-size: 10px; background: transparent; border: none;")
            geo_layout.addWidget(gs)
            geo_layout.addWidget(gd)

        # Footer
        footer = QVBoxLayout()
        footer.setSpacing(6)
        up_ts = self.video_data.get('updated_time') or self.video_data.get('timestamp') or 0
        if up_ts:
            try:
                date_str = datetime.datetime.fromtimestamp(up_ts).strftime("%Y-%m-%d %H:%M:%S")
                footer.addWidget(QLabel(f"Updated: {date_str}"))
            except Exception:
                pass

        video_url = self.video_data.get('url', '')
        url_row = QHBoxLayout()
        url_row.setSpacing(6)
        url_label = QLabel(f"URL: <a href='{video_url}' style='color: {C['primary']}; text-decoration: none;'>{video_url}</a>")
        url_label.setStyleSheet(f"color: {C['on_surface_variant']}; font-size: 11px;")
        url_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
        url_label.setOpenExternalLinks(True)
        url_label.setWordWrap(True)
        url_row.addWidget(url_label, 1)
        if video_url:
            url_row.addWidget(CopyButton(video_url, "URL"))
        footer.addLayout(url_row)

        thumb_url_str = self.video_data.get('thumbnail', '')
        if thumb_url_str:
            thumb_row = QHBoxLayout()
            thumb_row.setSpacing(6)
            thumb_link = QLabel(f"Thumb: <a href='{thumb_url_str}' style='color: {C['primary']};'>{thumb_url_str[:60]}...</a>")
            thumb_link.setStyleSheet(f"color: {C['on_surface_variant']}; font-size: 11px;")
            thumb_link.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
            thumb_link.setOpenExternalLinks(True)
            thumb_link.setWordWrap(True)
            thumb_row.addWidget(thumb_link, 1)
            thumb_row.addWidget(CopyButton(thumb_url_str, "THUMB"))
            footer.addLayout(thumb_row)

        body_layout.addLayout(title_box)
        body_layout.addWidget(stats_frame)
        body_layout.addWidget(geo_frame)
        body_layout.addLayout(footer)

        self.progress = QProgressBar()
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(
            f"QProgressBar {{ background: {C['surface_container_highest']}; border-radius: 3px; }} "
            f"QProgressBar::chunk {{ background: {C['primary']}; border-radius: 3px; }}"
        )
        self.progress.setValue(0)
        self.progress.hide()
        body_layout.addWidget(self.progress)

        self.status_label = QLabel("READY")
        self.status_label.setStyleSheet(f"color: {C['on_surface_variant']}; font-size: 10px; font-weight: bold; background: transparent; border: none;")
        body_layout.addWidget(self.status_label)

        main_layout.addWidget(thumb_container)
        main_layout.addWidget(body)

    def _stat_box(self, label, value, color):
        box = QFrame()
        box.setStyleSheet(f"""
            QFrame {{ background-color: {C['surface_container_high']}; border: 2px solid {C['outline_variant']}15; border-radius: 10px; padding: 8px; }}
        """)
        layout = QVBoxLayout(box)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)
        cap = QLabel(label.upper())
        cap.setStyleSheet(f"color: {C['on_surface_variant']}; font-size: 9px; font-weight: bold; letter-spacing: 1px; background: transparent; border: none;")
        val = QLabel(str(value))
        val.setStyleSheet(f"color: {color}; font-size: 17px; font-weight: 800; font-family: '{FONT_HEADLINE}'; background: transparent; border: none;")
        val.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(cap)
        layout.addWidget(val)
        return box

    def set_progress(self, fraction: float, speed: str):
        self.progress.show()
        self.progress.setValue(int(fraction * 100))
        self.status_label.setText(f"DOWNLOADING... {int(fraction * 100)}% ({speed})")
        self.status_label.setStyleSheet(f"color: {C['primary']}; font-size: 10px; border: none; background: transparent;")

    def set_status(self, text: str, state: str = "normal"):
        self.status_label.setText(text)
        color_map = {"success": C["secondary"], "error": C["error"], "active": C["primary"]}
        color = color_map.get(state, C["on_surface_variant"])
        self.status_label.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: bold; border: none; background: transparent;")


# ──────────────────────────────────────────────────────────────
# Scanner Page
# ──────────────────────────────────────────────────────────────
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
        s.status_msg.connect(self._on_status_msg)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 20, 30, 20)
        root.setSpacing(20)

        header = QLabel("Channel Scanner")
        header.setFont(QFont(FONT_HEADLINE, 22, QFont.ExtraBold))
        header.setStyleSheet(f"color: {C['on_surface']};")
        root.addWidget(header)

        sub = QLabel("Paste a channel URL to scan the latest videos. Select and download them.")
        sub.setStyleSheet(f"color: {C['on_surface_variant']}; font-size: 13px;")
        root.addWidget(sub)

        folder_row = QHBoxLayout()
        folder_row.setSpacing(10)
        self.folder_label = QLabel(f"📁  {self.tracker.download_path}")
        self.folder_label.setStyleSheet(f"color: {C['secondary']}; font-size: 12px; font-weight: bold;")
        folder_row.addWidget(self.folder_label)
        folder_row.addStretch()
        change_btn = QPushButton("Change Folder")
        change_btn.setFixedWidth(130)
        change_btn.clicked.connect(self._change_folder)
        folder_row.addWidget(change_btn)
        root.addLayout(folder_row)

        ctrl = QHBoxLayout()
        ctrl.setSpacing(10)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste Channel URL...")
        self.url_input.returnPressed.connect(self._start_scan)
        ctrl.addWidget(self.url_input, 1)
        self.scan_count = QSpinBox()
        self.scan_count.setRange(1, 100)
        self.scan_count.setValue(20)
        self.scan_count.setToolTip("Number of videos to scan")
        ctrl.addWidget(self.scan_count)
        self.scan_btn = QPushButton("SCAN CHANNEL")
        self.scan_btn.setObjectName("ActionButton")
        self.scan_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.scan_btn.clicked.connect(self._start_scan)
        ctrl.addWidget(self.scan_btn)
        root.addLayout(ctrl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        container.setStyleSheet(f"background-color: {C['surface']};")
        wrapper = QHBoxLayout(container)
        wrapper.setContentsMargins(0, 0, 0, 0)
        wrapper.addStretch()
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.grid_layout.setSpacing(24)
        wrapper.addWidget(self.grid_widget)
        wrapper.addStretch()
        scroll.setWidget(container)
        root.addWidget(scroll, 1)

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(8)
        self.clear_all_btn = QPushButton("🗑 CLEAR ALL")
        self.clear_all_btn.setObjectName("DangerButton")
        self.clear_all_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.clear_all_btn.setFixedHeight(45)
        self.clear_all_btn.setFixedWidth(140)
        self.clear_all_btn.clicked.connect(self._clear_all_cards)
        bottom_row.addWidget(self.clear_all_btn)
        self.dl_btn = QPushButton("DOWNLOAD SELECTED VIDEOS")
        self.dl_btn.setObjectName("ActionButton")
        self.dl_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.dl_btn.setFixedHeight(45)
        self.dl_btn.clicked.connect(self._start_download_queue)
        bottom_row.addWidget(self.dl_btn, 1)
        self.cancel_dl_btn = QPushButton("⏹ CANCEL")
        self.cancel_dl_btn.setObjectName("DangerButton")
        self.cancel_dl_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.cancel_dl_btn.setFixedHeight(45)
        self.cancel_dl_btn.setFixedWidth(100)
        self.cancel_dl_btn.setVisible(False)
        self.cancel_dl_btn.clicked.connect(self._cancel_downloads)
        bottom_row.addWidget(self.cancel_dl_btn)
        root.addLayout(bottom_row)

        self.status_bar = QLabel("🚀 Ready")
        self.status_bar.setStyleSheet(
            f"color: {C['on_surface_variant']}; font-size: 12px; font-weight: bold; "
            f"padding: 8px 12px; background-color: {C['surface_container']}; border-radius: 8px;"
        )
        root.addWidget(self.status_bar)

    def _change_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder", self.tracker.download_path)
        if path:
            self.tracker.set_download_path(path)
            self.folder_label.setText(f"📁  {path}")
            save_download_path(path)

    def _start_scan(self):
        url = self.url_input.text().strip()
        if not url:
            return
        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("SCANNING...")
        self.status_bar.setText(f"🔍 Scanning: {url}")
        count = self.scan_count.value()
        threading.Thread(target=self._scan_worker, args=(url, count), daemon=True).start()

    def _scan_worker(self, url, count):
        try:
            results = self.tracker.get_latest_videos(url, count)
            if not results:
                self.signals.scan_error.emit("Không tìm thấy video nào.")
            else:
                self.signals.scan_done.emit(results)
        except Exception as e:
            self.signals.scan_error.emit(str(e))

    def _on_scan_done(self, results: list):
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("SCAN CHANNEL")
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.video_widgets.clear()
        card_idx = 0
        for data in results:
            vid = data.get("id", str(card_idx))
            if "id" not in data:
                data["id"] = vid
            card = ScannerVideoCard(data)
            card.download_single.connect(self._download_single_video)
            self.video_widgets[vid] = card
            self.grid_layout.addWidget(card, card_idx // 2, card_idx % 2)
            card_idx += 1
        self.status_bar.setText(f"✅ Found {len(results)} videos")

    def _on_scan_error(self, err: str):
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("SCAN CHANNEL")
        self.status_bar.setText("❌ Scan failed")
        QMessageBox.warning(self, "Scan Error", f"Không thể quét kênh này:\n\n{err}")

    def _clear_all_cards(self):
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.video_widgets.clear()
        self.status_bar.setText("🗑 Cleared all cards")

    def _cancel_downloads(self):
        self._cancel_event.set()
        self.cancel_dl_btn.setEnabled(False)
        self.cancel_dl_btn.setText("Cancelling...")
        self.status_bar.setText("⏹ Cancelling — cleaning up partial files...")
        threading.Thread(target=self._cleanup_and_signal, daemon=True).start()

    def _cleanup_and_signal(self):
        import time
        time.sleep(1.5)
        patterns = ["*.part", "*.ytdl", "*.part-Frag*", "Frag*", "*.f[0-9]*.mp4", "*.f[0-9]*.webm", "*.f[0-9]*.m4a"]
        for pattern in patterns:
            for path in glob.glob(os.path.join(self.tracker.download_path, pattern)):
                try:
                    os.remove(path)
                except Exception:
                    pass
        self.signals.all_cancelled.emit()

    def _on_all_cancelled(self):
        for card in self.video_widgets.values():
            if card.status_label.text() not in ("DOWNLOADED",):
                card.set_status("⏹ CANCELLED", "error")
        self.dl_btn.setEnabled(True)
        self.cancel_dl_btn.setVisible(False)
        self.cancel_dl_btn.setEnabled(True)
        self.cancel_dl_btn.setText("⏹ CANCEL")
        self._cancel_event.clear()
        self.status_bar.setText("⏹ Download cancelled. Partial files deleted.")

    def _download_single_video(self, video_data: dict):
        vid = video_data.get("id", "")
        if vid in self.video_widgets:
            self.video_widgets[vid].set_status("QUEUED", "active")
        self._cancel_event.clear()
        self.cancel_dl_btn.setVisible(True)
        self.cancel_dl_btn.setEnabled(True)
        self.status_bar.setText(f"⬇ Downloading: {video_data.get('title', '')[:40]}")
        self.threadpool.start(ScanDownloadWorker(self.tracker, video_data, self.signals, self._cancel_event))

    def _start_download_queue(self):
        selected = [
            w.video_data for w in self.video_widgets.values()
            if w.checkbox.isChecked() and w.status_label.text() not in ("DOWNLOADED", "⏹ CANCELLED")
        ]
        if not selected:
            QMessageBox.information(self, "Selection", "No videos selected!")
            return
        self._cancel_event.clear()
        self.dl_btn.setEnabled(False)
        self.cancel_dl_btn.setVisible(True)
        self.cancel_dl_btn.setEnabled(True)
        self.status_bar.setText(f"⬇ Downloading {len(selected)} videos...")
        for data in selected:
            vid = data.get("id", "")
            if vid in self.video_widgets:
                self.video_widgets[vid].set_status("QUEUED", "normal")
            self.threadpool.start(ScanDownloadWorker(self.tracker, data, self.signals, self._cancel_event))

    def _on_download_finished(self, _vid: str):
        if self.threadpool.activeThreadCount() == 0:
            self.dl_btn.setEnabled(True)
            self.cancel_dl_btn.setVisible(False)
            self._cancel_event.clear()

    def _on_download_progress(self, vid: str, frac: float, _pct: str, speed: str):
        if vid in self.video_widgets:
            self.video_widgets[vid].set_progress(frac, speed)

    def _on_download_status(self, vid: str, status: str):
        if vid in self.video_widgets:
            state = "success" if "DOWN" in status else "active"
            self.video_widgets[vid].set_status(status, state)

    def _on_download_error(self, vid: str, err: str):
        if vid in self.video_widgets:
            self.video_widgets[vid].set_status(f"ERR: {err[:50]}", "error")
        if any(kw in err.lower() for kw in ['404', 'not found', 'deleted', 'unavailable', 'private']):
            QMessageBox.warning(self, "Video Unavailable", f"Video {vid} không khả dụng.")

    def _on_status_msg(self, text: str):
        self.status_bar.setText(text)
