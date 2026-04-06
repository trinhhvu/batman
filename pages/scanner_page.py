"""
scanner_page.py — Channel Scanner & Batch Downloader (TRACK)
=============================================================
Scan a Dailymotion channel URL and list latest videos as bento-style
VideoCards (same rich format as the Analyze page). User can select
videos via checkboxes and batch-download them.

Dependencies: PyQt5, requests, tracker.py, design.py
Used by: gui.py (loaded into QStackedWidget)
"""

import os
import re
import glob
import threading
import webbrowser
import datetime
from datetime import datetime as dt

import requests

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QFrame, QScrollArea, QProgressBar, QMessageBox, QTabWidget,
    QFileDialog, QCheckBox, QSpinBox, QInputDialog, QGridLayout, QApplication
)
from PyQt5.QtGui import QPixmap, QFont, QCursor
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThreadPool, QRunnable, pyqtSlot, QTimer

from tracker import DailymotionTracker, OAUTH_REDIRECT, OAUTH_SCOPE
from design import COLORS as C, FONT_HEADLINE, FONT_BODY, BORDER_RADIUS_CARD


# ──────────────────────────────────────────────────────────────
# CopyButton (reused from analyze_page)
# ──────────────────────────────────────────────────────────────
class CopyButton(QPushButton):
    """A polished copy button with icon + animated feedback."""

    def __init__(self, text_to_copy: str, label: str = "COPY", parent=None):
        super().__init__(parent)
        self._text_to_copy = text_to_copy
        self._default_label = label
        self.setText(f"📋 {label}")
        self.setFixedHeight(28)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet(self._default_qss())
        self.clicked.connect(self._do_copy)

    def _default_qss(self):
        return f"""
            QPushButton {{
                background-color: {C['surface_container_high']};
                color: {C['primary']};
                border: 1px solid {C['primary']}40;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 10px;
                font-weight: 700;
                font-family: '{FONT_HEADLINE}', sans-serif;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background-color: {C['primary']}20;
                border: 1px solid {C['primary']}80;
            }}
        """

    def _success_qss(self):
        return f"""
            QPushButton {{
                background-color: {C['secondary']}25;
                color: {C['secondary']};
                border: 1px solid {C['secondary']}60;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 10px;
                font-weight: 700;
                font-family: '{FONT_HEADLINE}', sans-serif;
                letter-spacing: 0.5px;
            }}
        """

    def _do_copy(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self._text_to_copy)
        self.setText("✅ COPIED!")
        self.setStyleSheet(self._success_qss())
        QTimer.singleShot(1500, self._reset)

    def _reset(self):
        self.setText(f"📋 {self._default_label}")
        self.setStyleSheet(self._default_qss())


