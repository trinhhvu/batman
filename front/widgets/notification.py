
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve
from PyQt5.QtGui import QColor

from front.design import COLORS as C, FONT_HEADLINE

class NotificationToast(QFrame):
    """An ultra-minimalist floating notification toast."""

    def __init__(self, title, message, parent=None, duration=4000):
        super().__init__(parent)
        self.duration = duration
        self._build_ui(title, message)
        
        self.setFixedWidth(280)
        self.adjustSize()
        
        # Smooth shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.fade_out)
        self.timer.start(self.duration)

    def _build_ui(self, title, message):
        # Ultra-minimalist: just background, no borders
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {C['notification_bg']};
                border-radius: 10px;
                border: none;
            }}
            QLabel {{
                background: transparent;
                border: none;
                color: {C['notification_text']};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(2)
        
        # Message is the primary info (e.g. IP)
        # If message contains newlines, we split it for hierarchy
        lines = message.split('\n')
        
        primary_text = lines[0]
        primary_label = QLabel(primary_text)
        primary_label.setStyleSheet(f"font-weight: 800; font-size: 15px; font-family: {FONT_HEADLINE};")
        layout.addWidget(primary_label)
        
        if len(lines) > 1:
            secondary_text = lines[1]
            secondary_label = QLabel(secondary_text)
            secondary_label.setStyleSheet(f"font-weight: 500; font-size: 11px; color: {C['on_surface_variant']};")
            layout.addWidget(secondary_label)

    def show_animated(self):
        parent_rect = self.parent().rect()
        target_x = parent_rect.width() - self.width() - 24
        target_y = 24
        
        self.move(parent_rect.width(), target_y)
        self.show()
        
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(400)
        self.anim.setStartValue(QPoint(parent_rect.width(), target_y))
        self.anim.setEndValue(QPoint(target_x, target_y))
        self.anim.setEasingCurve(QEasingCurve.OutExpo)
        self.anim.start()

    def fade_out(self):
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(300)
        self.anim.setEndValue(QPoint(self.parent().width(), self.y()))
        self.anim.setEasingCurve(QEasingCurve.InExpo)
        self.anim.finished.connect(self.close)
        self.anim.start()

def show_notification(parent, title, message, duration=4000):
    toast = NotificationToast(title, message, parent, duration)
    toast.show_animated()
    return toast
