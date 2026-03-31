# Batman v2 — AI Coding Style Guide
> **Mục đích:** Tài liệu này mô tả toàn bộ quy tắc viết code, đặt tên, tổ chức file, và phong cách thiết kế được sử dụng trong dự án Batman v2. Bất kỳ AI nào tiếp tục dự án này PHẢI đọc và tuân theo tài liệu này.

---

## 1. Triết lý Tổng thể

### 1.1. Nguyên tắc cốt lõi
- **Single Responsibility:** Mỗi file chỉ làm 1 việc duy nhất.
- **Don't Repeat Yourself (DRY):** Tất cả màu sắc, style, hằng số đều tập trung trong `design.py`. **Không được** hardcode màu sắc trực tiếp trong các file khác.
- **Explicit over Implicit:** Mọi phụ thuộc (dependency) và mục đích của file đều được khai báo rõ trong docstring đầu file.
- **Thread-Safe First:** Bất kỳ tác vụ nào chạy nền (download, network) đều phải dùng `pyqtSignal` để cập nhật UI, **không bao giờ** gọi trực tiếp widget từ thread con.

### 1.2. Framework & Library
| Mục đích | Library | Lý do chọn |
|---|---|---|
| GUI | `PyQt5` | Cross-platform (Win + macOS), styling linh hoạt nhất |
| Download | `yt-dlp` | Mạnh nhất cho Dailymotion |
| HTTP | `requests` | Đơn giản, ổn định |
| Image | `Pillow` (PIL) | Xử lý thumbnail |
| Data | `pandas` + `openpyxl` | Export Excel |

---

## 2. Cấu trúc Thư mục

```
DDproject/
├── main.py                 # Entry point duy nhất. Tối đa 15 dòng.
├── app.py                  # Main window + layout + sidebar
├── design.py               # ⭐ SINGLE SOURCE OF TRUTH cho tất cả styling
├── engine.py               # Logic download (yt-dlp). Không có gì liên quan UI.
├── utils.py                # Hàm tiện ích cross-platform (FFmpeg path, etc.)
├── requirements.txt        # Dependencies
├── widgets/
│   ├── __init__.py
│   └── sidebar.py          # Widget tái sử dụng
└── pages/
    ├── __init__.py
    ├── download_page.py    # Trang Downloader
    └── analytics_page.py   # Trang Analytics
```

### Quy tắc thêm file mới:
- **Widget tái sử dụng** (dùng ở nhiều trang) → `widgets/`
- **Trang hiển thị** (gắn vào sidebar) → `pages/`
- **Logic backend** (không UI) → file riêng ở thư mục gốc

---

## 3. Quy tắc Đặt tên (Naming Conventions)

### 3.1. Files & Modules
```
snake_case.py           ✅  download_page.py, video_card.py
CamelCase.py            ❌  DownloadPage.py
```

### 3.2. Classes
```python
class DownloadPage(QWidget):       # ✅ PascalCase, kế thừa rõ ràng
class downloadPage:                # ❌
class Page:                        # ❌ Quá chung chung
```

### 3.3. Methods & Functions
```python
def _build_ui(self):              # ✅ Private method: prefix _
def _on_progress(self, ...):      # ✅ Signal slot: prefix _on_
def refresh_queue_display(self):  # ✅ Public method: snake_case
def RefreshQueue(self):           # ❌ PascalCase
def rqd(self):                    # ❌ Viết tắt không rõ nghĩa
```

### 3.4. Variables
```python
# ✅ Rõ ràng, snake_case
video_data_list = []
is_downloading = False
current_video_info = None

# ❌ Tối nghĩa
vdl = []
flag = False
info = None
```

### 3.5. PyQt5 Widget instances
```python
# ✅ Prefix bằng loại widget khi cần phân biệt
self.url_input = QLineEdit()
self.scan_btn = QPushButton()
self.progress_bar = QProgressBar()
self.queue_layout = QVBoxLayout()

# ❌ Quá chung
self.input = QLineEdit()
self.btn = QPushButton()
```

