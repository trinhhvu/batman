"""
front/pages/analyze_page.py — Video Analytics Page (PURE UI)
=============================================================
Displays bento-style analytics cards. ALL API calls delegated to back/.
"""

import os
import re
import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QFrame, QGridLayout, QFileDialog, QApplication, QMessageBox,
    QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QPixmap, QFont, QCursor, QColor
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

from front.design import COLORS as C, FONT_HEADLINE, FONT_BODY, BORDER_RADIUS_CARD
from back.api_client import fetch_video_details, fetch_thumbnail_data


# ──────────────────────────────────────────────────────────────
# Animated Copy Button
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
# VideoCard — Bento-style analytics card
# ──────────────────────────────────────────────────────────────
class VideoCard(QFrame):
    """Renders a single video's analytics as a premium bento card."""

    send_to_download = pyqtSignal(str)

    def __init__(self, data, parent_page=None):
        super().__init__()
        self.data = data
        self.parent_page = parent_page
        self._build_ui()

    def _build_ui(self):
        self.setObjectName("VideoCard")
        self.setFixedWidth(480)
        self.setStyleSheet(f"""
            QFrame#VideoCard {{
                background-color: #1a1a2a;
                border: 1px solid {C['outline_variant']}30;
                border-radius: {BORDER_RADIUS_CARD}px;
            }}
            QFrame#VideoCard:hover {{
                background-color: #1e1e2e;
                border: 1px solid {C['primary']}50;
            }}
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Thumbnail ──
        thumb_container_wrapper = QFrame()
        thumb_container_wrapper.setFixedHeight(270)
        thumb_container_wrapper.setStyleSheet(
            f"background-color: #000; "
            f"border-top-left-radius: {BORDER_RADIUS_CARD}px; "
            f"border-top-right-radius: {BORDER_RADIUS_CARD}px;"
        )

        thumb_label = QLabel()
        thumb_label.setAlignment(Qt.AlignCenter)

        thumb_url = self.data.get('thumbnail_720_url') or self.data.get('thumbnail_480_url') or self.data.get('thumbnail', '')
        if thumb_url:
            try:
                img_data = fetch_thumbnail_data(thumb_url)
                pixmap = QPixmap()
                pixmap.loadFromData(img_data)
                pixmap = pixmap.scaled(480, 270, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                thumb_label.setPixmap(pixmap)
            except Exception:
                thumb_label.setText("")

        thumb_label.setParent(thumb_container_wrapper)
        thumb_label.setGeometry(0, 0, 480, 270)

        # Download overlay
        dl_overlay = QPushButton("⬇")
        dl_overlay.setFixedSize(36, 36)
        dl_overlay.setCursor(QCursor(Qt.PointingHandCursor))
        dl_overlay.setToolTip("Send to Download queue")
        dl_overlay.setStyleSheet(f"""
            QPushButton {{
                background-color: {C['primary']};
                color: {C['on_primary']};
                border: none;
                border-radius: 18px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {C['primary_dim']};
            }}
        """)
        video_url = self.data.get('url', '')
        dl_overlay.clicked.connect(lambda: self.send_to_download.emit(video_url))
        dl_overlay.setParent(thumb_container_wrapper)
        dl_overlay.move(480 - 46, 10)

        # ── Body ──
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 20, 20, 20)
        body_layout.setSpacing(15)

        # Title + Copy
        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        title_str = (self.data.get('title') or 'N/A').upper()
        title_label = QLabel(title_str)
        title_label.setWordWrap(True)
        title_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        title_label.setStyleSheet(
            f"color: {C['on_surface']}; font-size: 15px; font-weight: 800; "
            f"font-family: '{FONT_HEADLINE}';"
        )
        copy_title_btn = CopyButton(title_str, "TITLE")
        copy_title_btn.setFixedWidth(80)
        title_row.addWidget(title_label, 1)
        title_row.addWidget(copy_title_btn, 0)

        # Channel info
        channel_name = self.data.get('channel') or self.data.get('uploader') or 'N/A'
        owner_name = self.data.get('owner') or self.data.get('uploader_id') or 'N/A'
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

        # Stats grid
        stats_frame = QFrame()
        stats_frame.setStyleSheet("padding: 5px 0px;")
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 5, 0, 5)
        stats_layout.setSpacing(8)
        v_24h = int(self.data.get('views_last_day') or 0)
        v_1h = int(self.data.get('views_last_hour') or 0)
        v_total = max(int(self.data.get('views_total') or self.data.get('view_count') or 0), v_24h, v_1h)
        stats_layout.addWidget(self._stat_box("Total", f"{v_total:,}", C['on_surface']))
        stats_layout.addWidget(self._stat_box("24h", f"{v_24h:,}", C['secondary']))
        stats_layout.addWidget(self._stat_box("1h", f"{v_1h:,}", C['primary']))

        # Geoblock
        geoblock = str(self.data.get('geoblocking') or 'allow')
        geo_frame = QFrame()
        if "deny" in geoblock:
            geo_frame.setStyleSheet(f"background-color: {C['error']}15; border-radius: 8px;")
            geo_layout = QVBoxLayout(geo_frame)
            geo_status = QLabel("STATUS: DENY")
            geo_status.setStyleSheet(f"color: {C['error']}; font-size: 11px; font-weight: bold;")
            geo_desc = QLabel("Geoblocking active.")
            geo_desc.setStyleSheet(f"color: {C['on_surface_variant']}; font-size: 10px;")
            geo_layout.addWidget(geo_status)
            geo_layout.addWidget(geo_desc)
        else:
            geo_frame.setStyleSheet(
                f"background-color: {C['secondary']}25; border-radius: 8px; "
                f"border: 1px solid {C['secondary']}40;"
            )
            geo_layout = QVBoxLayout(geo_frame)
            geo_status = QLabel("STATUS: NO GEOBLOCK")
            geo_status.setStyleSheet(
                f"color: {C['secondary']}; font-size: 11px; font-weight: bold; "
                f"background: transparent; border: none;"
            )
            geo_desc = QLabel("Signal clear. Content is available globally.")
            geo_desc.setStyleSheet(
                f"color: {C['on_surface']}; font-size: 10px; "
                f"background: transparent; border: none;"
            )
            geo_layout.addWidget(geo_status)
            geo_layout.addWidget(geo_desc)

        # Footer
        footer = QVBoxLayout()
        footer.setSpacing(8)
        updated_time = self._format_time(self.data.get('updated_time') or 0)
        if updated_time:
            time_label = QLabel(f"Updated: {updated_time}")
            time_label.setStyleSheet(f"color: {C['on_surface_variant']}; font-size: 11px;")
            footer.addWidget(time_label)
        url_value = video_url or '#'
        url_row = QHBoxLayout()
        url_row.setSpacing(6)
        url_label = QLabel(f"URL: <a href='{url_value}' style='color: {C['primary']}; text-decoration: none;'>{url_value}</a>")
        url_label.setStyleSheet(f"color: {C['on_surface_variant']}; font-size: 11px;")
        url_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
        url_label.setOpenExternalLinks(True)
        url_label.setWordWrap(True)
        url_row.addWidget(url_label, 1)
        url_copy = CopyButton(url_value, "URL")
        url_copy.setFixedWidth(72)
        url_row.addWidget(url_copy)
        footer.addLayout(url_row)

        thumb_value = thumb_url or '#'
        thumb_row = QHBoxLayout()
        thumb_row.setSpacing(6)
        thumb_link = QLabel(f"Thumb: <a href='{thumb_value}' style='color: {C['primary']}; text-decoration: none;'>{thumb_value[:60]}...</a>")
        thumb_link.setStyleSheet(f"color: {C['on_surface_variant']}; font-size: 11px;")
        thumb_link.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
        thumb_link.setOpenExternalLinks(True)
        thumb_link.setWordWrap(True)
        thumb_row.addWidget(thumb_link, 1)
        thumb_copy = CopyButton(thumb_value, "THUMB")
        thumb_copy.setFixedWidth(80)
        thumb_row.addWidget(thumb_copy)
        footer.addLayout(thumb_row)

        body_layout.addLayout(title_box)
        body_layout.addWidget(stats_frame)
        body_layout.addWidget(geo_frame)
        body_layout.addLayout(footer)

        main_layout.addWidget(thumb_container_wrapper)
        main_layout.addWidget(body)

    def _stat_box(self, label, value, color):
        box = QFrame()
        box.setStyleSheet(f"""
            QFrame {{
                background-color: {C['surface_container_highest']}80;
                border: 1px solid {C['outline_variant']}40;
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

    def _format_time(self, ts):
        try:
            return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return ""


# ──────────────────────────────────────────────────────────────
# Analyze Page
# ──────────────────────────────────────────────────────────────
class AnalyzePage(QWidget):
    """Scan videos → Display bento cards. Logic delegated to back/api_client."""

    request_download = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.video_data_list = []
        self.card_count = 0
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)

        header = QLabel("Real-time Intelligence")
        header.setFont(QFont(FONT_HEADLINE, 22, QFont.ExtraBold))
        header.setStyleSheet(f"color: {C['on_surface']};")
        layout.addWidget(header)

        sub = QLabel("Scan Dailymotion videos. Analyze views, geoblock status, and metadata.")
        sub.setStyleSheet(f"color: {C['on_surface_variant']}; font-size: 13px;")
        layout.addWidget(sub)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL or Video ID...")
        self.url_input.setFixedWidth(400)
        self.url_input.returnPressed.connect(self._scan_one)
        toolbar.addWidget(self.url_input)

        scan_btn = QPushButton("SCAN VIDEO")
        scan_btn.setObjectName("ActionButton")
        scan_btn.setCursor(QCursor(Qt.PointingHandCursor))
        scan_btn.setFixedWidth(130)
        scan_btn.clicked.connect(self._scan_one)
        toolbar.addWidget(scan_btn)

        batch_btn = QPushButton("IMPORT BATCH")
        batch_btn.clicked.connect(self._scan_bulk)
        toolbar.addWidget(batch_btn)

        clear_btn = QPushButton("CLEAR ALL")
        clear_btn.setObjectName("DangerButton")
        clear_btn.setCursor(QCursor(Qt.PointingHandCursor))
        clear_btn.clicked.connect(self._clear_all)
        toolbar.addWidget(clear_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

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

    def _scan_one(self):
        url = self.url_input.text().strip()
        if url:
            vid_id = self._extract_id(url)
            self._fetch_and_display(vid_id)
        self.url_input.clear()

    def _scan_bulk(self):
        import re as _re
        path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "Text (*.txt);;HTML (*.html)")
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                ids = _re.findall(r'/video/([a-zA-Z0-9]+)', content)
                if not ids:
                    ids = content.splitlines()
                for vid in set(ids):
                    if len(vid) > 3:
                        self._fetch_and_display(vid)
            except Exception:
                pass

    def _clear_all(self):
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.video_data_list.clear()
        self.card_count = 0

    def _extract_id(self, url):
        match = re.search(r'/video/([a-zA-Z0-9]+)', url)
        return match.group(1) if match else url.strip().split('/')[-1]

    def _fetch_and_display(self, vid_id):
        """Fetch video details from backend API client and display."""
        try:
            data = fetch_video_details(vid_id.strip())
            self.video_data_list.append(data)
            card = VideoCard(data, self)
            card.send_to_download.connect(self.request_download.emit)
            row = self.card_count // 2
            col = self.card_count % 2
            self.grid_layout.addWidget(card, row, col)
            self.card_count += 1
        except ValueError as e:
            err_msg = str(e)
            if '404' in err_msg or 'error' in err_msg.lower():
                QMessageBox.warning(self, "Video Unavailable",
                    f"Video '{vid_id}' không tồn tại hoặc đã bị xóa.")
            else:
                QMessageBox.warning(self, "Error",
                    f"Không thể lấy thông tin video '{vid_id}'.\n{err_msg}")
        except Exception as e:
            QMessageBox.warning(self, "Error",
                f"Lỗi khi phân tích video '{vid_id}':\n{str(e)[:200]}")
