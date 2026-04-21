# 🦇 BATMAN V3 — TRACK (Unified Architecture)

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)
![Architecture](https://img.shields.io/badge/Architecture-Front%2FBack-orange)

## 🚀 Giới thiệu
**BATMAN V3** là phiên bản mới nhất của ứng dụng **TRACK**, một công cụ mạnh mẽ chuyên dùng để phân tích (Analyze), quét (Scan) và tải xuống (Download) dữ liệu từ Dailymotion và các nền tảng video khác.

⚠️ **Lưu ý:** Đây là branch `batman` với cấu trúc code mới, tách biệt hoàn toàn giữa giao diện (UI) và logic (Business Logic).

---

## 🏗️ Cấu trúc dự án (Architecture)

Ứng dụng được thiết kế theo mô hình tách biệt để dễ dàng bảo trì và mở rộng:

- **`front/`**: Chứa toàn bộ mã nguồn giao diện (PyQt5).
  - `pages/`: Các trang chức năng chính (Analyze, Download, Scanner, Research).
  - `widgets/`: Các thành phần UI dùng chung (Sidebar, v.v.).
  - `design.py`: Hệ thống màu sắc và QSS (Style Sheet).
- **`back/`**: Chứa toàn bộ logic xử lý, API và background workers.
  - `engine.py`: Bộ máy xử lý chính.
  - `api_client.py`: Giao thức kết nối Dailymotion.
  - `workers.py`: Multi-threading cho các tác vụ nặng.
- **`app_builder_2/`**: Các script build cho Windows, macOS và Linux.

---

## 🛠️ Cài đặt & Chạy ứng dụng

### 1. Yêu cầu hệ thống
- Python 3.10+
- FFmpeg (đã có sẵn `ffmpeg.exe` cho Windows trong repo).

### 2. Cài đặt môi trường
Mở terminal tại thư mục gốc và chạy:

```bash
# Tạo môi trường ảo
python -m venv .venv

# Kích hoạt môi trường ảo
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt
```

### 3. Chạy ứng dụng
```bash
python main.py
```

---

## 📦 Đóng gói ứng dụng (Build App)

Để tạo file `.exe` hoặc `.app` chạy trực tiếp mà không cần cài Python, truy cập thư mục `app_builder_2` và chọn đúng OS của bạn:

- **Windows:** Chạy `app_builder_2\windows\build_win.bat`
- **macOS:** Chạy `app_builder_2/macos/build_mac.sh`
- **Linux:** Chạy `app_builder_2/linux/build_linux.sh`

File kết quả sẽ nằm trong thư mục `dist/`.

---

## 📝 Nhật ký thay đổi (Changelog)
- **v3.0**: Tái cấu trúc thư mục `front/` và `back/`.
- **v3.1**: Cập nhật `app_builder_2` hỗ trợ build đa nền tảng với cấu trúc mới.
- **v3.2**: Thêm `README.md` chính thức cho nhánh `batman`.

---
*Phát triển bởi Batman Team.*