### 3.6. Constants & Design Tokens
```python
# design.py — CẶP VIẾT HOA
SIDEBAR_WIDTH = 240
BORDER_RADIUS_CARD = 20
FONT_HEADLINE = "Manrope"

# Shorthand alias cho dict
C = COLORS  # Dùng khi cần C['primary'] thay vì COLORS['primary']
```

### 3.7. PyQt5 ObjectName (dùng cho QSS targeting)
```python
btn.setObjectName("ActionButton")    # ✅ PascalCase
btn.setObjectName("action-button")   # ❌ kebab-case
btn.setObjectName("action_button")   # ❌ snake_case
```

---

## 4. Cấu trúc Class (PyQt5 Widget)

Mọi widget đều theo thứ tự này:

```python
class MyWidget(QWidget):
    """
    Docstring ngắn gọn mô tả widget làm gì.
    """

    my_signal = pyqtSignal(str)   # 1. Signals (nếu có)

    def __init__(self, parent=None):
        super().__init__(parent)
        # 2. Khởi tạo state variables
        self.some_data = []
        self.is_active = False

        # 3. Kết nối signals (nếu có)
        self._connect_signals()

        # 4. Build UI
        self._build_ui()

    def _connect_signals(self):   # 5. Signal connections riêng biệt
        self.my_signal.connect(self._on_signal)

    def _build_ui(self):          # 6. UI construction
        # Layout logic ở đây
        pass

    # ── Actions (public) ──       # 7. Public methods
    def refresh(self):
        pass

    # ── Signal slots (private) ── # 8. Signal handlers
    def _on_signal(self, value):
        pass

    # ── Helpers (private) ──      # 9. Helper methods
    def _format_time(self, ts):
        pass
```

---

## 5. Cấu trúc File — Docstring Bắt buộc

**Mọi file Python** đều phải có docstring đầu file theo template này:

```python
"""
ten_file.py — Tiêu đề ngắn gọn
================================
Mô tả chi tiết file này làm gì.
Giải thích logic quan trọng nếu có.

Dependencies: PyQt5, requests, design.py
Used by: app.py (nơi file này được import)
"""
```

> **Lý do:** Khi AI mới tiếp tục dự án, nó có thể đọc docstring và hiểu ngay mà không cần phân tích toàn bộ file.

---

## 6. Design System (design.py)

### 6.1. Nguyên tắc bất biến
- **KHÔNG BAO GIỜ** hardcode màu hex trong các file khác.
- Mọi màu đều phải là `C['ten_mau']` hoặc `COLORS['ten_mau']`.
- Mọi QSS stylesheet phức tạp đều nằm trong hàm `get_*_qss()` trong `design.py`.

### 6.2. Cách dùng đúng
```python
# ✅ Đúng — import từ design.py
from design import COLORS as C, FONT_HEADLINE

label.setStyleSheet(f"color: {C['primary']}; font-family: '{FONT_HEADLINE}';")

# ❌ Sai — hardcode màu
label.setStyleSheet("color: #8cb7fe; font-family: 'Manrope';")
```

### 6.3. Bảng màu chính
| Token | Hex | Dùng cho |
|---|---|---|
| `surface` | `#0d0d1c` | Nền chính của app |
| `surface_container` | `#18182a` | Panel, card nền |
| `surface_container_high` | `#1e1e32` | Hover state |
| `primary` | `#8cb7fe` | Accent xanh dương, nút chính |
| `secondary` | `#b4f2af` | Accent xanh lá, trạng thái success |
| `error` | `#ff716c` | Lỗi, cảnh báo |
| `on_surface` | `#e6e3f9` | Chữ chính |
| `on_surface_variant` | `#aba9be` | Chữ phụ, placeholder |
| `outline_variant` | `#474658` | Đường kẻ mờ, border |

---

## 7. Thread Safety (Quy tắc bắt buộc với PyQt5)

