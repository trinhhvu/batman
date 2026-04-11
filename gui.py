"""
gui.py — Main Application Window (TRACK v3 Unified)
=====================================================
Combines three features into a single window with sidebar navigation
and page switching via QStackedWidget:

  1. AnalyzePage  — Scan single videos, display bento cards
  2. DownloadPage — Queue-based video downloader
  3. ScannerPage  — Channel batch scanner + selective download

Dependencies: PyQt5, design.py, widgets/sidebar.py, pages/*
Entry point: main.py
"""

from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from widgets.sidebar import Sidebar
from pages.analyze_page import AnalyzePage
from pages.download_page import DownloadPage
from pages.scanner_page import ScannerPage
from design import get_main_window_qss

import os


class TrackerApp(QMainWindow):
    """
    Main application window.
    Layout: [Sidebar 240px] | [Content Area (stacked pages)]
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("BATMAN V3 FINAL SUPER MẠNH MẼ NHẤT THẾ GIỚI")
        self.setMinimumSize(1200, 800)
        self.resize(1360, 860)
        self.setStyleSheet(get_main_window_qss())

        # Load Icon
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Navigation Bar (Top) ──
        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self._switch_page)
        root.addWidget(self.sidebar)

        # ── Stacked pages (Bottom) ──
        self.stack = QStackedWidget()

        self.analyze_page = AnalyzePage()
        self.download_page = DownloadPage()
        self.scanner_page = ScannerPage()

        self.stack.addWidget(self.analyze_page)    # index 0
        self.stack.addWidget(self.download_page)   # index 1
        self.stack.addWidget(self.scanner_page)    # index 2

        root.addWidget(self.stack, 1)

    def _connect_signals(self):
        """Wire inter-page communication signals."""
        # When a card's download icon is clicked on the Analyze page,
        # switch to the Download page and paste the URL.
        self.analyze_page.request_download.connect(self._send_to_download_page)

    def _send_to_download_page(self, url: str):
        """Switch to Download tab and start analyzing the given URL."""
        self.stack.setCurrentIndex(1)
        self.sidebar.current_page = "download"
        self.sidebar._refresh_styles()
        self.download_page.set_url_and_analyze(url)

    def _switch_page(self, page_id):
        """Switch the visible page based on sidebar signal."""
        page_map = {
            "analyze": 0,
            "download": 1,
            "scanner": 2,
        }
        idx = page_map.get(page_id, 0)
        self.stack.setCurrentIndex(idx)
