# app_builder_2 — Hướng dẫn Build TRACK

Thư mục này chứa các script build **để tạo ra app chạy thẳng** (không có installer), đã cập nhật đúng với cấu trúc `front/` + `back/` mới.

---

## 📁 Cấu trúc

```
app_builder_2/
├── windows/
│   └── build_win.bat       ← Build ra BATMAN V3.exe
├── macos/
│   └── build_mac.sh        ← Build ra BATMAN V3.app
└── linux/
    └── build_linux.sh      ← Build ra binary BATMAN V3
```

**Output**: toàn bộ file app được xuất vào `TRACK/dist/`

---

## 🪟 Windows

```bat
cd app_builder_2\windows
build_win.bat
```

- Yêu cầu: `PyInstaller` đã cài trong `.venv` (`pip install pyinstaller`)
- Output: `dist\BATMAN V3.exe` — chạy thẳng, không cần cài đặt

---

## 🍎 macOS

```bash
cd app_builder_2/macos
chmod +x build_mac.sh
./build_mac.sh
```

- Yêu cầu: `brew install ffmpeg` và `pip3 install pyinstaller`
- Output: `dist/BATMAN V3.app` — kéo vào Applications hoặc double-click

---

## 🐧 Linux

```bash
cd app_builder_2/linux
chmod +x build_linux.sh
./build_linux.sh
```

- Yêu cầu: `sudo apt install ffmpeg && pip3 install pyinstaller`
- Output: `dist/BATMAN V3` — binary có quyền execute, chạy thẳng

---

## 🔄 So sánh với app_builder (cũ)

| | `app_builder` (cũ) | `app_builder_2` (mới) |
|---|---|---|
| Cấu trúc module | `pages/`, `widgets/` (root) | `front/`, `back/` |
| Output | Installer (.iss, DMG) | App chạy thẳng |
| Hidden imports | Outdated | Đầy đủ front + back |
| `ffmpeg` path | Hardcoded Windows | Auto-detect mọi OS |
