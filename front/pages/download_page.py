"""
front/pages/download_page.py — Downloader Page (AuraOS Redesign V2)
====================================================================
"""

import os
import threading
import time

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QProgressBar, QScrollArea, QFrame, QMessageBox,
    QFileDialog, QGraphicsDropShadowEffect, QListView
)
from PyQt5.QtGui import QPixmap, QFont, QCursor, QColor
from PyQt5.QtCore import Qt, pyqtSignal

from front.design import COLORS as C, FONT_HEADLINE, FONT_BODY, BORDER_RADIUS_CARD, action_btn_style, danger_btn_style
from back.engine import DownloadEngine, parse_progress, DownloadCancelled
from back.config import load_download_path, save_download_path
from back.workers import DownloadWorkerSignals


class QueueItemWidget(QFrame):
    def __init__(self, index, item_data, is_active, parent_page):
        super().__init__()
        self.index = index
        self.item_data = item_data
        self.parent_page = parent_page
        self.is_active = is_active
        self._build_ui()

    def _build_ui(self):
        self.setObjectName("QueueItem")
        # Style is now handled globally in design.py
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        num = QLabel(f"{self.index + 1}")
        num.setFixedWidth(24)
        num.setObjectName("StatusLabel")
        layout.addWidget(num)

        title_str = str(self.item_data.get('title', 'Video'))
        title = QLabel(title_str[:45] + ("..." if len(title_str) > 45 else ""))
        title.setObjectName("SubtitleLabel")
        layout.addWidget(title, 1)

        status = self.item_data.get('status', 'Waiting')
        badge = QLabel(status.upper())
        badge.setObjectName("StatusLabel")
        layout.addWidget(badge)

        if not self.is_active:
            remove_btn = QPushButton("DELETE")
            remove_btn.setFixedSize(60, 28)
            remove_btn.setCursor(Qt.PointingHandCursor)
            remove_btn.setStyleSheet(f"QPushButton {{ background-color: transparent; color: {C['error']}; border: 1px solid {C['error']}; border-radius: 4px; font-size: 10px; font-weight: 800; }}")
            remove_btn.clicked.connect(lambda: self.parent_page.remove_item(self.index))
            layout.addWidget(remove_btn)


class DownloadPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.download_path = load_download_path()
        os.makedirs(self.download_path, exist_ok=True)
        self.queue = []
        self.is_downloading = False
        self.engine = DownloadEngine(self.download_path)
        self.signals = DownloadWorkerSignals()
        
        self._connect_signals()
        self.setObjectName("DownloadPage")
        self._build_ui()

    def _connect_signals(self):
        self.signals.update_progress.connect(self._on_progress)
        self.signals.download_error.connect(self._on_download_error)
        self.signals.download_cancelled.connect(self._on_download_cancelled)
        self.signals.analysis_done.connect(self._on_analysis_done)
        self.signals.analysis_error.connect(self._on_analysis_error)
        self.signals.status_text.connect(self._on_status_text)
        self.signals.refresh_queue.connect(self.refresh_queue_display)
        self.signals.all_done.connect(self._on_all_done)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(32)

        # Header
        header = QVBoxLayout()
        title = QLabel("Downloads")
        title.setObjectName("PageTitle")
        header.addWidget(title)
        
        self.sub_info = QLabel("0 Active, 0 Completed")
        self.sub_info.setObjectName("SubtitleLabel")
        header.addWidget(self.sub_info)
        layout.addLayout(header)

        # Main Content Split
        content = QHBoxLayout()
        content.setSpacing(32)

        # Left Column
        left_box = QVBoxLayout()
        left_box.setSpacing(24)
        
        # 1. Action Card
        self.action_card = QFrame()
        self.action_card.setObjectName("BentoCard")
        action_layout = QVBoxLayout(self.action_card)
        action_layout.setContentsMargins(24, 24, 24, 24)
        action_layout.setSpacing(20)
        
        url_label = QLabel("NEW DOWNLOAD")
        url_label.setObjectName("SectionTitle")
        action_layout.addWidget(url_label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste video URL here...")
        self.url_input.setMinimumHeight(44)
        action_layout.addWidget(self.url_input)
        
        row = QHBoxLayout()
        self.quality_combo = QComboBox()
        self.quality_combo.setView(QListView())
        self.quality_combo.addItems(["Best Available", "1080p", "720p", "480p"])
        self.quality_combo.setMinimumHeight(44)
        row.addWidget(self.quality_combo, 1)
        
        self.analyze_btn = QPushButton("ANALYZE")
        self.analyze_btn.setObjectName("ActionButton")
        self.analyze_btn.setFixedSize(120, 44)
        self.analyze_btn.clicked.connect(self._start_analyze)
        row.addWidget(self.analyze_btn)
        action_layout.addLayout(row)
        
        folder_card = QFrame()
        folder_card.setObjectName("FolderCard")
        f_layout = QHBoxLayout(folder_card)
        f_layout.setContentsMargins(12, 4, 12, 4)
        self.folder_label = QLabel(f"{self.download_path[:50]}...")
        self.folder_label.setObjectName("SubtitleLabel")
        f_layout.addWidget(self.folder_label, 1)
        
        change_btn = QPushButton("CHANGE")
        change_btn.setObjectName("ChangeFolderBtn")
        change_btn.setCursor(Qt.PointingHandCursor)
        change_btn.clicked.connect(self._change_folder)
        f_layout.addWidget(change_btn)
        action_layout.addWidget(folder_card)
        
        left_box.addWidget(self.action_card)
        
        # 2. Progress Card
        self.progress_card = QFrame()
        self.progress_card.setObjectName("BentoCard")
        prog_layout = QVBoxLayout(self.progress_card)
        prog_layout.setContentsMargins(24, 24, 24, 24)
        prog_layout.setSpacing(16)
        
        prog_title_label = QLabel("ACTIVE PROCESS")
        prog_title_label.setObjectName("SectionTitle")
        prog_layout.addWidget(prog_title_label)
        
        self.active_title = QLabel("Ready to download")
        self.active_title.setObjectName("SubtitleLabel")
        self.active_title.setWordWrap(True)
        prog_layout.addWidget(self.active_title)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 1000)
        self.progress_bar.setValue(0)
        prog_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Idle")
        self.status_label.setObjectName("SubtitleLabel")
        prog_layout.addWidget(self.status_label)
        
        left_box.addWidget(self.progress_card)
        left_box.addStretch()
        content.addLayout(left_box, 3)

        # Right Column: Queue
        self.queue_card = QFrame()
        self.queue_card.setObjectName("BentoCard")
        q_layout = QVBoxLayout(self.queue_card)
        q_layout.setContentsMargins(24, 24, 24, 24)
        
        q_title = QLabel("ACTIVE QUEUE")
        q_title.setObjectName("SectionTitle")
        q_layout.addWidget(q_title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        self.queue_container = QWidget()
        self.queue_layout = QVBoxLayout(self.queue_container)
        self.queue_layout.setSpacing(10)
        self.queue_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.queue_container)
        q_layout.addWidget(scroll)
        
        self.start_btn = QPushButton("START QUEUE")
        self.start_btn.setStyleSheet(action_btn_style())
        self.start_btn.setMinimumHeight(48)
        self.start_btn.clicked.connect(self._start_queue)
        q_layout.addWidget(self.start_btn)
        
        self.cancel_btn = QPushButton("STOP")
        self.cancel_btn.setStyleSheet(danger_btn_style())
        self.cancel_btn.setMinimumHeight(48)
        self.cancel_btn.setVisible(False)
        self.cancel_btn.clicked.connect(self._cancel_download)
        q_layout.addWidget(self.cancel_btn)
        
        content.addWidget(self.queue_card, 2)
        layout.addLayout(content)

    def set_url_and_analyze(self, url: str):
        self.url_input.setText(url)
        self._start_analyze()

    def _change_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder", self.download_path)
        if path:
            self.download_path = path
            self.engine.download_path = path
            self.folder_label.setText(f"📁 {path[:40]}...")
            save_download_path(path)

    def _start_analyze(self):
        url = self.url_input.text().strip()
        if not url: return
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setText("...")
        threading.Thread(target=self._analyze_worker, args=(url,), daemon=True).start()

    def _analyze_worker(self, url):
        try:
            info = self.engine.analyze_video(url)
            self.signals.analysis_done.emit(info)
        except Exception as e:
            self.signals.analysis_error.emit(str(e))

    def _on_analysis_done(self, info):
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("ANALYZE")
        item = {
            "url": self.url_input.text().strip(),
            "title": info.get('title', 'Video'),
            "quality": self.quality_combo.currentText(),
            "status": "Waiting"
        }
        self.queue.append(item)
        self.refresh_queue_display()
        self.url_input.clear()
        self.sub_info.setText(f"{len([i for i in self.queue if i['status'] != 'Done'])} Active, {len([i for i in self.queue if i['status'] == 'Done'])} Completed")

    def _on_analysis_error(self, msg):
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("ANALYZE")
        QMessageBox.warning(self, "Analysis Error", msg)

    def refresh_queue_display(self):
        while self.queue_layout.count():
            child = self.queue_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
        for i, item in enumerate(self.queue):
            if item['status'] == 'Done': continue
            is_active = (i == 0 and self.is_downloading)
            self.queue_layout.addWidget(QueueItemWidget(i, item, is_active, self))

    def remove_item(self, idx):
        self.queue.pop(idx)
        self.refresh_queue_display()

    def _cancel_download(self):
        self.engine.cancel_download()
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setText("Stopping...")

    def _start_queue(self):
        if self.is_downloading or not self.queue: return
        self.is_downloading = True
        self.start_btn.setVisible(False)
        self.cancel_btn.setVisible(True)
        self.cancel_btn.setEnabled(True)
        self.cancel_btn.setText("STOP")
        threading.Thread(target=self._process_queue, daemon=True).start()

    def _process_queue(self):
        while self.queue:
            if self.engine.is_cancelled(): break
            item = self.queue[0]
            if item['status'] == 'Done': 
                self.queue.pop(0)
                continue
            
            item["status"] = "Downloading"
            self.signals.refresh_queue.emit()
            self.signals.status_text.emit(f"Preparing: {item['title'][:40]}...")
            
            def hook(d):
                result = parse_progress(d)
                if result:
                    pf, ps, speed = result
                    self.signals.update_progress.emit(pf, ps, speed)

            try:
                self.engine.start_download(item['url'], item['quality'], hook)
                item['status'] = "Done"
                self.queue.pop(0)
                self.signals.refresh_queue.emit()
            except DownloadCancelled:
                break
            except Exception as e:
                self.signals.download_error.emit(str(e))
                self.queue.pop(0)
                self.signals.refresh_queue.emit()
            time.sleep(0.5)

        self.is_downloading = False
        self.signals.all_done.emit()

    def _on_progress(self, fraction, percent_str, speed_str):
        self.progress_bar.setValue(int(fraction * 1000))
        self.status_label.setText(f"{percent_str}% • {speed_str}")

    def _on_download_error(self, msg):
        QMessageBox.warning(self, "Download Error", msg)

    def _on_status_text(self, text):
        self.status_label.setText(text)

    def _on_download_cancelled(self):
        self._on_all_done()
        self.status_label.setText("Stopped.")

    def _on_all_done(self):
        self.is_downloading = False
        self.start_btn.setVisible(True)
        self.cancel_btn.setVisible(False)
        self.progress_bar.setValue(0)
        self.active_title.setText("Ready to download")
        self.status_label.setText("All tasks finished")
        self.refresh_queue_display()
        self.sub_info.setText(f"0 Active, {len([i for i in self.queue if i['status'] == 'Done'])} Completed")

    def refresh_theme(self):
        """Standardized refresh handled by QApplication."""
        self.refresh_queue_display()
