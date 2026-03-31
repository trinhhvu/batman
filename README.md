# 🦇 Batman v2 — The Ultimate Suite

A unified Dailymotion **Downloader + Analytics** desktop application built with Python and PyQt5.

---

## Features

### ⬇ Video Downloader
- Paste Dailymotion URL → Analyze → Preview thumbnail & title
- Select quality (Best / 1080p / 720p / 480p)
- Queue management: add, reorder, remove items
- Multi-threaded downloads with real-time progress bar
- FFmpeg integration for high-quality video/audio merging

### 📊 Real-time Analytics
- Scan any Dailymotion video for live stats
- View count breakdown: Total / 24h / 1h
- Geoblock detection
- Batch import from `.txt` or `.html` files
- Export reports to Excel (`.xlsx`)

---

## Requirements

- Python 3.10+
- FFmpeg (see installation below)

### Install dependencies

```bash
pip install -r requirements.txt
```

### Install FFmpeg

**Windows:**
Download `ffmpeg.exe` from [ffmpeg.org](https://ffmpeg.org/download.html) and place it in the project root folder.

**macOS:**
```bash
brew install ffmpeg
```

---

## Run

```bash
python main.py
```

---

## Build

### Windows
```bash
cd app_builder/windows
build_win.bat
```

### macOS
```bash
cd app_builder/macos
bash build_mac.sh
```

---

## Project Structure

```
Batman v2/
├── main.py              # Entry point
├── app.py               # Main window + sidebar navigation
├── design.py            # Unified design system (colors, fonts, QSS)
├── engine.py            # Download backend (yt-dlp)
├── utils.py             # Cross-platform FFmpeg utility
├── requirements.txt     # Dependencies
├── CODING_STYLE.md      # AI coding style guide
├── assets/
│   └── icon.png         # Batman icon
├── widgets/
│   └── sidebar.py       # Sidebar navigation widget
├── pages/
│   ├── download_page.py # Downloader UI
│   └── analytics_page.py# Analytics UI
└── app_builder/
    ├── windows/
    │   └── build_win.bat
    └── macos/
        └── build_mac.sh
```

---

## Tech Stack

| Component | Technology |
|---|---|
| GUI | PyQt5 |
| Download Engine | yt-dlp |
| Media Processing | FFmpeg |
| Data Export | pandas + openpyxl |
| Design System | Custom QSS (Material 3 Dark) |

---

*Built with 🦇 by Batman.*
