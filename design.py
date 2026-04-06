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

# ============================================================
# FONT SETTINGS
# ============================================================

FONT_HEADLINE = "Manrope"
FONT_BODY = "Inter"
FONT_MONO = "Consolas"

# ============================================================
# DIMENSION TOKENS
# ============================================================

SIDEBAR_WIDTH = 240
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
            font-family: '{FONT_BODY}', 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
        }}
        QLineEdit {{
            background-color: {C['surface_container_low']};
            border: 2px solid {C['outline_variant']}40;
            border-radius: {BORDER_RADIUS_INPUT}px;
            padding: 10px 14px;
            color: {C['on_surface']};
            font-family: '{FONT_MONO}', monospace;
            font-size: 13px;
        }}
        QLineEdit:focus {{
            border: 2px solid {C['primary']};
        }}
        QPushButton {{
            background-color: {C['surface_container_high']};
            border: 2px solid {C['outline_variant']}20;
            border-radius: {BORDER_RADIUS_BUTTON}px;
            padding: 10px 20px;
            color: {C['on_surface']};
            font-weight: bold;
            font-size: 12px;
            font-family: '{FONT_HEADLINE}', sans-serif;
        }}
        QPushButton:hover {{
            background-color: {C['surface_container_highest']};
        }}
        QPushButton#ActionButton {{
            background-color: {C['primary']};
            color: {C['on_primary']};
            border: none;
            font-weight: 800;
        }}
        QPushButton#ActionButton:hover {{
            background-color: {C['primary_dim']};
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
            background-color: {C['surface_container_high']};
            color: {C['on_surface']};
            border: 1px solid {C['outline_variant']};
            selection-background-color: {C['primary']};
            selection-color: {C['on_primary']};
        }}
    """


def get_sidebar_qss():
    """Stylesheet for the sidebar navigation panel."""
    return f"""
        QFrame#Sidebar {{
            background-color: {C['surface']};
            border-right: 2px solid {C['outline_variant']}30;
        }}
    """


def get_sidebar_button_qss(active=False):
    """Stylesheet for a sidebar navigation button."""
    if active:
        return f"""
            QPushButton {{
                background-color: {C['primary']};
                color: {C['on_primary']};
                border: none;
                border-radius: 12px;
                padding: 12px 16px;
                font-weight: 800;
                font-size: 13px;
                font-family: '{FONT_HEADLINE}', sans-serif;
                text-align: left;
            }}
        """
    else:
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {C['on_surface_variant']};
                border: none;
                border-radius: 12px;
                padding: 12px 16px;
                font-weight: 500;
                font-size: 13px;
                font-family: '{FONT_HEADLINE}', sans-serif;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {C['surface_container_high']};
                color: {C['on_surface']};
            }}
        """
