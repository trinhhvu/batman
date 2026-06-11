
import os
import re
import datetime
import webbrowser

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QFrame, QGridLayout, QFileDialog, QApplication, QMessageBox,
    QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QPixmap, QFont, QCursor, QColor
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

from front.design import COLORS as C, FONT_HEADLINE, FONT_BODY, BORDER_RADIUS_CARD, action_btn_style, danger_btn_style, get_main_window_qss
from front.widgets.notification import show_notification
from back.api_client import fetch_video_details, fetch_thumbnail_data


class CopyButton(QPushButton):


    def __init__(self, text_to_copy: str, label: str = "COPY", parent=None):
        super().__init__(parent)
        self._text_to_copy = text_to_copy
        self._default_label = label
        self.setText(label)
        self.setFixedHeight(28)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet(self._default_qss())
        self.clicked.connect(self._do_copy)

    def _default_qss(self):
        return f"""
            QPushButton {{
                background-color: {C['surface_container_high']};
                color: {C['on_surface']};
                border: 1px solid {C['outline_variant']};
                border-radius: 8px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 600;
                font-family: {FONT_BODY};
            }}
            QPushButton:hover {{
                background-color: {C['surface_container_highest']};
            }}
        """

    def _success_qss(self):
        return f"""
            QPushButton {{
                background-color: {C['primary']}20;
                color: {C['primary']};
                border: 1px solid {C['primary']};
                border-radius: 8px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 700;
            }}
        """

    def _do_copy(self):
        QApplication.clipboard().setText(self._text_to_copy)
        self.setText("COPIED")
        self.setStyleSheet(self._success_qss())
        show_notification(self.window(), "COPIED", f"{self._default_label} copied to clipboard")
        QTimer.singleShot(1500, self._reset)

    def _reset(self):
        self.setText(self._default_label)
        self.setStyleSheet(self._default_qss())


