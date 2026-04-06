"""
sidebar.py — Sidebar Navigation Widget (TRACK)
================================================
Provides the left-side navigation panel for the unified TRACK app.
Contains navigation buttons: Analyze, Download, Scanner.

Emits signals when a page is selected so the main app can switch views.
Imports design tokens from design.py.

Dependencies: PyQt5, design.py
Used by: gui.py
"""

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont

from design import (
    COLORS as C, FONT_HEADLINE, SIDEBAR_WIDTH,
    get_sidebar_qss, get_sidebar_button_qss
)


class Sidebar(QFrame):
    """Left navigation sidebar. Emits `page_changed(str)` when a nav button is clicked."""

    page_changed = pyqtSignal(str)  # "analyze", "download", or "scanner"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(SIDEBAR_WIDTH)
        self.setStyleSheet(get_sidebar_qss())
        self.current_page = "analyze"
        self._buttons = {}

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 30, 20, 20)
        layout.setSpacing(8)

        # ── Logo Section ──
        logo_label = QLabel("BATMAN V3")
        logo_label.setFont(QFont(FONT_HEADLINE, 18, QFont.Bold))
        logo_label.setStyleSheet(f"color: {C['on_surface']}; letter-spacing: -1px;")
        layout.addWidget(logo_label)

        subtitle = QLabel("FINAL SUPER MẠNH MẾ")
        subtitle.setStyleSheet(
            f"color: {C['on_surface_variant']}; font-size: 9px; "
            f"font-weight: bold; letter-spacing: 3px;"
        )
        layout.addWidget(subtitle)

        layout.addSpacing(40)

        # ── Navigation Buttons ──
        nav_items = [
            ("analyze",  "📊  Analyze"),
            ("download", "⬇  Download"),
            ("scanner",  "📡  Scan Channel"),
        ]

        for page_id, label in nav_items:
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, pid=page_id: self._on_nav_click(pid))
            self._buttons[page_id] = btn
            layout.addWidget(btn)

        # ── Spacer ──
        layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # ── Version Info ──
        version_label = QLabel("v3.0 Unified")
        version_label.setStyleSheet(f"color: {C['outline']}; font-size: 10px;")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)

        # Apply initial active state
        self._refresh_styles()

    def _on_nav_click(self, page_id):
        if page_id == self.current_page:
            return
        self.current_page = page_id
        self._refresh_styles()
        self.page_changed.emit(page_id)

    def _refresh_styles(self):
        for pid, btn in self._buttons.items():
            btn.setStyleSheet(get_sidebar_button_qss(active=(pid == self.current_page)))
