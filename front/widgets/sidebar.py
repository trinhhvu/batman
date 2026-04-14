"""
sidebar.py — Sidebar Navigation Widget (TRACK)
================================================
PURE UI — no business logic, no API calls.
"""

from PyQt5.QtWidgets import (
    QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox
)
from PyQt5.QtCore import pyqtSignal, Qt, pyqtSlot, QMetaObject, Q_ARG
from PyQt5.QtGui import QFont
import threading

from front.design import (
    COLORS as C, FONT_HEADLINE, NAVBAR_HEIGHT,
    get_navbar_qss, get_navbar_button_qss
)


class Sidebar(QFrame):
    """Horizontal navigation bar. Emits `page_changed(str)` when a nav button is clicked."""

    page_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Navbar")
        self.setFixedHeight(NAVBAR_HEIGHT)
        self.setStyleSheet(get_navbar_qss())
        self.current_page = "analyze"
        self._buttons = {}
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(12)

        # ── Logo Section (Left) ──
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(0)
        logo_layout.setAlignment(Qt.AlignCenter)

        logo_label = QLabel("BATMAN V3")
        logo_label.setFont(QFont(FONT_HEADLINE, 16, QFont.Bold))
        logo_label.setStyleSheet(f"color: {C['on_surface']}; letter-spacing: -1px; background: transparent; border: none;")
        logo_layout.addWidget(logo_label)

        subtitle = QLabel("FINAL SUPER MẠNH MẾ")
        subtitle.setStyleSheet(
            f"color: {C['on_surface_variant']}; font-size: 8px; "
            f"font-weight: bold; letter-spacing: 2px; background: transparent; border: none;"
        )
        logo_layout.addWidget(subtitle)
        layout.addWidget(logo_container)

        layout.addStretch()

        # ── Navigation Buttons (Center Grouped) ──
        nav_container = QWidget()
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(8)

        nav_items = [
            ("analyze",  "📊  Analyze"),
            ("download", "⬇  Download"),
            ("scanner",  "📡  Scanner"),
            ("research", "🔍  Research"),
        ]

        for page_id, label in nav_items:
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(40)
            btn.clicked.connect(lambda checked, pid=page_id: self._on_nav_click(pid))
            self._buttons[page_id] = btn
            nav_layout.addWidget(btn)

        layout.addWidget(nav_container)
        layout.addStretch()

        # ── Right Section (IP + Version) ──
        right_container = QWidget()
        right_layout = QHBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(20)

        self.ip_btn = QPushButton("📍 IP Info")
        self.ip_btn.setCursor(Qt.PointingHandCursor)
        self.ip_btn.setStyleSheet(f"""
            QPushButton {{
                color: {C['outline']};
                font-size: 11px;
                background: transparent;
                border: none;
                padding: 4px;
            }}
            QPushButton:hover {{
                color: {C['primary']};
                text-decoration: underline;
            }}
        """)
        self.ip_btn.clicked.connect(self._on_ip_check_click)
        right_layout.addWidget(self.ip_btn)

        version_label = QLabel("v3.0 Unified")
        version_label.setStyleSheet(f"color: {C['outline']}; font-size: 10px; background: transparent; border: none;")
        right_layout.addWidget(version_label)

        layout.addWidget(right_container)
        self._refresh_styles()

    def _on_nav_click(self, page_id):
        if page_id == self.current_page:
            return
        self.current_page = page_id
        self._refresh_styles()
        self.page_changed.emit(page_id)

    def _refresh_styles(self):
        for pid, btn in self._buttons.items():
            btn.setStyleSheet(get_navbar_button_qss(active=(pid == self.current_page)))

    def _on_ip_check_click(self):
        self.ip_btn.setText("Checking...")
        self.ip_btn.setEnabled(False)

        def _fetch():
            try:
                import requests
                response = requests.get("https://ipapi.co/json/", timeout=5)
                data = response.json()
                ip = data.get("ip", "Unknown")
                country = data.get("country_name", "Unknown")
                city = data.get("city", "")
                info = f"🌐 IP: {ip}\n📍 Location: {city}, {country}" if city else f"🌐 IP: {ip}\n📍 Location: {country}"
                QMetaObject.invokeMethod(self, "_show_ip_result", Qt.QueuedConnection,
                                        Q_ARG(str, "Network Info"), Q_ARG(str, info))
            except Exception as e:
                QMetaObject.invokeMethod(self, "_show_ip_result", Qt.QueuedConnection,
                                        Q_ARG(str, "Error"), Q_ARG(str, f"Could not fetch IP info: {e}"))
            finally:
                QMetaObject.invokeMethod(self, "_reset_ip_button", Qt.QueuedConnection)

        threading.Thread(target=_fetch, daemon=True).start()

    @pyqtSlot(str, str)
    def _show_ip_result(self, title, message):
        if title == "Error":
            QMessageBox.warning(self, title, message)
        else:
            QMessageBox.information(self, title, message)

    @pyqtSlot()
    def _reset_ip_button(self):
        self.ip_btn.setText("📍 What is my IP?")
        self.ip_btn.setEnabled(True)
