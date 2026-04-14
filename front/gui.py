"""
front/gui.py — Main Application Window (TRACK v3 Unified)
==========================================================
PURE UI shell. Wires sidebar navigation to page switching.
All business logic lives in back/.
"""

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from front.widgets.sidebar import Sidebar
from front.pages.analyze_page import AnalyzePage
from front.pages.download_page import DownloadPage
from front.pages.scanner_page import ScannerPage
from front.pages.research_page import ResearchPage
from front.design import get_main_window_qss, COLORS as C

import os


class TrackerApp(QMainWindow):
    """
    Main application window.
    Layout: [Navbar (top)] | [Content Area (stacked pages)]
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("BATMAN V3 FINAL SUPER MẠNH MẼ NHẤT THẾ GIỚI")
        self.setMinimumSize(1200, 800)
        self.resize(1360, 860)
        self.setStyleSheet(get_main_window_qss())

        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("MainWindow")
        central.setStyleSheet(f"""
            QWidget#MainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {C['surface']}, stop:1 #05050f);
            }}
        """)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Navigation Bar (Top)
        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self._switch_page)
        root.addWidget(self.sidebar)

        # Stacked pages
        self.stack = QStackedWidget()

        self.analyze_page = AnalyzePage()
        self.download_page = DownloadPage()
        self.scanner_page = ScannerPage()
        self.research_page = ResearchPage()

        self.stack.addWidget(self.analyze_page)    # index 0
        self.stack.addWidget(self.download_page)   # index 1
        self.stack.addWidget(self.scanner_page)    # index 2
        self.stack.addWidget(self.research_page)   # index 3

        root.addWidget(self.stack, 1)

    def _connect_signals(self):
        self.analyze_page.request_download.connect(self._send_to_download_page)
        self.research_page.request_download.connect(self._send_to_download_page)

    def _send_to_download_page(self, url: str):
        self.stack.setCurrentIndex(1)
        self.sidebar.current_page = "download"
        self.sidebar._refresh_styles()
        self.download_page.set_url_and_analyze(url)

    def _switch_page(self, page_id):
        page_map = {
            "analyze": 0,
            "download": 1,
            "scanner": 2,
            "research": 3,
        }
        idx = page_map.get(page_id, 0)
        self.stack.setCurrentIndex(idx)