**PyQt5 không cho phép cập nhật UI từ thread con.** Vi phạm quy tắc này gây crash app.

### Pattern bắt buộc: `WorkerSignals`

```python
# ✅ ĐÚNG — Dùng signals
class WorkerSignals(QObject):
    update_progress = pyqtSignal(float, str, str)
    status_text = pyqtSignal(str)
    all_done = pyqtSignal()

class MyPage(QWidget):
    def __init__(self):
        self.signals = WorkerSignals()
        self.signals.status_text.connect(self._on_status)  # kết nối

    def _start_worker(self):
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):  # Chạy trong thread con
        # ... xử lý nặng ...
        self.signals.status_text.emit("Done!")  # ✅ An toàn

    def _on_status(self, text):  # Chạy trên main thread
        self.status_label.setText(text)  # ✅ Cập nhật UI an toàn

# ❌ SAI — Gọi UI trực tiếp từ thread
def _worker(self):
    self.status_label.setText("Done!")  # ❌ Crash!
```

---

## 8. Comment Style

### 8.1. Section separators
```python
# ── Tên Section ──           # Phân tách các nhóm code lớn trong file
```

### 8.2. Inline comments
```python
self.queue_layout.setAlignment(Qt.AlignTop)  # Prevent items from centering vertically
```

### 8.3. TODO / Fix notes
```python
# Logic Fix: Sync total views with daily/hourly data if API lag occurs
data['views_total'] = max(v_total, v_day, v_hour)
```

### 8.4. Warning comments
```python
self._thumb_pixmap = scaled  # prevent GC (garbage collection)
```

---

## 9. PyQt5 Layout Patterns

### 9.1. Cấu trúc layout chuẩn
```python
def _build_ui(self):
    # 1. Tạo root layout gắn vào self
    root = QVBoxLayout(self)
    root.setContentsMargins(30, 20, 30, 20)
    root.setSpacing(20)

    # 2. Tạo widget, thêm vào layout
    header = QLabel("Title")
    header.setFont(QFont(FONT_HEADLINE, 22, QFont.ExtraBold))
    root.addWidget(header)

    # 3. Dùng stretch để đẩy nội dung
    root.addStretch()  # Đẩy nội dung lên trên
```

### 9.2. Scrollable area pattern
```python
scroll = QScrollArea()
scroll.setWidgetResizable(True)

container = QWidget()
container_layout = QVBoxLayout(container)
container_layout.setAlignment(Qt.AlignTop)  # QUAN TRỌNG: tránh items bị giãn

scroll.setWidget(container)
layout.addWidget(scroll, 1)  # stretch=1 để fill không gian còn lại
```

---

## 10. Entry Point Pattern

`main.py` luôn tối giản, chỉ khởi động app:

```python
import sys
from PyQt5.QtWidgets import QApplication
from app import DDProjectApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DDProjectApp()
    window.show()
    sys.exit(app.exec_())
```

---

## 11. Quy tắc cho AI tiếp tục dự án

Nếu bạn là AI đang đọc file này để tiếp tục code, hãy tuân theo:

1. **Đọc `design.py` trước tiên** — đây là nguồn sự thật.
2. **Đọc docstring đầu file** của file bạn cần sửa để hiểu dependencies.
3. **Không thay đổi `engine.py` và `utils.py`** trừ khi có yêu cầu rõ ràng.
4. **Không import customtkinter** — dự án đã chuyển sang PyQt5 hoàn toàn.
5. **Khi thêm màu/style mới**, thêm vào `design.py` trước, sau đó dùng `C['ten_token']`.
6. **Khi thêm trang mới**, tạo file trong `pages/`, thêm vào `QStackedWidget` trong `app.py`, thêm nút vào `sidebar.py`.
7. **Mọi network call hoặc heavy computation** phải chạy trong `threading.Thread` với `daemon=True`.

---

*Tài liệu này được tạo ngày 2026-04-01 bởi AI assistant (Antigravity) cho dự án DDproject.*
