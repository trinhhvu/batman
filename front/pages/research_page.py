
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QFrame, QGridLayout, QMessageBox, QComboBox, QListView
)
from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtCore import Qt, pyqtSignal

from front.design import COLORS as C, FONT_HEADLINE, FONT_BODY, action_btn_style, danger_btn_style
from front.pages.analyze_page import VideoCard
from back.workers import ResearchWorker


class ResearchPage(QWidget):


    request_download = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.card_count = 0
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(32)

        # Header
        header = QVBoxLayout()
        self.title = QLabel("Research & Trend")
        self.title.setObjectName("PageTitle")
        header.addWidget(self.title)
        
        self.subtitle = QLabel("Discover trending keywords, competitor content, and cross-platform performance.")
        self.subtitle.setObjectName("SubtitleLabel")
        header.addWidget(self.subtitle)
        layout.addLayout(header)

        # Toolbar
        self.toolbar = QFrame()
        self.toolbar.setObjectName("BentoCard")
        tool_layout = QHBoxLayout(self.toolbar)
        tool_layout.setContentsMargins(20, 10, 20, 10)
        tool_layout.setSpacing(12)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter a keyword to search...")
        self.search_input.setMinimumHeight(44)
        self.search_input.returnPressed.connect(self._do_research)
        tool_layout.addWidget(self.search_input, 1)
        
        self.sort_combo = QComboBox()
        self.sort_combo.setView(QListView())
        self.sort_combo.setMinimumHeight(44)
        self.sort_combo.setFixedWidth(220)
        self.sort_combo.addItems([
            "trending: Trending",
            "visited-hour: Top Views (1h)",
            "visited-today: Top Views (24h)",
            "visited-week: Top Views (7d)",
            "visited: Top Views (All Time)",
            "recent: Recent Uploads"
        ])
        tool_layout.addWidget(self.sort_combo)
        
        self.search_btn = QPushButton("SEARCH")
        self.search_btn.setStyleSheet(action_btn_style())
        self.search_btn.setFixedSize(120, 44)
        self.search_btn.setCursor(Qt.PointingHandCursor)
        self.search_btn.clicked.connect(self._do_research)
        tool_layout.addWidget(self.search_btn)
        
        clear_btn = QPushButton("CLEAR")
        clear_btn.setStyleSheet(danger_btn_style())
        clear_btn.setFixedSize(100, 44)
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.clicked.connect(self._clear_all)
        tool_layout.addWidget(clear_btn)
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
        
        self.status_bar = QLabel("Ready")
        self.status_bar.setObjectName("SubtitleLabel")
        layout.addWidget(self.status_bar)

    def _do_research(self):
        query = self.search_input.text().strip()
        if not query: return
        self._clear_all()
        sort_mode = self.sort_combo.currentText().split(':')[0]
        self.status_bar.setText("Searching...")
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
        self.grid_layout.addWidget(card, self.card_count // 2, self.card_count % 2)
        self.card_count += 1
        self.status_bar.setText(f"Found {self.card_count} videos...")

    def _on_search_finished(self):
        self.search_btn.setEnabled(True)
        self.status_bar.setText(f"Complete. {self.card_count} videos loaded.")

    def _on_search_error(self, err_msg):
        self.search_btn.setEnabled(True)
        self.status_bar.setText("Error occurred.")
        QMessageBox.warning(self, "Research Error", err_msg)

    def _clear_all(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self.card_count = 0
        self.status_bar.setText("Cleared.")
