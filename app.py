"""
app.py — Main Application Window (Unified DDproject)
=====================================================
Combines the Downloader and Analytics into a single window with
sidebar navigation and page switching via QStackedWidget.

This is the central orchestrator. It creates:
  1. Sidebar (widgets/sidebar.py) — navigation
  2. DownloadPage (pages/download_page.py) — video downloader
  3. AnalyticsPage (pages/analytics_page.py) — video analytics

Dependencies: PyQt5, sidebar.py, download_page.py, analytics_page.py, design.py
Entry point: main.py
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QStackedWidget
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

from widgets.sidebar import Sidebar
from pages.download_page import DownloadPage
from pages.analytics_page import AnalyticsPage
from design import get_main_window_qss, FONT_HEADLINE, COLORS as C

import os


class DDProjectApp(QWidget):
    """
    Main application window.
    Layout: [Sidebar 240px] | [Content Area (stacked pages)]
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Batman v2 — The Ultimate Suite")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)
        self.setStyleSheet(get_main_window_qss())

        # Load Batman Icon
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ──
        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self._switch_page)
        root.addWidget(self.sidebar)

        # ── Stacked pages ──
        self.stack = QStackedWidget()

        self.download_page = DownloadPage()
        self.analytics_page = AnalyticsPage()

        self.stack.addWidget(self.download_page)   # index 0
        self.stack.addWidget(self.analytics_page)   # index 1

        root.addWidget(self.stack, 1)

    def _switch_page(self, page_id):
        """Switch the visible page based on sidebar signal."""
        page_map = {
            "download": 0,
            "analytics": 1,
        }
        idx = page_map.get(page_id, 0)
        self.stack.setCurrentIndex(idx)
