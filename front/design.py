"""
design.py — Unified Design System for AuraOS / Batman v3
========================================================
Centralizes ALL color tokens, font settings, and reusable QSS stylesheets.
"""

LIGHT_COLORS = {
    "surface":                  "#f1f3f5",
    "surface_dim":              "#e9ecef",
    "surface_bright":           "#ffffff",
    "surface_container_lowest": "#ffffff",
    "surface_container_low":    "#f8f9fa",
    "surface_container":        "#e9ecef",
    "surface_container_high":   "#dee2e6",
    "surface_container_highest":"#ced4da",
    "primary":                  "#212529",
    "on_primary":               "#ffffff",
    "on_surface":               "#212529",
    "on_surface_variant":       "#495057",
    "error":                    "#c92a2a",
    "error_container":          "#fff5f5",
    "success":                  "#2b8a3e",
    "outline":                  "#adb5bd",
    "outline_variant":          "#e9ecef",
    "notification_bg":          "#ffffff",
    "notification_text":        "#212529",
}

DARK_COLORS = {
    "surface":                  "#0a0a0a",
    "surface_dim":              "#121212",
    "surface_bright":           "#161616",
    "surface_container_lowest": "#0e0e0e",
    "surface_container_low":    "#1e1e1e",
    "surface_container":        "#262626",
    "surface_container_high":   "#333333",
    "surface_container_highest":"#404040",
    "primary":                  "#ececeb",
    "on_primary":               "#121212",
    "on_surface":               "#f8f9fa",
    "on_surface_variant":       "#adb5bd",
    "error":                    "#ff8787",
    "error_container":          "#2c0b0e",
    "success":                  "#69db7c",
    "outline":                  "#262626",
    "outline_variant":          "#1a1a1a",
    "notification_bg":          "#2c3036",
    "notification_text":        "#f8f9fa",
}

COLORS = dict(LIGHT_COLORS)
C = COLORS

FONT_HEADLINE = "'Inter', 'Segoe UI', sans-serif"
FONT_BODY = "'Inter', 'Segoe UI', sans-serif"
BORDER_RADIUS_CARD = 16
BORDER_RADIUS_BUTTON = 10
BORDER_RADIUS_INPUT = 10

def set_active_theme(theme_name="light"):
    src = DARK_COLORS if theme_name == "dark" else LIGHT_COLORS
    C.clear()
    C.update(src)

