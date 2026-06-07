
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from front.design import COLORS as C, FONT_HEADLINE, get_main_window_qss
from front.widgets.toggle import ModernToggle

class SettingsPage(QWidget):
    """Application settings and theme configuration."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsPage")
        self._build_ui()

    def _build_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(32)

        # Header
        self.header = QVBoxLayout()
        self.title = QLabel("Settings")
        self.title.setFont(QFont(FONT_HEADLINE, 28, QFont.Bold))
        self.header.addWidget(self.title)
        
        self.subtitle = QLabel("Configure application preferences and system appearance.")
        self.subtitle.setObjectName("SubtitleLabel")
        self.header.addWidget(self.subtitle)
        self.layout.addLayout(self.header)

        # Appearance Card
        self.theme_card = QFrame()
        self.theme_card.setObjectName("BentoCard")
        theme_layout = QVBoxLayout(self.theme_card)
        theme_layout.setContentsMargins(24, 24, 24, 24)
        theme_layout.setSpacing(16)
        
        t_title = QLabel("APPEARANCE")
        t_title.setObjectName("SectionTitle")
        theme_layout.addWidget(t_title)
        
        row = QHBoxLayout()
        t_desc = QLabel("Enable Dark Mode for a minimalist Charcoal experience.")
        row.addWidget(t_desc, 1)
        
        self.toggle = ModernToggle()
        self.toggle.toggled.connect(self._handle_toggle)
        row.addWidget(self.toggle)
        
        theme_layout.addLayout(row)
        self.layout.addWidget(self.theme_card)

        self.layout.addStretch()

    def _handle_toggle(self, is_on):
        window = self.window()
        if hasattr(window, 'apply_theme'):
            new_theme = "dark" if is_on else "light"
            # Only apply if it's different to avoid loops
            if getattr(window, 'current_theme', '') != new_theme:
                window.apply_theme(new_theme)

    def refresh_theme(self):
        """Update colors and sync toggle state."""
        window = self.window()
        if hasattr(window, 'current_theme'):
            is_dark = window.current_theme == "dark"
            self.toggle.set_checked(is_dark, animate=False)
