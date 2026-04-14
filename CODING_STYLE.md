# CODING STYLE — TRACK Professional v3
# ========================================
# This document defines the coding conventions for the entire TRACK project.
# All contributors (human and AI) MUST follow these rules precisely.

## Project Structure

```
TRACK/
├── main.py              # Entry point – launches TrackerApp
├── config.json          # Persistent app configuration
├── ffmpeg.exe           # Bundled ffmpeg (Windows)
├── requirements.txt
├── assets/
│   └── icon.png         # App icon
├── front/               # ═══ PURE UI LAYER (PyQt5 only) ═══
│   ├── __init__.py
│   ├── design.py        # SINGLE SOURCE OF TRUTH for colors, fonts, QSS
│   ├── gui.py           # Main window orchestrator (Navbar + QStackedWidget)
│   ├── widgets/
│   │   ├── __init__.py
│   │   └── sidebar.py   # Top navigation bar
│   └── pages/
│       ├── __init__.py
│       ├── analyze_page.py   # Tab 1: Single video analytics (bento cards)
│       ├── download_page.py  # Tab 2: Queue-based video downloader
│       ├── scanner_page.py   # Tab 3: Channel scanner + batch download
│       └── research_page.py  # Tab 4: Research & Trend discovery
├── back/                # ═══ LOGIC LAYER (No UI widgets) ═══
│   ├── __init__.py      # Exports TRACK_ROOT path constant
│   ├── api_client.py    # All Dailymotion Public API HTTP requests
│   ├── config.py        # Centralized config.json read/write
│   ├── engine.py        # yt-dlp download engine (single video)
│   ├── tracker.py       # OAuth, channel scan, batch download
│   ├── utils.py         # Cross-platform ffmpeg utilities
│   └── workers.py       # All QThread/QRunnable background workers
└── app_builder/
    ├── windows/
    │   └── build_win.bat
    ├── macos/
    │   └── build_mac.sh
    └── linux/
```

## Architecture Rules

### FRONT (front/)
- **ONLY** PyQt5 widget imports (`QWidget`, `QLabel`, `QPushButton`, etc.)
- **NEVER** import `requests`, `yt_dlp`, `sqlite3`, or any network/IO library
- Pages emit signals → receive data → display it. That's all.
- All HTTP calls go through `back/api_client.py`
- All background threads go through `back/workers.py`
- All config read/write goes through `back/config.py`

### BACK (back/)
- **NEVER** import `QWidget`, `QLabel`, `QPushButton`, or any UI widget
- **ALLOWED**: `QThread`, `QObject`, `pyqtSignal`, `QRunnable` (for threading only)
- Pure Python logic: HTTP requests, file I/O, yt-dlp, data processing
- `TRACK_ROOT` constant (from `back/__init__.py`) for all path resolution

## Naming Conventions

| Element           | Convention            | Examples                             |
|-------------------|-----------------------|--------------------------------------|
| Files/Modules     | `snake_case.py`       | `analyze_page.py`, `scanner_page.py` |
| Classes           | `PascalCase`          | `TrackerApp`, `VideoCard`            |
| Functions/Methods | `snake_case`          | `set_url_and_analyze()`, `_build_ui()` |
| Constants         | `UPPER_SNAKE_CASE`    | `CONFIG_PATH`, `BORDER_RADIUS_CARD`  |
| Variables         | `snake_case`          | `download_path`, `card_count`        |
| Signals           | `snake_case`          | `page_changed`, `request_download`   |

## Design System Rules

1. **NEVER** hardcode colors or font names in page files — always import from `front/design.py`.
2. Use `COLORS` dict keys: `primary`, `secondary`, `error`, `surface_container_*`, etc.
3. Use `FONT_HEADLINE` for headers, `FONT_BODY` for text, `FONT_MONO` for code/logs.
4. Use `BORDER_RADIUS_CARD` for card widgets, `BORDER_RADIUS_BUTTON` for buttons.
5. Use `get_main_window_qss()` on the top-level window/application.
6. Use `get_navbar_qss()` and `get_navbar_button_qss()` for navigation styling.

## Widget Architecture

- **Pages** are standalone `QWidget` subclasses in `front/pages/`. Each page manages its own
  layout, signals, and state. They are loaded into `QStackedWidget` by `front/gui.py`.
- **Widgets** are reusable UI components in `front/widgets/`. They emit signals for communication.
- **Inter-page communication** goes through `front/gui.py` using signal/slot connections.
  Pages never reference each other directly.
- **Workers** live in `back/workers.py`. Pages instantiate workers, connect to their signals,
  and display the results.

## Code Style

- Private methods: prefix with `_` (e.g. `_build_ui`, `_on_scan_done`).
- Prefix UI construction methods with `_build_`.
- Prefix signal callbacks with `_on_`.
- Prefix action triggers with `_run_` or `_start_`.
- Use type hints for function signatures and class attributes.
- Use docstrings on all classes and public methods.
- Keep imports organized: stdlib → PyQt5 → back.* → front.*

## Import Examples

```python
# In front/pages/research_page.py (UI file):
from front.design import COLORS as C, FONT_HEADLINE     # ✅ OK
from back.workers import ResearchWorker                   # ✅ OK (QThread)
import requests                                           # ❌ FORBIDDEN

# In back/api_client.py (Logic file):
import requests                                           # ✅ OK
from PyQt5.QtWidgets import QLabel                        # ❌ FORBIDDEN
```

## Build System

- **Windows**: Run `app_builder/windows/build_win.bat` from the `app_builder/windows/` dir.
- **macOS**: Run `app_builder/macos/build_mac.sh` from the `app_builder/macos/` dir.
- Both scripts use PyInstaller with `--onefile --windowed`.

## Configuration

- App config is stored in `config.json` at the project root.
- All config access goes through `back/config.py` — never read config.json directly in UI.
- Download path is persisted under `"download_folder"`.
- API keys and access tokens are also stored in `config.json`.
