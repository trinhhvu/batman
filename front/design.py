"""
design.py — Unified Design System for Batman v2
================================================
Centralizes ALL color tokens, font settings, and reusable QSS stylesheets.
Matches the HTML mockup design system (Material 3 dark theme).

Used by: app.py, sidebar.py, download_page.py, analytics_page.py, video_card.py, queue_item.py

If an AI assistant is continuing this project, this file is the SINGLE SOURCE OF TRUTH
for all visual styling. Do NOT hardcode colors in other files — import from here.
"""

# ============================================================
# COLOR TOKENS (from Tailwind config in the HTML mockup)
# ============================================================

COLORS = {
    # Surfaces (backgrounds)
    "surface":                  "#0d0d1c",
    "surface_container_lowest": "#000000",
    "surface_container_low":    "#121222",
    "surface_container":        "#18182a",
    "surface_container_high":   "#1e1e32",
    "surface_container_highest":"#24243a",
    "surface_bright":           "#2a2a42",
    "surface_variant":          "#24243a",

    # Primary (blue accent)
    "primary":                  "#8cb7fe",
    "primary_dim":              "#7faaef",
    "primary_container":        "#77a2e6",
    "on_primary":               "#003469",
    "on_primary_container":     "#002249",

    # Secondary (green success)
    "secondary":                "#b4f2af",
    "secondary_dim":            "#a7e4a2",
    "secondary_container":      "#19511f",
    "on_secondary":             "#265d29",

    # Error (red)
    "error":                    "#ff716c",
    "error_dim":                "#d7383b",
    "error_container":          "#9f0519",

    # Tertiary (pink)
    "tertiary":                 "#ffa0b9",

    # Text / On-surface
    "on_surface":               "#e6e3f9",
    "on_surface_variant":       "#aba9be",
    "on_background":            "#e6e3f9",

    # Outlines / Borders
    "outline":                  "#757387",
    "outline_variant":          "#474658",
}

# Shorthand access
C = COLORS

# Manrope and Inter are bundled or downloaded as Google Fonts, 
# but we add OS-native fallbacks just in case.
FONT_HEADLINE = "'Manrope', 'Inter', 'Segoe UI', 'San Francisco', 'Helvetica Neue', 'Arial', sans-serif"
FONT_BODY = "'Inter', 'Segoe UI', 'San Francisco', 'Helvetica Neue', 'Arial', sans-serif"
FONT_MONO = "'Consolas', 'Menlo', 'Monaco', 'DejaVu Sans Mono', 'Courier New', monospace"

# ============================================================
# DIMENSION TOKENS
# ============================================================

NAVBAR_HEIGHT = 72
BORDER_RADIUS_CARD = 20
BORDER_RADIUS_BUTTON = 12
BORDER_RADIUS_INPUT = 10

# ============================================================
# REUSABLE QSS STYLESHEETS
# ============================================================

def get_main_window_qss():
    """Global stylesheet for the main QApplication window."""
    return f"""
        QWidget {{
            background-color: {C['surface']};
            color: {C['on_surface']};
            font-family: {FONT_BODY};
            font-size: 13px;
        }}
        QLineEdit {{
            background-color: {C['surface_container_low']};
            border: 2px solid {C['outline_variant']}40;
            border-radius: {BORDER_RADIUS_INPUT}px;
            padding: 10px 14px;
            color: {C['on_surface']};
            font-family: {FONT_MONO};
            font-size: 13px;
        }}
        QLineEdit:focus {{
            border: 2px solid {C['primary']};
        }}
        QPushButton {{
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #24243a, stop:1 #1e1e32);
            border: 1px solid #474658;
            border-radius: {BORDER_RADIUS_BUTTON}px;
            padding: 10px 20px;
            color: {C['on_surface']};
            font-weight: bold;
            font-size: 12px;
            font-family: {FONT_HEADLINE};
            outline: none;
        }}
        QPushButton:hover {{
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2a2a42, stop:1 #24243a);
            border: 1px solid #757387;
        }}
        QPushButton:pressed {{
            background-color: #1a1a2e;
        }}
        QPushButton#ActionButton {{
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8cb7fe, stop:1 #7faaef);
            color: {C['on_primary']};
            border: 1px solid #8cb7fe;
            font-weight: 800;
        }}
        QPushButton#ActionButton:hover {{
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7faaef, stop:1 #77a2e6);
        }}
        QPushButton#DangerButton {{
            background-color: {C['error']};
            color: #ffffff;
            border: none;
        }}
        QPushButton#DangerButton:hover {{
            background-color: {C['error_dim']};
        }}
        QScrollArea {{
            border: none;
            background-color: {C['surface']};
        }}
        QScrollBar:vertical {{
            background: {C['surface_container']};
            width: 8px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical {{
            background: {C['outline_variant']};
            border-radius: 4px;
            min-height: 30px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        QProgressBar {{
            background-color: {C['surface_container_highest']};
            border: none;
            border-radius: 4px;
            text-align: center;
            color: transparent;
            height: 8px;
        }}
        QProgressBar::chunk {{
            background-color: {C['secondary']};
            border-radius: 4px;
        }}
        QComboBox {{
            background-color: {C['surface_container_high']};
            border: 2px solid {C['outline_variant']}20;
            border-radius: {BORDER_RADIUS_INPUT}px;
            padding: 8px 14px;
            color: {C['on_surface']};
            font-size: 12px;
        }}
        QComboBox:hover {{
            border: 2px solid {C['primary']};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        QComboBox QAbstractItemView {{
            background-color: #1e1e32;
            color: #e6e3f9;
            border: 1px solid #474658;
            border-radius: 8px;
            selection-background-color: #2a2a42;
            selection-color: #8cb7fe;
            outline: none;
            padding: 4px;
        }}
        QComboBox QAbstractItemView::item {{
            padding: 8px 12px;
            border-radius: 6px;
            margin: 2px 0;
        }}
        QComboBox QAbstractItemView::item:hover {{
            background-color: #24243a;
        }}
    """


def get_navbar_qss():
    """Stylesheet for the top navigation bar."""
    return f"""
        QFrame#Navbar {{
            background-color: {C['surface']};
            border-bottom: 2px solid {C['outline_variant']}30;
        }}
    """


def get_navbar_button_qss(active=False):
    """Stylesheet for a navigation button (Navbar)."""
    if active:
        return f"""
            QPushButton {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8cb7fe, stop:1 #7faaef);
                color: {C['on_primary']};
                border: none;
                border-radius: 12px;
                padding: 10px 24px;
                font-weight: 800;
                font-size: 13px;
                font-family: {FONT_HEADLINE};
                text-align: left;
                padding-left: 20px;
                outline: none;
            }}
        """
    else:
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {C['on_surface_variant']};
                border: none;
                border-radius: 12px;
                padding: 10px 24px;
                font-weight: 500;
                font-size: 13px;
                font-family: {FONT_HEADLINE};
                text-align: left;
                padding-left: 20px;
                outline: none;
            }}
            QPushButton:hover {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #24243a, stop:1 #1e1e32);
                color: {C['on_surface']};
            }}
        """
