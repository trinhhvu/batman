"""
front/pages/research_page.py — Research & Trend Discovery (PURE UI)
====================================================================
Displays search results. All API logic in back/workers.py.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QFrame, QGridLayout, QMessageBox, QComboBox
)
from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtCore import Qt, pyqtSignal

from front.design import COLORS as C, FONT_HEADLINE
from front.pages.analyze_page import VideoCard
from back.workers import ResearchWorker


class ResearchPage(QWidget):
    """Research page — PURE UI shell. Worker lives in back/workers.py."""

    request_download = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.card_count = 0
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)

        header = QLabel("Research & Trend")
        header.setFont(QFont(FONT_HEADLINE, 22, QFont.ExtraBold))
        header.setStyleSheet(f"color: {C['on_surface']};")
        layout.addWidget(header)

        sub = QLabel("Search Dailymotion for trending keywords, filter by views, and discover competitor content.")
        sub.setStyleSheet(f"color: {C['on_surface_variant']}; font-size: 13px;")
        layout.addWidget(sub)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter a keyword to search...")
        self.search_input.setFixedWidth(400)
        self.search_input.returnPressed.connect(self._do_research)
        toolbar.addWidget(self.search_input)

        self.sort_combo = QComboBox()
        self.sort_combo.setFixedWidth(200)
        self.sort_combo.addItems([
            "trending: 🔥 Trending",
            "visited-hour: 🚀 Top Views (1h)",
            "visited-today: 📅 Top Views (24h)",
            "visited-week: 📆 Top Views (7d)",
            "visited: 📈 Top Views (All Time)",
            "recent: 🆕 Recent Uploads"
        ])
        toolbar.addWidget(self.sort_combo)

        self.search_btn = QPushButton("SEARCH")
        self.search_btn.setObjectName("ActionButton")
        self.search_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.search_btn.setFixedWidth(120)
        self.search_btn.clicked.connect(self._do_research)
        toolbar.addWidget(self.search_btn)

        clear_btn = QPushButton("CLEAR")
        clear_btn.setObjectName("DangerButton")
        clear_btn.setCursor(QCursor(Qt.PointingHandCursor))
        clear_btn.clicked.connect(self._clear_all)
        toolbar.addWidget(clear_btn)

        self.status_label = QLabel()
        self.status_label.setStyleSheet(f"color: {C['primary']}; font-size: 13px; font-weight: bold;")
        toolbar.addWidget(self.status_label)
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

    def _do_research(self):
        query = self.search_input.text().strip()
        if not query:
            return
        self._clear_all()
        sort_mode = self.sort_combo.currentText().split(':')[0]
        self.status_label.setText("Searching...")
        self.search_btn.setEnabled(False)

        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()

        self.worker = ResearchWorker(query, sort_mode)
        self.worker.card_ready.connect(self._on_card_ready)
        self.worker.finished.connect(self._on_search_finished)
        self.worker.error.connect(self._on_search_error)
        self.worker.start()

    def _on_card_ready(self, data):
        card = VideoCard(data, self)
        card.send_to_download.connect(self.request_download.emit)
        row = self.card_count // 2
        col = self.card_count % 2
        self.grid_layout.addWidget(card, row, col)
        self.card_count += 1
        self.status_label.setText(f"Found {self.card_count} videos...")

    def _on_search_finished(self):
        self.search_btn.setEnabled(True)
        self.status_label.setText(f"Complete. {self.card_count} videos loaded.")

    def _on_search_error(self, err_msg):
        self.search_btn.setEnabled(True)
        self.status_label.setText("Error occurred.")
        QMessageBox.warning(self, "Research Error", f"Failed to perform research: {err_msg}")

    def _clear_all(self):
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.card_count = 0
        self.status_label.setText("")