# ──────────────────────────────────────────────────────────────
# ScannerVideoCard — bento card for scanned channel videos
# ──────────────────────────────────────────────────────────────
class ScannerVideoCard(QFrame):
    """Bento-style card for a scanned channel video with checkbox for selection."""

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

        # ── Thumbnail ──
        thumb_url = self.video_data.get('thumbnail', '')
        thumb_container = QFrame()
        thumb_container.setFixedHeight(270)
        thumb_container.setStyleSheet(
            f"background-color: #000; "
            f"border-top-left-radius: {BORDER_RADIUS_CARD}px; "
            f"border-top-right-radius: {BORDER_RADIUS_CARD}px;"
        )

        thumb_label = QLabel()
        thumb_label.setAlignment(Qt.AlignCenter)
        if thumb_url:
            try:
                img_data = requests.get(thumb_url, timeout=5).content
                pixmap = QPixmap()
                pixmap.loadFromData(img_data)
                pixmap = pixmap.scaled(480, 270, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                thumb_label.setPixmap(pixmap)
            except Exception:
                thumb_label.setText("")

        thumb_label.setParent(thumb_container)
        thumb_label.setGeometry(0, 0, 480, 270)

        # Checkbox overlay (top-left)
        self.checkbox = QCheckBox()
        self.checkbox.setParent(thumb_container)
        self.checkbox.move(12, 12)
        self.checkbox.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 24px; height: 24px; border-radius: 6px;
                border: 2px solid {C['primary']}; background: #00000080;
            }}
            QCheckBox::indicator:checked {{
                background: {C['primary']}; border: 2px solid {C['primary']};
            }}
        """)

        # ── Body ──
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 20, 20, 20)
        body_layout.setSpacing(12)

        # Title
        title_str = (self.video_data.get('title') or 'Unknown').upper()
        title_label = QLabel(title_str)
        title_label.setWordWrap(True)
        title_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        title_label.setStyleSheet(
            f"color: {C['on_surface']}; font-size: 15px; font-weight: 800; "
            f"font-family: '{FONT_HEADLINE}';"
        )
        body_layout.addWidget(title_label)

        # Stats row
        stats_frame = QFrame()
        stats_frame.setStyleSheet("padding: 5px 0px;")
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 5, 0, 5)
        stats_layout.setSpacing(8)

        v_total = int(self.video_data.get('view_count') or 0)
        dur = self.video_data.get('duration_string', '00:00')

        stats_layout.addWidget(self._stat_box("Views", f"{v_total:,}", C['on_surface']))
        stats_layout.addWidget(self._stat_box("Duration", str(dur), C['secondary']))

        body_layout.addWidget(stats_frame)

        # Footer: URL + Thumb copy
        video_url = self.video_data.get('url', '')
        footer = QVBoxLayout()
        footer.setSpacing(6)

        url_row = QHBoxLayout()
        url_row.setSpacing(6)
        url_label = QLabel(
            f"URL: <a href='{video_url}' style='color: {C['primary']}; "
            f"text-decoration: none;'>{video_url}</a>"
        )
        url_label.setStyleSheet(f"color: {C['on_surface_variant']}; font-size: 11px;")
        url_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
        url_label.setOpenExternalLinks(True)
        url_label.setWordWrap(True)
        url_row.addWidget(url_label, 1)
        if video_url:
            url_row.addWidget(CopyButton(video_url, "URL"))
        footer.addLayout(url_row)

        if thumb_url:
            thumb_row = QHBoxLayout()
            thumb_row.setSpacing(6)
            thumb_link = QLabel(
                f"Thumb: <a href='{thumb_url}' style='color: {C['primary']}; "
                f"text-decoration: none;'>{thumb_url[:60]}...</a>"
            )
            thumb_link.setStyleSheet(f"color: {C['on_surface_variant']}; font-size: 11px;")
            thumb_link.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
            thumb_link.setOpenExternalLinks(True)
            thumb_link.setWordWrap(True)
            thumb_row.addWidget(thumb_link, 1)
            thumb_row.addWidget(CopyButton(thumb_url, "THUMB"))
            footer.addLayout(thumb_row)

        body_layout.addLayout(footer)

        # Progress bar (hidden by default)
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

        # Status label
        self.status_label = QLabel("READY")
        self.status_label.setStyleSheet(
            f"color: {C['on_surface_variant']}; font-size: 10px; font-weight: bold; "
            f"background: transparent; border: none;"
        )
        body_layout.addWidget(self.status_label)

        main_layout.addWidget(thumb_container)
        main_layout.addWidget(body)

    def _stat_box(self, label, value, color):
        box = QFrame()
        box.setStyleSheet(f"""
            QFrame {{
                background-color: {C['surface_container_high']};
                border: 2px solid {C['outline_variant']}15;
                border-radius: 10px;
                padding: 8px;
            }}
        """)
        layout = QVBoxLayout(box)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)
        cap = QLabel(label.upper())
        cap.setStyleSheet(
            f"color: {C['on_surface_variant']}; font-size: 9px; font-weight: bold; "
            f"letter-spacing: 1px; background: transparent; border: none;"
        )
        val = QLabel(value)
        val.setStyleSheet(
            f"color: {color}; font-size: 17px; font-weight: 800; "
            f"font-family: '{FONT_HEADLINE}'; background: transparent; border: none;"
        )
        val.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(cap)
        layout.addWidget(val)
        return box

    def set_progress(self, fraction: float, speed: str):
        self.progress.show()
        self.progress.setValue(int(fraction * 100))
        self.status_label.setText(f"DOWNLOADING... {int(fraction * 100)}% ({speed})")
        self.status_label.setStyleSheet(
            f"color: {C['primary']}; font-size: 10px; border: none; background: transparent;"
        )

    def set_status(self, text: str, state: str = "normal"):
        self.status_label.setText(text)
        color_map = {
            "success": C["secondary"],
            "error": C["error"],
            "active": C["primary"],
        }
        color = color_map.get(state, C["on_surface_variant"])
        self.status_label.setStyleSheet(
            f"color: {color}; font-size: 10px; font-weight: bold; "
            f"border: none; background: transparent;"
        )


# ──────────────────────────────────────────────────────────────
# Background Workers
# ──────────────────────────────────────────────────────────────
class ScannerSignals(QObject):
    log = pyqtSignal(str)
    scan_done = pyqtSignal(list)
    scan_error = pyqtSignal(str)
    download_progress = pyqtSignal(str, float, str, str)
    download_status = pyqtSignal(str, str)
    download_finished = pyqtSignal(str)
    download_error = pyqtSignal(str, str)
    auth_result = pyqtSignal(bool, str)
    all_cancelled = pyqtSignal()              # emitted when cancel finishes cleanup


class ScanDownloadWorker(QRunnable):
    def __init__(self, tracker: DailymotionTracker, video_data: dict,
                 signals: ScannerSignals, cancel_event: threading.Event):
        super().__init__()
        self.tracker = tracker
        self.video_data = video_data
        self.signals = signals
        self.cancel_event = cancel_event
        self.vid = video_data["id"]

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
            self.signals.log.emit(f"[+] Downloaded: {self.video_data['title'][:30]}")
        except Exception as e:
            err_str = str(e)
            if "cancelled" in err_str.lower():
                self.signals.download_status.emit(self.vid, "CANCELLED")
            else:
                self.signals.download_error.emit(self.vid, err_str)
                self.signals.log.emit(f"[-] Download error ({self.vid}): {e}")
        finally:
            self.signals.download_finished.emit(self.vid)


class AuthPasswordWorker(QRunnable):
    def __init__(self, tracker, email, password, signals):
        super().__init__()
        self.tracker = tracker
        self.email = email
        self.password = password
        self.signals = signals

    @pyqtSlot()
    def run(self):
        try:
            self.tracker.login_via_password(self.email, self.password)
            info = self.tracker.get_user_info()
            name = info.get("screenname", "?")
            user = info.get("username", "?")
            self.signals.auth_result.emit(True, f"✅ Authenticated as: {name} (@{user})")
        except Exception as e:
            self.signals.auth_result.emit(False, str(e))


class AuthTestWorker(QRunnable):
    def __init__(self, tracker, signals, force_reauth=False):
        super().__init__()
        self.tracker = tracker
        self.signals = signals
        self.force_reauth = force_reauth

    @pyqtSlot()
    def run(self):
        try:
            if self.force_reauth:
                self.tracker.start_browser_auth()
            info = self.tracker.get_user_info()
            name = info.get("screenname", "?")
            user = info.get("username", "?")
            self.signals.auth_result.emit(True, f"✅ Authenticated as: {name} (@{user})")
        except Exception as e:
            self.signals.auth_result.emit(False, str(e))


# ──────────────────────────────────────────────────────────────
# Scanner Page Widget
# ──────────────────────────────────────────────────────────────
class ScannerPage(QWidget):
    """Channel Scanner: scan URL → bento cards → select → batch download."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tracker = DailymotionTracker()
        self.signals = ScannerSignals()
        self.threadpool = QThreadPool()
        self.video_widgets: dict[str, ScannerVideoCard] = {}
        self._cancel_event = threading.Event()   # set → cancel all running downloads

        max_threads = int(self.tracker.config.get("max_concurrent_syncs", 3))
        self.threadpool.setMaxThreadCount(max_threads)

        self._build_ui()
        self._connect_signals()
        self.signals.log.emit(f"🚀 Scanner ready. Concurrency: {max_threads}")

    def _connect_signals(self):
        s = self.signals
        s.log.connect(self._on_log)
        s.scan_done.connect(self._on_scan_done)
        s.scan_error.connect(self._on_scan_error)
        s.download_progress.connect(self._on_download_progress)
        s.download_status.connect(self._on_download_status)
        s.download_error.connect(self._on_download_error)
        s.download_finished.connect(self._on_download_finished)
        s.auth_result.connect(self._on_auth_result)
        s.all_cancelled.connect(self._on_all_cancelled)

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Left panel — scan controls + card grid ──
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(30, 20, 20, 20)
        left_layout.setSpacing(20)

        header = QLabel("Channel Scanner")
        header.setFont(QFont(FONT_HEADLINE, 22, QFont.ExtraBold))
        header.setStyleSheet(f"color: {C['on_surface']};")
        left_layout.addWidget(header)

        sub = QLabel("Paste a channel URL to scan the latest videos. Select and download them.")
        sub.setStyleSheet(f"color: {C['on_surface_variant']}; font-size: 13px;")
        left_layout.addWidget(sub)

        # Control row
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
        left_layout.addLayout(ctrl)

        # Card grid (scrollable)
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
        left_layout.addWidget(scroll, 1)

        # Bottom row: Clear All + Download Selected + Cancel
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

        left_layout.addLayout(bottom_row)

        root.addWidget(left_panel, 7)

        # ── Right panel — Logs + Settings ──
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

        tabs = QTabWidget()

        # Logs tab
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet(
            f"background: {C['surface_container_lowest']}; "
            f"font-family: 'Consolas'; font-size: 11px;"
        )
        log_layout.addWidget(self.log_area)
        tabs.addTab(log_tab, "Logs")

        # Settings tab
        set_tab = QWidget()
        set_layout = QVBoxLayout(set_tab)

        self.inp_dl_path = QLabel(f"📁 {self.tracker.download_path}")
        set_layout.addWidget(self.inp_dl_path)
        btn_folder = QPushButton("Change Folder")
        btn_folder.clicked.connect(self._change_folder)
        set_layout.addWidget(btn_folder)

        set_layout.addWidget(QLabel("Dailymotion Credentials:"))
        self.inp_api = QLineEdit(self.tracker.config.get("api_key", ""))
        self.inp_api.setPlaceholderText("API Key / Client ID")
        set_layout.addWidget(self.inp_api)

        self.inp_secret = QLineEdit(self.tracker.config.get("api_secret", ""))
        self.inp_secret.setEchoMode(QLineEdit.Password)
        self.inp_secret.setPlaceholderText("API Secret / Client Secret")
        set_layout.addWidget(self.inp_secret)

        save_btn = QPushButton("SAVE API KEYS")
        save_btn.clicked.connect(self._save_settings)
        set_layout.addWidget(save_btn)

        self.login_btn = QPushButton("LOGIN VIA BROWSER")
        self.login_btn.setObjectName("ActionButton")
        self.login_btn.clicked.connect(self._run_browser_login)
        set_layout.addWidget(self.login_btn)

        self.pass_btn = QPushButton("LOGIN WITH PASSWORD")
        self.pass_btn.setStyleSheet(f"background: {C['secondary']}; color: white;")
        self.pass_btn.clicked.connect(self._run_password_login)
        set_layout.addWidget(self.pass_btn)

        btn_paste = QPushButton("PASTE ACCESS TOKEN")
        btn_paste.setStyleSheet(
            f"color: {C['secondary']}; border: 1px dashed {C['secondary']};"
        )
        btn_paste.clicked.connect(self._run_paste_token)
        set_layout.addWidget(btn_paste)

        self.test_btn = QPushButton("Check Connection")
        self.test_btn.clicked.connect(self._run_test_auth)
        set_layout.addWidget(self.test_btn)

        set_layout.addStretch()
        tabs.addTab(set_tab, "Settings")

        right_layout.addWidget(tabs)
        root.addWidget(right_panel, 3)

    # ── Settings ──
    def _save_settings(self):
        self.tracker.config["api_key"] = self.inp_api.text().strip()
        self.tracker.config["api_secret"] = self.inp_secret.text().strip()
        self.tracker.save_config()
        QMessageBox.information(self, "Saved", "Settings updated.")

    def _change_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder", self.tracker.download_path)
        if path:
            self.tracker.set_download_path(path)
            self.inp_dl_path.setText(f"📁 {path}")

    # ── Scanner Actions ──
    def _start_scan(self):
        url = self.url_input.text().strip()
        if not url:
            return
        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("SCANNING...")
        self.signals.log.emit(f"[*] Scanning: {url}")
        count = self.scan_count.value()
        threading.Thread(
            target=self._scan_worker, args=(url, count), daemon=True
        ).start()

    def _scan_worker(self, url, count):
        try:
            results = self.tracker.get_latest_videos(url, count)
            self.signals.scan_done.emit(results)
        except Exception as e:
            self.signals.scan_error.emit(str(e))

    def _on_scan_done(self, results: list):
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("SCAN CHANNEL")

        # Clear old cards
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.video_widgets.clear()

        card_idx = 0
        for data in results:
            card = ScannerVideoCard(data)
            vid = data.get("id", str(card_idx))
            self.video_widgets[vid] = card
            row = card_idx // 2
            col = card_idx % 2
            self.grid_layout.addWidget(card, row, col)
            card_idx += 1

        self.signals.log.emit(f"[+] Found {len(results)} videos.")

    def _on_scan_error(self, err: str):
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("SCAN CHANNEL")
        QMessageBox.warning(self, "Scan Error", err)

    # ── Clear All ──
    def _clear_all_cards(self):
        """Remove all scanned cards from the grid."""
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.video_widgets.clear()
        self.signals.log.emit("[*] Cleared all cards.")

    # ── Cancel Downloads ──
    def _cancel_downloads(self):
        """Signal all running workers to stop + cleanup partial files."""
        self._cancel_event.set()
        self.cancel_dl_btn.setEnabled(False)
        self.cancel_dl_btn.setText("Cancelling...")
        self.signals.log.emit("[⏹] Cancel requested — cleaning up partial files...")
        # Cleanup in a background thread to avoid blocking UI
        threading.Thread(target=self._cleanup_and_signal, daemon=True).start()

    def _cleanup_and_signal(self):
        """Delete partial/temp files from tracker's download path, then signal done."""
        import time as _time
        _time.sleep(1.5)  # give workers a moment to stop
        patterns = ["*.part", "*.ytdl", "*.part-Frag*", "Frag*",
                    "*.f[0-9]*.mp4", "*.f[0-9]*.webm", "*.f[0-9]*.m4a"]
        for pattern in patterns:
            for path in glob.glob(os.path.join(self.tracker.download_path, pattern)):
                try:
                    os.remove(path)
                except Exception:
                    pass
        self.signals.all_cancelled.emit()

    def _on_all_cancelled(self):
        """Called after cancel + cleanup completes."""
        for card in self.video_widgets.values():
            if card.status_label.text() not in ("DOWNLOADED", ):
                card.set_status("⏹ CANCELLED", "error")
        self.dl_btn.setEnabled(True)
        self.cancel_dl_btn.setVisible(False)
        self.cancel_dl_btn.setEnabled(True)
        self.cancel_dl_btn.setText("⏹ CANCEL")
        self._cancel_event.clear()   # reset for next use
        self.signals.log.emit("[⏹] Download cancelled. Partial files deleted.")

    # ── Download Actions ──
    def _start_download_queue(self):
        selected = [
            w.video_data
            for w in self.video_widgets.values()
            if w.checkbox.isChecked() and w.status_label.text() not in ("DOWNLOADED", "⏹ CANCELLED")
        ]
        if not selected:
            QMessageBox.information(self, "Selection", "No videos selected!")
            return
        self._cancel_event.clear()  # fresh cancel flag
        self.dl_btn.setEnabled(False)
        self.cancel_dl_btn.setVisible(True)
        self.cancel_dl_btn.setEnabled(True)
        for data in selected:
            vid = data.get("id", "")
            if vid in self.video_widgets:
                self.video_widgets[vid].set_status("QUEUED", "normal")
            self.threadpool.start(
                ScanDownloadWorker(self.tracker, data, self.signals, self._cancel_event)
            )

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

    # ── Log ──
    def _on_log(self, text: str):
        timestamp = dt.now().strftime("%H:%M:%S")
        self.log_area.append(f"[{timestamp}] {text}")

    # ── Auth Actions ──
    def _run_browser_login(self):
        self._save_settings()
        self.signals.log.emit("[*] Opening browser for login...")
        self.threadpool.start(AuthTestWorker(self.tracker, self.signals, force_reauth=True))

    def _run_password_login(self):
        self._save_settings()
        email, ok1 = QInputDialog.getText(self, "Password Login", "Enter Dailymotion Email:")
        if not ok1 or not email:
            return
        password, ok2 = QInputDialog.getText(
            self, "Password Login", "Enter Dailymotion Password:", QLineEdit.Password
        )
        if not ok2 or not password:
            return
        self.signals.log.emit("[*] Attempting password login...")
        self.threadpool.start(AuthPasswordWorker(self.tracker, email, password, self.signals))

    def _run_test_auth(self):
        self._save_settings()
        self.threadpool.start(AuthTestWorker(self.tracker, self.signals))

    def _on_auth_result(self, success: bool, message: str):
        self.signals.log.emit(message)
        if success:
            QMessageBox.information(self, "Identity", message)
        else:
            QMessageBox.critical(self, "Auth Failed", message)

    def _run_paste_token(self):
        client_id = self.inp_api.text().strip()
        if not client_id:
            QMessageBox.warning(self, "API Key Required", "Please enter API Key first.")
            return
        url = (
            f"https://www.dailymotion.com/oauth/authorize"
            f"?response_type=token&client_id={client_id}"
            f"&redirect_uri={OAUTH_REDIRECT}&scope={OAUTH_SCOPE}"
        )
        webbrowser.open(url)
        token, ok = QInputDialog.getText(
            self, "Paste Token",
            "Login in browser, then COPY the access_token from the URL and PASTE here:",
        )
        if ok and token:
            clean = token.split("&")[0].split("=")[-1]
            self.tracker.access_token = clean
            self.tracker.config["access_token"] = clean
            self.tracker.save_config()
            self._run_test_auth()
