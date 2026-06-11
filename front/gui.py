
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QFrame, QGraphicsOpacityEffect
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve

from front.widgets.sidebar import Sidebar
from front.pages.analyze_page import AnalyzePage
from front.pages.download_page import DownloadPage
from front.pages.scanner_page import ScannerPage
from front.pages.research_page import ResearchPage
from front.pages.upload_page import UploadPage
from front.pages.settings_page import SettingsPage
from front.design import get_main_window_qss, COLORS as C, set_active_theme

import os


class TrackerApp(QMainWindow):
    """
    Main application window.
    Layout: [Sidebar (left)] | [Content Area (right)]
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cậu vàng")
        self.setMinimumSize(1200, 800)
        self.resize(1360, 860)

        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icon moi.jpg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._build_ui()
        self._connect_signals()
        self.apply_theme('light') # Force initial style application

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("CentralWidget")
        self.setCentralWidget(central)
        
        # Horizontal layout for Sidebar + Content
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar (Left)
        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self._switch_page)
        root.addWidget(self.sidebar)

        # Content Area (Right)
        self.content_container = QFrame()
        self.content_container.setObjectName("ContentContainer")
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        self.stack = QStackedWidget()
        self.analyze_page = AnalyzePage()
        self.download_page = DownloadPage()
        self.scanner_page = ScannerPage()
        self.research_page = ResearchPage()
        self.upload_page = UploadPage()
        self.settings_page = SettingsPage()

        self.stack.addWidget(self.analyze_page)    # index 0
        self.stack.addWidget(self.download_page)   # index 1
        self.stack.addWidget(self.scanner_page)    # index 2
        self.stack.addWidget(self.research_page)   # index 3
        self.stack.addWidget(self.upload_page)     # index 4
        self.stack.addWidget(self.settings_page)   # index 5

        content_layout.addWidget(self.stack)
        root.addWidget(self.content_container, 1)

    def _connect_signals(self):
        self.analyze_page.request_download.connect(self._send_to_download_page)
        self.research_page.request_download.connect(self._send_to_download_page)
        self.scanner_page.request_download.connect(self._send_to_download_page)

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
            "upload": 4,
            "settings": 5,
        }
        idx = page_map.get(page_id, 0)
        
        # Smooth Transition Animation
        target_widget = self.stack.widget(idx)
        
        # Set opacity effect
        opacity_effect = QGraphicsOpacityEffect(target_widget)
        target_widget.setGraphicsEffect(opacity_effect)
        
        # Create animation
        self.fade_anim = QPropertyAnimation(opacity_effect, b"opacity")
        self.fade_anim.setDuration(400)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # Switch and play
        self.stack.setCurrentIndex(idx)
        self.fade_anim.start()

    def apply_theme(self, theme_name):
        """Switch theme by updating the app-level stylesheet and system palette."""
        self.current_theme = theme_name
        set_active_theme(theme_name)

        # Apply to the entire application — this covers every widget at once
        QApplication.instance().setStyleSheet(get_main_window_qss())

        # Update sidebar (uses its own QSS selectors)
        if hasattr(self, 'sidebar'):
            self.sidebar.refresh_theme()

        # Update system palette (fixes native widgets: SpinBox arrows, scrollbars)
        self._update_palette()


    def _update_palette(self):
        """Update the system-wide palette to match the current theme."""
        from PyQt5.QtGui import QPalette, QColor
        palette = QPalette()
        c = C # Current colors in design.py
        
        palette.setColor(QPalette.Window,          QColor(c['surface']))
        palette.setColor(QPalette.WindowText,      QColor(c['on_surface']))
        palette.setColor(QPalette.Base,            QColor(c['surface_bright']))
        palette.setColor(QPalette.AlternateBase,   QColor(c['surface_container_low']))
        palette.setColor(QPalette.Text,            QColor(c['on_surface']))
        palette.setColor(QPalette.Button,          QColor(c['surface_bright']))
        palette.setColor(QPalette.ButtonText,      QColor(c['on_surface']))
        palette.setColor(QPalette.Highlight,       QColor(c['primary']))
        palette.setColor(QPalette.HighlightedText, QColor(c['on_primary']))
        palette.setColor(QPalette.PlaceholderText, QColor(c['on_surface_variant']))
        
        QApplication.instance().setPalette(palette)
