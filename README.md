# TRACK (Unified Architecture)

Trạng thái: Active
Nền tảng: Windows | macOS | Linux
Kiến trúc: Front/Back

## Giới thiệu
TRACK là công cụ chuyên dùng để phân tích (Analyze), quét (Scan) và tải xuống (Download) dữ liệu từ Dailymotion và các nền tảng video khác.

Lưu ý: Đây là branch với cấu trúc code mới, tách biệt hoàn toàn giữa giao diện (UI) và logic (Business Logic).

## Cấu trúc dự án (Architecture)

Ứng dụng được thiết kế theo mô hình tách biệt để dễ dàng bảo trì và mở rộng:

- `front/`: Chứa toàn bộ mã nguồn giao diện (PyQt5).
  - `pages/`: Các trang chức năng chính (Analyze, Download, Scanner, Research).
  - `widgets/`: Các thành phần UI dùng chung.
  - `design.py`: Hệ thống màu sắc và QSS (Style Sheet).
- `back/`: Chứa toàn bộ logic xử lý, API và background workers.
  - `engine.py`: Bộ máy xử lý chính.
  - `api_client.py`: Giao thức kết nối Dailymotion.
  - `workers.py`: Multi-threading cho các tác vụ nặng.
- `app_builder_2/`: Các script build cho Windows, macOS và Linux.

## Cài đặt & Chạy ứng dụng

### 1. Yêu cầu hệ thống
- Python 3.10+
- FFmpeg
  - macOS: Chạy lệnh `brew install ffmpeg`
  - Windows: Đã có sẵn file `ffmpeg.exe` trong repo.

### 2. Cài đặt môi trường
Mở terminal tại thư mục gốc và chạy các lệnh sau:

```bash
# Tạo môi trường ảo (Dùng python3 cho macOS)
python3 -m venv .venv

# Kích hoạt môi trường ảo
# macOS / Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate

# Cài đặt thư viện
pip3 install -r requirements.txt
```

### 3. Chạy ứng dụng
```bash
python3 main.py
```

## Đóng gói ứng dụng (Build App)

Để tạo file chạy trực tiếp mà không cần cài Python, chạy các script sau:

- macOS: `bash app_builder_2/macos/build_mac.sh`
- Windows: `app_builder_2\windows\build_win.bat`
- Linux: `bash app_builder_2/linux/build_linux.sh`

File kết quả sẽ nằm trong thư mục `dist/`.

## Nhật ký thay đổi (Changelog)
- v3.0: Tái cấu trúc thư mục `front/` và `back/`.
- v3.1: Cập nhật `app_builder_2` hỗ trợ build đa nền tảng với cấu trúc mới.
