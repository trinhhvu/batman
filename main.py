import sys
import re
import datetime
import requests
import pandas as pd
import os
from bs4 import BeautifulSoup

from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, 
                             QFileDialog, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QScrollArea, QFrame, QMessageBox, QSpacerItem, QSizePolicy)
from PyQt5.QtGui import QPixmap, QIcon, QFont, QColor
from PyQt5.QtCore import Qt, QSize

class VideoCard(QFrame):
    def __init__(self, data, parent_app):
        super().__init__()
        self.data = data
        self.parent_app = parent_app
        self.initUI()

    def initUI(self):
        self.setObjectName("VideoCard")
        self.setFixedWidth(480)
        self.setStyleSheet("""
            QFrame#VideoCard {
                background-color: #1e1e2e;
                border: 1px solid #313244;
                border-radius: 12px;
            }
            QFrame#VideoCard:hover {
                border: 1px solid #89b4fa;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.thumb_container = QFrame()
        self.thumb_container.setFixedHeight(270)
        self.thumb_container.setStyleSheet("background-color: #000000; border-top-left-radius: 12px; border-top-right-radius: 12px; border-bottom: 1px solid #313244;")
        thumb_layout = QVBoxLayout(self.thumb_container)
        thumb_layout.setContentsMargins(0,0,0,0)

        self.thumbnail_label = QLabel()
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        
        thumb_url = self.data.get('thumbnail_720_url') or self.data.get('thumbnail_480_url')
        if thumb_url:
            try:
                img_data = requests.get(thumb_url, timeout=5).content
                pixmap = QPixmap()
                pixmap.loadFromData(img_data)
                pixmap = pixmap.scaled(480, 270, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                self.thumbnail_label.setPixmap(pixmap)
            except:
                self.thumbnail_label.setText("")
        
        badge = QLabel("LIVE ANALYTICS", self.thumb_container)
        badge.setStyleSheet("background-color: rgba(0, 0, 0, 150); color: #ffffff; font-weight: bold; font-size: 10px; padding: 4px 10px; border-radius: 4px;")
        badge.move(360, 230)
        thumb_layout.addWidget(self.thumbnail_label)

        body_widget = QWidget()
        body_layout = QVBoxLayout(body_widget)
        body_layout.setContentsMargins(20, 20, 20, 20)
        body_layout.setSpacing(15)

        title_box = QVBoxLayout()
        title_box.setSpacing(5)
        
        title_str = (self.data.get('title') or 'N/A').upper()
        title_label = QLabel(title_str)
        title_label.setWordWrap(True)
        title_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        title_label.setStyleSheet("color: #e3e0f7; font-size: 16px; font-weight: 800; line-height: 1.2;")
        
        identity_label = QLabel(f"<span style='color: #89b4fa; font-weight: bold;'>{self.data.get('channel') or 'N/A'}</span> <span style='color: #45475a;'>•</span> <span style='color: #cdd6f4;'>{self.data.get('owner') or 'N/A'}</span>")
        identity_label.setStyleSheet("font-size: 12px;")
        identity_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        title_box.addWidget(title_label)
        title_box.addWidget(identity_label)

        stats_frame = QFrame()
        stats_frame.setStyleSheet("border-top: 1px solid #313244; border-bottom: 1px solid #313244; padding: 10px 0px;")
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 10, 0, 10)
        stats_layout.setSpacing(0)

        def create_stat_item(label, value, color="#a6e3a1", has_border=True):
            item = QFrame()
            if has_border:
                item.setStyleSheet("border-left: 1px solid #313244; padding-left: 15px;")
            else:
                item.setStyleSheet("padding-left: 0px;")
            l = QVBoxLayout(item)
            l.setContentsMargins(0,0,0,0)
            l.setSpacing(2)
            cap = QLabel(label.upper())
            cap.setStyleSheet("color: #8d919b; font-size: 9px; font-weight: bold;")
            val = QLabel(str(value))
            val.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: 800; font-family: 'Manrope', sans-serif;")
            val.setTextInteractionFlags(Qt.TextSelectableByMouse)
            l.addWidget(cap)
            l.addWidget(val)
            return item

        v_total = int(self.data.get('views_total') or 0)
        v_24h = int(self.data.get('views_last_day') or 0)
        v_1h = int(self.data.get('views_last_hour') or 0)

        stats_layout.addWidget(create_stat_item("Total Views", f"{v_total:,}", "#99d595", False))
        stats_layout.addWidget(create_stat_item("Last Day", f"{v_24h:,}", "#89b4fa"))
        stats_layout.addWidget(create_stat_item("Last Hour", f"{v_1h:,}", "#b5cfff"))

        geoblock = str(self.data.get('geoblocking') or 'allow')
        security_box = QFrame()
        if "deny" in geoblock:
            security_box.setStyleSheet("background-color: rgba(243, 139, 168, 25); border: 1px solid rgba(243, 139, 168, 50); border-radius: 8px;")
            sec_layout = QVBoxLayout(security_box)
            sec_status = QLabel(f"STATUS: DENY ({geoblock.split(',')[-1] if ',' in geoblock else geoblock})")
            sec_status.setStyleSheet("color: #f38ba8; font-size: 11px; font-weight: bold; text-transform: uppercase;")
            sec_desc = QLabel("Geoblocking active for restricted territories.")
            sec_desc.setStyleSheet("color: #a6adc8; font-size: 10px;")
            sec_layout.addWidget(sec_status)
            sec_layout.addWidget(sec_desc)
        else:
            security_box.setStyleSheet("background-color: rgba(166, 227, 161, 20); border: 1px solid rgba(166, 227, 161, 40); border-radius: 8px;")
            sec_layout = QVBoxLayout(security_box)
            sec_status = QLabel("STATUS: NO GEOBLOCK")
            sec_status.setStyleSheet("color: #a6e3a1; font-size: 11px; font-weight: bold;")
            sec_desc = QLabel("Signal clear. Content is available globally.")
            sec_desc.setStyleSheet("color: #a6adc8; font-size: 10px;")
            sec_layout.addWidget(sec_status)
            sec_layout.addWidget(sec_desc)

        footer_box = QVBoxLayout()
        footer_box.setSpacing(8)
        
        time_row = QHBoxLayout()
        time_txt = QLabel(f"Updated: {self.parent_app.format_updated_time(self.data.get('updated_time') or 0)}")
        time_txt.setStyleSheet("color: #8d919b; font-size: 10px;")
        time_txt.setTextInteractionFlags(Qt.TextSelectableByMouse)
        time_row.addWidget(time_txt)
        time_row.addStretch()

        def create_link_row(label, url):
            row = QHBoxLayout()
            txt = QLabel(f"{label}: <a href='{url}' style='color: #89b4fa; text-decoration: none;'>{url}</a>")
            txt.setStyleSheet("color: #8d919b; font-size: 10px;")
            txt.setOpenExternalLinks(True)
            txt.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
            row.addWidget(txt)
            return row

        footer_box.addLayout(time_row)
        footer_box.addLayout(create_link_row("URL", self.data.get('url') or '#'))
        footer_box.addLayout(create_link_row("Thumb", thumb_url or '#'))

        body_layout.addLayout(title_box)
        body_layout.addWidget(stats_frame)
        body_layout.addWidget(security_box)
        body_layout.addLayout(footer_box)

        main_layout.addWidget(self.thumb_container)
        main_layout.addWidget(body_widget)

class DailymotionVideoInfoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.api_endpoint = "https://api.dailymotion.com/video/{video_id}?fields=thumbnail_480_url,thumbnail_720_url,owner,channel,title,views_total,views_last_day,views_last_hour,updated_time,url,geoblocking"
        self.video_data_list = []
        self.save_directory = os.path.join(os.path.expanduser("~"), "Downloads")
        self.card_count = 0
        self.initUI()

    def initUI(self):
        self.setWindowTitle("batman v1")
        self.setMinimumSize(1150, 850)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #0d0d1c;
                color: #cdd6f4;
                font-family: 'Inter', 'Segoe UI', Arial;
            }
            QLineEdit {
                background-color: #1a1a2a;
                border: 1px solid #313244;
                border-radius: 8px;
                padding: 12px;
                color: #ffffff;
                font-family: Consolas, monospace;
            }
            QLineEdit:focus {
                border: 1px solid #89b4fa;
            }
            QPushButton {
                background-color: #1a1a2a;
                border: 1px solid #313244;
                border-radius: 8px;
                padding: 12px 20px;
                color: #cdd6f4;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #313244;
            }
            QPushButton#Action {
                background-color: #89b4fa;
                color: #0d0d1c;
                border: none;
            }
            QPushButton#Action:hover {
                background-color: #b4befe;
            }
        """)

        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        toolbar_layout = QHBoxLayout()
        toolbar_layout.addStretch()

        control_bar = QHBoxLayout()
        control_bar.setSpacing(10)
        self.url_input = QLineEdit()
        self.url_input.setFixedWidth(500)
        self.url_input.setPlaceholderText("ENTER URL OR VIDEO ID...")
        
        scan_btn = QPushButton("SCAN VIDEO")
        scan_btn.setObjectName("Action")
        scan_btn.setFixedWidth(120)
        scan_btn.clicked.connect(self.scan_one)

        file_btn = QPushButton("IMPORT BATCH")
        file_btn.clicked.connect(self.scan_bulk)
        
        export_btn = QPushButton("EXPORT EXCEL")
        export_btn.clicked.connect(self.export_excel)
        
        dir_btn = QPushButton("DIR")
        dir_btn.clicked.connect(self.change_folder)

        control_bar.addWidget(self.url_input)
        control_bar.addWidget(scan_btn)
        control_bar.addWidget(file_btn)
        control_bar.addWidget(export_btn)
        control_bar.addWidget(dir_btn)
        
        toolbar_layout.addLayout(control_bar)
        toolbar_layout.addStretch()

        layout.addLayout(toolbar_layout)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background-color: #0d0d1c; }")
        
        self.container = QWidget()
        self.container.setObjectName("Contents")
        self.container.setStyleSheet("QWidget#Contents { background-color: #0d0d1c; }")
        
        self.center_wrapper = QHBoxLayout(self.container)
        self.center_wrapper.setContentsMargins(0, 0, 0, 0)
        self.center_wrapper.addStretch()

        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.grid_layout.setSpacing(30)
        
        self.center_wrapper.addWidget(self.grid_container)
        self.center_wrapper.addStretch()
        
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

    def change_folder(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Folder", self.save_directory)
        if dir_path:
            self.save_directory = dir_path

    def scan_one(self):
        url = self.url_input.text()
        if url:
            vid_id = self.extract_id(url)
            self.fetch_and_display(vid_id)
        self.url_input.clear()

    def scan_bulk(self):
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
                        self.fetch_and_display(vid)
            except Exception as e:
                pass

    def extract_id(self, url):
        match = re.search(r'/video/([a-zA-Z0-9]+)', url)
        return match.group(1) if match else url.strip().split('/')[-1]

    def format_updated_time(self, timestamp):
        try:
            dt_object = datetime.datetime.fromtimestamp(timestamp)
            return dt_object.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return ""

    def fetch_and_display(self, vid_id):
        url = self.api_endpoint.format(video_id=vid_id.strip())
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                self.video_data_list.append(data)
                card = VideoCard(data, self)
                row = self.card_count // 2
                col = self.card_count % 2
                self.grid_layout.addWidget(card, row, col)
                self.card_count += 1
        except Exception as e:
            pass

    def export_excel(self):
        if not self.video_data_list:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save", "report.xlsx", "Excel (*.xlsx)")
        if path:
            pd.DataFrame(self.video_data_list).to_excel(path, index=False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DailymotionVideoInfoApp()
    window.show()
    sys.exit(app.exec_())
