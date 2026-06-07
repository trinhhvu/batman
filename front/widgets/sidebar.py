
from PyQt5.QtWidgets import (
    QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import pyqtSignal, Qt, pyqtSlot, QMetaObject, Q_ARG, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QFont, QPixmap

from front.design import (
    COLORS as C, FONT_HEADLINE, get_navbar_button_qss, get_navbar_qss
)
from front.widgets.notification import show_notification


class Sidebar(QFrame):
    """Vertical navigation bar."""

    page_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(260)
        self.current_page = "analyze"
        self._buttons = {}
        self._build_ui()

    def _build_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 32, 0, 32)
        self.main_layout.setSpacing(8)

        # ── Logo Area ──
        logo_container = QWidget()
        logo_container.setStyleSheet("background: transparent;")
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(24, 0, 24, 32)
        logo_layout.setSpacing(4)
        
        logo_title = QLabel("Cậu vàng")
        logo_title.setFont(QFont(FONT_HEADLINE, 20, QFont.Bold))
        logo_title.setStyleSheet(f"color: {C['primary']}; letter-spacing: -0.5px; background: transparent;")
        logo_layout.addWidget(logo_title)
        

        self.main_layout.addWidget(logo_container)

        # ── Nav Container (for relative marker movement) ──
        self.nav_container = QWidget()
        self.nav_container.setStyleSheet("background: transparent;")
        self.nav_layout = QVBoxLayout(self.nav_container)
        self.nav_layout.setContentsMargins(0, 0, 0, 0)
        self.nav_layout.setSpacing(8)

        # The Sliding Marker
        self.marker = QFrame(self.nav_container)
        self.marker.setFixedHeight(48)
        self.marker.setFixedWidth(260)
        self.marker.setStyleSheet(f"""
            background-color: {C['surface_container']};
            border-left: 4px solid #000000;
        """)
        self.marker.lower() # Place behind buttons
        self.marker.show()

        # ── Nav Buttons ──
        nav_items = [
            ("analyze",  "Analyze"),
            ("download", "Download"),
            ("scanner",  "Scanner"),
            ("research", "Research"),
            ("upload",   "Upload"),
            ("settings", "Settings"),
        ]

        for page_id, label in nav_items:
            btn = QPushButton(f"{label}")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(48)
            btn.clicked.connect(lambda checked, pid=page_id: self._on_nav_click(pid))
            self._buttons[page_id] = btn
            self.nav_layout.addWidget(btn)

        self.main_layout.addWidget(self.nav_container)
        self.main_layout.addStretch()

        # ── Footer Info ──
        self.ip_btn = QPushButton("Public IP")
        self.ip_btn.setCursor(Qt.PointingHandCursor)
        self.ip_btn.setStyleSheet(f"""
            QPushButton {{
                color: {C['on_surface_variant']};
                font-size: 11px;
                background: transparent;
                border: none;
                text-align: left;
                padding-left: 24px;
            }}
            QPushButton:hover {{
                color: {C['primary']};
            }}
        """)
        self.ip_btn.clicked.connect(self._on_ip_check_click)
        self.main_layout.addWidget(self.ip_btn)

        self._refresh_styles(animate=False)

    def _on_nav_click(self, page_id):
        if page_id == self.current_page:
            return
        self.current_page = page_id
        self._refresh_styles(animate=True)
        self.page_changed.emit(page_id)

    def refresh_theme(self):
        """Update sidebar styling for light/dark mode."""
        self.setStyleSheet(get_navbar_qss())
        self.marker.setStyleSheet(f"""
            background-color: {C['surface_container']};
            border-left: 4px solid {C['on_surface']};
        """)
        self._refresh_styles(animate=False)

    def _refresh_styles(self, animate=True):
        # Update text colors
        for pid, btn in self._buttons.items():
            active = (pid == self.current_page)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {"#000000" if active else C['on_surface_variant']};
                    border: none;
                    padding-left: 24px;
                    font-weight: {"700" if active else "500"};
                    font-size: 14px;
                    font-family: {FONT_HEADLINE};
                    text-align: left;
                    outline: none;
                }}
            """)
            if active:
                self._move_marker(btn, animate)

    def _move_marker(self, target_btn, animate):
        target_y = target_btn.y()
        if not animate:
            self.marker.move(0, target_y)
            return

        self.anim = QPropertyAnimation(self.marker, b"pos")
        self.anim.setDuration(350)
        self.anim.setStartValue(self.marker.pos())
        self.anim.setEndValue(QPoint(0, target_y))
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

    def _on_ip_check_click(self):
        self.ip_btn.setText("Checking...")
        self.ip_btn.setEnabled(False)

        def _fetch():
            import requests
            headers = {"User-Agent": "Mozilla/5.0"}
            
            # List of GeoIP services with their specific key mappings
            # Format: (URL, IP_KEY, CITY_KEY, REGION_KEY, COUNTRY_KEY, ISP_KEY)
            services = [
                ("https://ipapi.co/json/", "ip", "city", "region", "country_name", "org"),
                ("http://ip-api.com/json/", "query", "city", "regionName", "country", "isp"),
                ("https://ipinfo.io/json", "ip", "city", "region", "country", "org")
            ]
            
            success = False
            for url, k_ip, k_city, k_region, k_country, k_isp in services:
                try:
                    resp = requests.get(url, headers=headers, timeout=6)
                    if resp.status_code == 200:
                        data = resp.json()
                        ip = data.get(k_ip)
                        if not ip: continue
                        
                        city = data.get(k_city, "Unknown City")
                        country = data.get(k_country, "Unknown Country")
                        
                        info = f"{ip}\n{city}, {country}"
                        QMetaObject.invokeMethod(self, "_show_ip_result", Qt.QueuedConnection,
                                                Q_ARG(str, ""), Q_ARG(str, info))
                        success = True
                        break
                except:
                    continue
            
            if not success:
                # Absolute fallback to ipify for just IP
                try:
                    ip = requests.get("https://api.ipify.org", timeout=5).text
                    QMetaObject.invokeMethod(self, "_show_ip_result", Qt.QueuedConnection,
                                            Q_ARG(str, ""), Q_ARG(str, f"{ip}\nLocation hidden"))
                except:
                    QMetaObject.invokeMethod(self, "_show_ip_result", Qt.QueuedConnection,
                                            Q_ARG(str, ""), Q_ARG(str, "Network Offline"))
            
            QMetaObject.invokeMethod(self, "_reset_ip_button", Qt.QueuedConnection)

        import threading
        threading.Thread(target=_fetch, daemon=True).start()

    @pyqtSlot(str, str)
    def _show_ip_result(self, title, message):
        # Use our new modern notification system
        show_notification(self.window(), title, message, duration=6000)

    @pyqtSlot()
    def _reset_ip_button(self):
        self.ip_btn.setText("Public IP")
        self.ip_btn.setEnabled(True)
