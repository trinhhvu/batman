
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect, QPropertyAnimation, pyqtProperty, pyqtSignal, QEasingCurve
from PyQt5.QtGui import QPainter, QColor
from front.design import COLORS as C

class ModernToggle(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 28)
        self.setCursor(Qt.PointingHandCursor)
        
        self._is_on = False
        self._circle_pos = 2
        self._anim = QPropertyAnimation(self, b"circle_pos")
        self._anim.setDuration(250)
        self._anim.setEasingCurve(QEasingCurve.OutExpo)

    @pyqtProperty(float)
    def circle_pos(self):
        return self._circle_pos

    @circle_pos.setter
    def circle_pos(self, pos):
        self._circle_pos = pos
        self.update()

    def set_checked(self, checked, animate=True):
        if self._is_on == checked: 
            # Still update position in case it was initialized incorrectly
            end_val = self.width() - 26 if self._is_on else 2
            self.circle_pos = end_val
            return
            
        self._is_on = checked
        end_val = self.width() - 26 if self._is_on else 2
        
        if animate:
            self._anim.stop()
            self._anim.setEndValue(end_val)
            self._anim.start()
        else:
            self.circle_pos = end_val
        
        self.toggled.emit(self._is_on)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.set_checked(not self._is_on)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        
        is_dark = C['surface'] != "#f1f3f5" # Basic check for dark mode
        
        # Colors based on state and theme
        if self._is_on:
            bg = QColor("#34C759") # iOS Green
        else:
            bg = QColor("#39393D") if is_dark else QColor("#E9E9EA")
            
        circle = QColor("#FFFFFF")
        
        # Draw track
        p.setBrush(bg)
        p.drawRoundedRect(0, 0, self.width(), self.height(), self.height()/2, self.height()/2)
        
        # Draw thumb
        p.setBrush(circle)
        p.drawEllipse(QRect(int(self._circle_pos), 2, 24, 24))