def get_main_window_qss(colors=None):
    if colors is None: colors = C
    is_dark = (colors['surface'] == DARK_COLORS['surface'])
    
    return f"""
        QWidget {{
            font-family: {FONT_BODY};
            font-size: 14px;
            color: {colors['on_surface']};
            background-color: {colors['surface']};
        }}
        
        QMainWindow, QStackedWidget, QScrollArea, QWidget#CentralWidget, QFrame#ContentContainer, QWidget#grid_widget {{
            background-color: {colors['surface']};
            border: none;
        }}

        QLabel, QCheckBox, QRadioButton, QGroupBox, QWidget#queue_container {{
            background-color: transparent;
        }}

        /* Typography */
        QLabel#PageTitle {{ font-size: 32px; font-weight: 800; color: {colors['on_surface']}; }}
        QLabel#SubtitleLabel {{ font-size: 15px; color: {colors['on_surface_variant']}; }}
        QLabel#SectionTitle {{ font-weight: 800; font-size: 10px; color: {colors['primary']}; letter-spacing: 1.5px; text-transform: uppercase; }}
        
        QLabel#StatusLabel {{ font-size: 11px; font-weight: 800; color: {colors['primary']}; }}
        QLabel#StatusLabel[state="success"] {{ color: {colors['success']}; }}
        QLabel#StatusLabel[state="error"] {{ color: {colors['error']}; }}
        QLabel#StatusLabel[state="active"] {{ color: {colors['primary']}; }}

        /* Input / SpinBox */
        QLineEdit, QSpinBox, QDoubleSpinBox {{
            background-color: {colors['surface_container_low']};
            border: none;
            border-radius: {BORDER_RADIUS_INPUT}px;
            padding: 10px 16px;
            color: {colors['on_surface']} !important;
        }}
        
        QSpinBox::up-button, QSpinBox::down-button {{ 
            background-color: {colors['surface_container_high'] if is_dark else colors['surface_dim']}; 
            width: 24px; 
            border: none;
        }}
        QSpinBox::up-button {{ border-top-right-radius: {BORDER_RADIUS_INPUT}px; }}
        QSpinBox::down-button {{ border-bottom-right-radius: {BORDER_RADIUS_INPUT}px; }}
        
        QSpinBox::up-arrow {{ image: none; border-left: 4px solid transparent; border-right: 4px solid transparent; border-bottom: 4px solid {colors['on_surface']}; }}
        QSpinBox::down-arrow {{ image: none; border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 4px solid {colors['on_surface']}; }}

        /* ComboBox - Fully Custom Zen Style */
        QComboBox {{
            background-color: {colors['surface_container_low']};
            border: none;
            border-radius: {BORDER_RADIUS_INPUT}px;
            padding: 10px 16px;
            color: {colors['on_surface']};
            combobox-popup: 0; /* Important for non-native look */
        }}
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {colors['on_surface']};
            margin-right: 12px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {colors['surface_container_low']};
            color: {colors['on_surface']};
            border: 1px solid {colors['outline_variant']};
            border-radius: 8px;
            selection-background-color: {colors['surface_container_highest']};
            selection-color: {colors['on_surface']};
            outline: none;
        }}
        QComboBox QListView {{
            background-color: {colors['surface_container_low']};
            color: {colors['on_surface']};
            border: 1px solid {colors['outline_variant']};
            border-radius: 8px;
        }}
        QComboBox QAbstractItemView::item {{
            padding: 12px;
        }}

        /* Cards */
        QFrame#BentoCard, QFrame#VideoCard, QFrame#ScannerVideoCard, QFrame#QueueItem, QFrame#FolderCard {{
            background-color: {colors['surface_bright'] if is_dark else colors['surface_container_lowest']};
            border: none;
            border-radius: {BORDER_RADIUS_CARD}px;
        }}
        
        QFrame#CardThumb {{
            background-color: {colors['surface_container_low']};
            border-radius: 0px;
        }}
        
        QFrame#StatBox {{
            background-color: {colors['surface_container_low']};
            border-radius: 12px;
            border: none;
        }}
        
        QLabel#GeoBanner {{
            border-radius: 8px;
            font-weight: 800;
            font-size: 10px;
            letter-spacing: 1px;
            padding: 6px 12px;
        }}
        QLabel#GeoBanner[state="error"] {{
            background-color: {colors['error_container']};
            color: {colors['error']};
        }}
        QLabel#GeoBanner[state="success"] {{
            background-color: {colors['surface_container_low']};
            color: {colors['success']};
        }}

        /* Checkbox */
        QCheckBox::indicator {{
            width: 20px; height: 20px; border-radius: 6px;
            border: 2px solid {colors['outline']};
            background: {colors['surface_bright']};
        }}
        QCheckBox::indicator:checked {{
            background: {colors['primary']};
            border-color: {colors['primary']};
        }}

        /* Buttons */
        QPushButton {{
            background-color: {colors['surface_container_low']};
            border: none;
            border-radius: {BORDER_RADIUS_BUTTON}px;
            padding: 10px 20px;
            color: {colors['on_surface']};
            font-weight: 700;
        }}
        QPushButton:hover {{ background-color: {colors['surface_container_high']}; }}
        QPushButton#ActionButton {{ background-color: {colors['primary']}; color: {colors['on_primary']}; border: none; font-weight: 800; }}

        /* Progress Bar */
        QProgressBar {{ background-color: {colors['surface_container_low']}; border-radius: 6px; text-align: center; color: transparent; height: 8px; border: none; }}
        QProgressBar::chunk {{ background-color: {colors['primary']}; border-radius: 6px; }}
    """

def get_navbar_qss(colors=None):
    if colors is None: colors = C
    return f"QFrame#Sidebar {{ background-color: {colors['surface_dim']}; border: none; }}"

def get_navbar_button_qss(active=False, colors=None):
    if colors is None: colors = C
    if active:
        return f"QPushButton {{ background-color: {colors['surface_container_low']}; color: {colors['on_surface']}; border-left: 4px solid {colors['on_surface']}; padding: 14px 16px; text-align: left; border-radius: 0; font-weight: 800; }}"
    else:
        return f"QPushButton {{ background: transparent; color: {colors['on_surface_variant']}; border: none; padding: 14px 16px 14px 24px; text-align: left; font-weight: 600; }} QPushButton:hover {{ background-color: {colors['surface_container_low']}; color: {colors['on_surface']}; }}"

def action_btn_style(colors=None):
    if colors is None: colors = C
    return f"QPushButton {{ background-color: {colors['primary']}; color: {colors['on_primary']}; border: none; border-radius: {BORDER_RADIUS_BUTTON}px; font-weight: 800; }}"

def danger_btn_style(colors=None):
    if colors is None: colors = C
    return f"QPushButton {{ background: transparent; color: {colors['error']}; border: none; font-weight: 800; }}"
