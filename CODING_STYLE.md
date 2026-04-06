# CODING STYLE — TRACK Professional v3
# ========================================
# This document defines the coding conventions for the entire TRACK project.
# All contributors (human and AI) MUST follow these rules precisely.

## Project Structure

```
TRACK/
├── main.py              # Entry point – launches TrackerApp
├── gui.py               # Main window orchestrator (Sidebar + QStackedWidget)
├── design.py            # SINGLE SOURCE OF TRUTH for all colors, fonts, QSS
├── engine.py            # yt-dlp download engine (single video)
├── tracker.py           # Backend: auth, channel scan, batch download
├── utils.py             # Cross-platform ffmpeg utilities
├── config.json          # Persistent app configuration
├── history.json         # Download history
├── ffmpeg.exe           # Bundled ffmpeg (Windows)
├── assets/
│   └── icon.png         # App icon
├── pages/
│   ├── __init__.py
│   ├── analyze_page.py  # Tab 1: Single video analytics (bento cards)
│   ├── download_page.py # Tab 2: Queue-based video downloader
│   └── scanner_page.py  # Tab 3: Channel scanner + batch download
├── widgets/
│   ├── __init__.py
│   └── sidebar.py       # Left navigation sidebar
├── app_builder/
│   ├── windows/
│   │   └── build_win.bat
│   └── macos/
│       └── build_mac.sh
└── requirements.txt
```

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

1. **NEVER** hardcode colors or font names in page files — always import from `design.py`.
2. Use `COLORS` dict keys: `primary`, `secondary`, `error`, `surface_container_*`, etc.
3. Use `FONT_HEADLINE` for headers, `FONT_BODY` for text, `FONT_MONO` for code/logs.
4. Use `BORDER_RADIUS_CARD` for card widgets, `BORDER_RADIUS_BUTTON` for buttons.
5. Use `get_main_window_qss()` on the top-level window/application.
6. Use `get_sidebar_qss()` and `get_sidebar_button_qss()` for sidebar styling.

## Widget Architecture

- **Pages** are standalone `QWidget` subclasses in `pages/`. Each page manages its own
  layout, signals, and state. They are loaded into `QStackedWidget` by `gui.py`.
- **Widgets** are reusable UI components in `widgets/`. They emit signals for communication.
- **Inter-page communication** goes through `gui.py` using signal/slot connections.
  Pages never reference each other directly.

## Code Style

- Private methods: prefix with `_` (e.g. `_build_ui`, `_on_scan_done`).
- Prefix UI construction methods with `_build_`.
- Prefix signal callbacks with `_on_`.
- Prefix action triggers with `_run_` or `_start_`.
- Use type hints for function signatures and class attributes.
- Use docstrings on all classes and public methods.
- Avoid raw threads for simple tasks; prefer `QRunnable` + `QThreadPool`.
- Keep imports organized: stdlib → PyQt5 → third-party → local.

## Build System

- **Windows**: Run `app_builder/windows/build_win.bat` from the `app_builder/windows/` dir.
- **macOS**: Run `app_builder/macos/build_mac.sh` from the `app_builder/macos/` dir.
- Both scripts use PyInstaller with `--onefile --windowed`.
- ffmpeg is bundled automatically (Windows: `ffmpeg.exe` in root, macOS: from `which ffmpeg`).
- Config, assets, pages, and widgets are bundled as data files.

## Configuration

- App config is stored in `config.json` at the project root.
- Download path is persisted in `config.json` under `"download_folder"`.
- API keys and access tokens are also stored in `config.json`.
- On startup, pages restore their state from `config.json`.