class VideoCard(QFrame):


    send_to_download = pyqtSignal(str)

    def __init__(self, data, parent_page=None):
        super().__init__()
        self.data = data
        self.parent_page = parent_page
        self._build_ui()

    def _build_ui(self):
        self.setObjectName("VideoCard")
        self.setFixedWidth(460)
        # Style is now handled globally in design.py

        # Fluidic shadow
        # shadow = QGraphicsDropShadowEffect(self)
        # shadow.setBlurRadius(30)
        # shadow.setColor(QColor(0, 0, 0, 20))
        # shadow.setOffset(0, 10)
        # self.setGraphicsEffect(shadow)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Thumbnail ──
        thumb_container = QFrame()
        thumb_container.setObjectName("CardThumb")
        thumb_container.setFixedHeight(260)
        
        thumb_label = QLabel(thumb_container)
        thumb_label.setGeometry(0, 0, 460, 260)
        thumb_label.setAlignment(Qt.AlignCenter)
        
        thumb_url = self.data.get('thumbnail_720_url') or self.data.get('thumbnail', '')
        if thumb_url:
            try:
                img_data = fetch_thumbnail_data(thumb_url)
                pixmap = QPixmap()
                pixmap.loadFromData(img_data)
                pixmap = pixmap.scaled(460, 260, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                thumb_label.setPixmap(pixmap)
            except: pass

        dl_btn = QPushButton("GET", thumb_container)
        dl_btn.setObjectName("ActionButton")
        dl_btn.setFixedSize(56, 32)
        dl_btn.setCursor(Qt.PointingHandCursor)
        dl_btn.move(460 - 72, 12)
        def _on_get():
            url = self.data.get('url', '')
            if url:
                self.send_to_download.emit(url)
        dl_btn.clicked.connect(_on_get)

        # ── Content Body ──
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(24, 24, 24, 24)
        body_layout.setSpacing(16)

        # Title
        title_row = QHBoxLayout()
        title_str = (self.data.get('title') or 'N/A').upper()
        title_label = QLabel(title_str)
        title_label.setWordWrap(True)
        title_label.setFont(QFont(FONT_HEADLINE, 11, QFont.Bold))
        # Color handled globally
        title_row.addWidget(title_label, 1)
        
        copy_title = CopyButton(title_str, "TITLE")
        title_row.addWidget(copy_title)
        body_layout.addLayout(title_row)

        # Channel
        channel = QLabel(f"<span style='color: {C['primary']}; font-weight: 700;'>{self.data.get('channel', 'N/A')}</span> • {self.data.get('id', 'N/A')}")
        body_layout.addWidget(channel)

        # Publish Date
        created_ts = self.data.get('created_time')
        if created_ts:
            try:
                pub_date = datetime.datetime.fromtimestamp(int(created_ts)).strftime('%Y-%m-%d %H:%M')
            except Exception:
                pub_date = 'N/A'
        else:
            pub_date = 'N/A'
        date_label = QLabel(f"📅 Published: {pub_date}")
        date_label.setStyleSheet(f"color: {C['on_surface_variant']}; font-size: 12px;")
        body_layout.addWidget(date_label)

        # Stats Grid
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(10)
        
        v_24h = int(self.data.get('views_last_day') or 0)
        v_1h = int(self.data.get('views_last_hour') or 0)
        v_total = int(self.data.get('views_total') or self.data.get('view_count') or 0)
        
        stats_layout.addWidget(self._stat_box("TOTAL", f"{v_total:,}"))
        stats_layout.addWidget(self._stat_box("24H", f"{v_24h:,}"))
        stats_layout.addWidget(self._stat_box("1H", f"{v_1h:,}"))
        body_layout.addLayout(stats_layout)

        # Geoblock Banner
        geo = str(self.data.get('geoblocking') or 'allow')
        geo_banner = QLabel()
        geo_banner.setObjectName("GeoBanner")
        geo_banner.setContentsMargins(12, 6, 12, 6)
        geo_banner.setAlignment(Qt.AlignCenter)
        if "deny" in geo:
            geo_banner.setText("GEOBLOCK ACTIVE")
            geo_banner.setProperty("state", "error")
        else:
            geo_banner.setText("CLEAN / NO GEOBLOCK")
            geo_banner.setProperty("state", "success")
        body_layout.addWidget(geo_banner)

        # Footer Actions
        actions = QHBoxLayout()
        actions.setSpacing(12)
        
        video_url = self.data.get('url', '')
        btn_url = QPushButton("URL")
        btn_url.setCursor(Qt.PointingHandCursor)
        def _copy_url():
            QApplication.clipboard().setText(video_url)
            show_notification(self.window(), "COPIED", "Video URL copied to clipboard")
            if video_url:
                webbrowser.open(video_url)
        btn_url.clicked.connect(_copy_url)
        
        btn_thumb = QPushButton("IMAGE")
        btn_thumb.setCursor(Qt.PointingHandCursor)
        def _copy_thumb():
            QApplication.clipboard().setText(thumb_url)
            show_notification(self.window(), "COPIED", "Thumbnail URL copied to clipboard")
            if thumb_url:
                webbrowser.open(thumb_url)
        btn_thumb.clicked.connect(_copy_thumb)
        
        actions.addWidget(btn_url, 1)
        actions.addWidget(btn_thumb, 1)
        body_layout.addLayout(actions)

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


class AnalyzePage(QWidget):


    request_download = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AnalyzePage")
        self.card_count = 0
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(32)

        # Header
        header_box = QVBoxLayout()
        self.title = QLabel("Real-time Intelligence")
        self.title.setObjectName("PageTitle")
        header_box.addWidget(self.title)
        
        self.subtitle = QLabel("Scan Dailymotion videos. Analyze views, geoblock status, and performance.")
        self.subtitle.setObjectName("SubtitleLabel")
        header_box.addWidget(self.subtitle)
        layout.addLayout(header_box)

        # Toolbar
        self.toolbar = QFrame()
        self.toolbar.setObjectName("BentoCard")
        tool_layout = QHBoxLayout(self.toolbar)
        tool_layout.setContentsMargins(20, 10, 20, 10)
        tool_layout.setSpacing(12)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Video URL or ID")
        self.url_input.setMinimumHeight(44)
        self.url_input.returnPressed.connect(self._scan_one)
        tool_layout.addWidget(self.url_input, 1)
        
        scan_btn = QPushButton("SCAN")
        scan_btn.setObjectName("ActionButton")
        scan_btn.setFixedSize(120, 44)
        scan_btn.setCursor(Qt.PointingHandCursor)
        scan_btn.clicked.connect(self._scan_one)
        tool_layout.addWidget(scan_btn)
        
        clear_btn = QPushButton("CLEAR")
        clear_btn.setFixedSize(100, 44)
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.clicked.connect(self._clear_all)
        tool_layout.addWidget(clear_btn)
        layout.addWidget(self.toolbar)

        # Results Grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(24)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        scroll.setWidget(self.grid_widget)
        layout.addWidget(scroll, 1)

    def _scan_one(self):
        url = self.url_input.text().strip()
        if url:
            vid_id = url.split('/')[-1] if 'dailymotion.com' in url else url
            self._fetch_and_display(vid_id)
            self.url_input.clear()

    def _clear_all(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self.card_count = 0

    def _fetch_and_display(self, vid_id):
        try:
            data = fetch_video_details(vid_id.strip())
            card = VideoCard(data, self)
            card.send_to_download.connect(self.request_download.emit)
            row = self.card_count // 2
            col = self.card_count % 2
            self.grid_layout.addWidget(card, row, col)
            self.card_count += 1
        except Exception as e:
            QMessageBox.warning(self, "Scan Error", str(e))

    def refresh_theme(self):
        """No manual refresh needed for standard labels anymore."""
        pass
