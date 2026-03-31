"""
analytics_page.py — Analytics Page (migrated from Batman v1)
=============================================================
Provides video analytics: scan Dailymotion videos for view stats,
geoblock status, thumbnails. Display results as bento-grid cards.

Migrated from APP MACOS/main.py (standalone PyQt5 app) into this
unified page widget.

Dependencies: PyQt5, requests, pandas, openpyxl, design.py
Used by: app.py (loaded into QStackedWidget)
"""

import os
import re
import datetime

import requests
import pandas as pd

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QFrame, QGridLayout, QFileDialog, QApplication
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer

from design import COLORS as C, FONT_HEADLINE, FONT_BODY, BORDER_RADIUS_CARD


# ──────────────────────────────────────────────────────────────
# VideoCard — Bento-style analytics card for a single video
# ──────────────────────────────────────────────────────────────
class VideoCard(QFrame):
    """Renders a single video's analytics as a premium bento card."""

    def __init__(self, data, parent_page):
        super().__init__()
        self.data = data
        self.parent_page = parent_page
        self._build_ui()

    def copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.copy_btn.setText("DONE!")
        QTimer.singleShot(1500, lambda: self.copy_btn.setText("Copy"))

    def _build_ui(self):
        self.setObjectName("VideoCard")
        self.setFixedWidth(480)
        self.setStyleSheet(f"""
            QFrame#VideoCard {{
                background-color: #1a1a2a;
                border: 2px solid {C['outline_variant']}30;
                border-radius: {BORDER_RADIUS_CARD}px;
            }}
            QFrame#VideoCard:hover {{
                background-color: #1e1e2e;
            }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Thumbnail ──
        thumb_container = QFrame()
        thumb_container.setFixedHeight(270)
        thumb_container.setStyleSheet(f"background-color: #000; border-top-left-radius: {BORDER_RADIUS_CARD}px; border-top-right-radius: {BORDER_RADIUS_CARD}px;")
        thumb_layout = QVBoxLayout(thumb_container)
        thumb_layout.setContentsMargins(0, 0, 0, 0)

        thumb_label = QLabel()
        thumb_label.setAlignment(Qt.AlignCenter)

        thumb_url = self.data.get('thumbnail_720_url') or self.data.get('thumbnail_480_url')
        if thumb_url:
            try:
                img_data = requests.get(thumb_url, timeout=5).content
                pixmap = QPixmap()
                pixmap.loadFromData(img_data)
                pixmap = pixmap.scaled(480, 270, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                thumb_label.setPixmap(pixmap)
            except:
                thumb_label.setText("")

        thumb_layout.addWidget(thumb_label)

        # ── Body ──
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 20, 20, 20)
        body_layout.setSpacing(15)

        # Title + Copy button
        title_row = QHBoxLayout()
        title_row.setSpacing(10)

        title_str = (self.data.get('title') or 'N/A').upper()
        title_label = QLabel(title_str)
        title_label.setWordWrap(True)
        title_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        title_label.setStyleSheet(f"color: {C['on_surface']}; font-size: 15px; font-weight: 800; font-family: '{FONT_HEADLINE}';")

        self.copy_btn = QPushButton("Copy")
        self.copy_btn.setFixedWidth(50)
        self.copy_btn.setFlat(True)
        self.copy_btn.setCursor(Qt.PointingHandCursor)
        self.copy_btn.setStyleSheet(f"""
            QPushButton {{
                color: {C['primary']};
                font-size: 11px;
                font-weight: 600;
                border: none;
                background: transparent;
            }}
            QPushButton:hover {{ color: {C['primary_dim']}; }}
        """)
        self.copy_btn.clicked.connect(lambda: self.copy_to_clipboard(title_str))

        title_row.addWidget(title_label, 1)
        title_row.addWidget(self.copy_btn, 0)

        # Channel info
        identity = QLabel(
            f"<span style='color: {C['primary']}; font-weight: bold;'>{self.data.get('channel') or 'N/A'}</span>"
            f" <span style='color: {C['outline_variant']};'>•</span> "
            f"<span style='color: {C['on_surface']};'>{self.data.get('owner') or 'N/A'}</span>"
        )
        identity.setStyleSheet("font-size: 12px;")
        identity.setTextInteractionFlags(Qt.TextSelectableByMouse)

        title_box = QVBoxLayout()
        title_box.setSpacing(5)
        title_box.addLayout(title_row)
        title_box.addWidget(identity)

        # ── Stats grid (3 boxes) ──
        stats_frame = QFrame()
        stats_frame.setStyleSheet("padding: 5px 0px;")
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 5, 0, 5)
        stats_layout.setSpacing(8)

        v_24h = int(self.data.get('views_last_day') or 0)
        v_1h = int(self.data.get('views_last_hour') or 0)
        v_total = max(int(self.data.get('views_total') or 0), v_24h, v_1h)

        stats_layout.addWidget(self._stat_box("Total", f"{v_total:,}", C['on_surface']))
        stats_layout.addWidget(self._stat_box("24h", f"{v_24h:,}", C['secondary']))
        stats_layout.addWidget(self._stat_box("1h", f"{v_1h:,}", C['primary']))

        # ── Geoblock status ──
        geoblock = str(self.data.get('geoblocking') or 'allow')
        geo_frame = QFrame()
        if "deny" in geoblock:
            geo_frame.setStyleSheet(f"background-color: {C['error']}15; border-radius: 8px;")
            geo_layout = QVBoxLayout(geo_frame)
            geo_status = QLabel(f"STATUS: DENY")
            geo_status.setStyleSheet(f"color: {C['error']}; font-size: 11px; font-weight: bold;")
            geo_desc = QLabel("Geoblocking active.")
            geo_desc.setStyleSheet(f"color: {C['on_surface_variant']}; font-size: 10px;")
            geo_layout.addWidget(geo_status)
            geo_layout.addWidget(geo_desc)
        else:
            geo_frame.setStyleSheet(f"background-color: {C['secondary']}25; border-radius: 8px; border: 1px solid {C['secondary']}40;")
            geo_layout = QVBoxLayout(geo_frame)
            geo_status = QLabel("STATUS: NO GEOBLOCK")
            geo_status.setStyleSheet(f"color: {C['secondary']}; font-size: 11px; font-weight: bold; background: transparent; border: none;")
            geo_desc = QLabel("Signal clear. Content is available globally.")
            geo_desc.setStyleSheet(f"color: {C['on_surface']}; font-size: 10px; background: transparent; border: none;")
            geo_layout.addWidget(geo_status)
            geo_layout.addWidget(geo_desc)

        # ── Footer links ──
        footer = QVBoxLayout()
        footer.setSpacing(4)

        updated_time = self._format_time(self.data.get('updated_time') or 0)
        for label, value in [("Updated", updated_time), ("URL", self.data.get('url', '#')), ("Thumb", thumb_url or '#')]:
            line = QLabel(f"{label}: <a href='{value}' style='color: {C['primary']}; text-decoration: none;'>{value}</a>" if label != "Updated" else f"{label}: {value}")
            line.setStyleSheet(f"color: {C['on_surface_variant']}; font-size: 11px;")
            line.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
            line.setOpenExternalLinks(True)
            footer.addWidget(line)

        body_layout.addLayout(title_box)
        body_layout.addWidget(stats_frame)
        body_layout.addWidget(geo_frame)
        body_layout.addLayout(footer)

        main_layout.addWidget(thumb_container)
        main_layout.addWidget(body)

    def _stat_box(self, label, value, color):
        """Creates a single stat box widget."""
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
        cap.setStyleSheet(f"color: {C['on_surface_variant']}; font-size: 9px; font-weight: bold; letter-spacing: 1px; background: transparent; border: none;")
        val = QLabel(value)
        val.setStyleSheet(f"color: {color}; font-size: 17px; font-weight: 800; font-family: '{FONT_HEADLINE}'; background: transparent; border: none;")
        val.setTextInteractionFlags(Qt.TextSelectableByMouse)

        layout.addWidget(cap)
        layout.addWidget(val)
        return box

    def _format_time(self, ts):
        try:
            return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        except:
            return ""


# ──────────────────────────────────────────────────────────────
# Analytics Page (main widget)
# ──────────────────────────────────────────────────────────────
class AnalyticsPage(QWidget):
    """
    Full analytics page: Scan videos → Display bento cards → Export to Excel.
    Migrated from APP MACOS/main.py (Batman v1).
    """

    API_ENDPOINT = "https://api.dailymotion.com/video/{video_id}?fields=thumbnail_480_url,thumbnail_720_url,owner,channel,title,views_total,views_last_day,views_last_hour,updated_time,url,geoblocking"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.video_data_list = []
        self.save_directory = os.path.join(os.path.expanduser("~"), "Downloads")
        self.card_count = 0
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)

        # ── Header ──
        header = QLabel("Real-time Intelligence")
        header.setFont(QFont(FONT_HEADLINE, 22, QFont.ExtraBold))
        header.setStyleSheet(f"color: {C['on_surface']};")
        layout.addWidget(header)

        sub = QLabel("Scan Dailymotion videos. Analyze views, geoblock status, and metadata.")
        sub.setStyleSheet(f"color: {C['on_surface_variant']}; font-size: 13px;")
        layout.addWidget(sub)

        # ── Toolbar ──
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL or Video ID...")
        self.url_input.setFixedWidth(400)
        self.url_input.returnPressed.connect(self._scan_one)
        toolbar.addWidget(self.url_input)

        scan_btn = QPushButton("SCAN VIDEO")
        scan_btn.setObjectName("ActionButton")
        scan_btn.setCursor(Qt.PointingHandCursor)
        scan_btn.setFixedWidth(130)
        scan_btn.clicked.connect(self._scan_one)
        toolbar.addWidget(scan_btn)

        batch_btn = QPushButton("IMPORT BATCH")
        batch_btn.clicked.connect(self._scan_bulk)
        toolbar.addWidget(batch_btn)

        export_btn = QPushButton("EXPORT EXCEL")
        export_btn.clicked.connect(self._export_excel)
        toolbar.addWidget(export_btn)

        dir_btn = QPushButton("DIR")
        dir_btn.clicked.connect(self._change_folder)
        toolbar.addWidget(dir_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # ── Card grid (scrollable) ──
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
        layout.addWidget(scroll, 1)

    # ── Actions ──

    def _scan_one(self):
        url = self.url_input.text().strip()
        if url:
            vid_id = self._extract_id(url)
            self._fetch_and_display(vid_id)
        self.url_input.clear()

    def _scan_bulk(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "Text (*.txt);;HTML (*.html)")
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                ids = re.findall(r'/video/([a-zA-Z0-9]+)', content)
                if not ids:
                    ids = content.splitlines()
                for vid in set(ids):
                    if len(vid) > 3:
                        self._fetch_and_display(vid)
            except:
                pass

    def _export_excel(self):
        if not self.video_data_list:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save", "report.xlsx", "Excel (*.xlsx)")
        if path:
            pd.DataFrame(self.video_data_list).to_excel(path, index=False)

    def _change_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder", self.save_directory)
        if path:
            self.save_directory = path

    def _extract_id(self, url):
        match = re.search(r'/video/([a-zA-Z0-9]+)', url)
        return match.group(1) if match else url.strip().split('/')[-1]

    def _fetch_and_display(self, vid_id):
        url = self.API_ENDPOINT.format(video_id=vid_id.strip())
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()

                # Sync total views with daily/hourly (API lag fix)
                v_total = int(data.get('views_total') or 0)
                v_day = int(data.get('views_last_day') or 0)
                v_hour = int(data.get('views_last_hour') or 0)
                data['views_total'] = max(v_total, v_day, v_hour)

                self.video_data_list.append(data)
                card = VideoCard(data, self)
                row = self.card_count // 2
                col = self.card_count % 2
                self.grid_layout.addWidget(card, row, col)
                self.card_count += 1
        except:
            pass
