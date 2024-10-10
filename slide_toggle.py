from PySide6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve, Property, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from PySide6.QtWidgets import QWidget


class SlideToggle(QWidget):
    toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._toggle_width = 60
        self._toggle_height = 30
        self.setFixedSize(self._toggle_width, self._toggle_height)
        self._is_checked = False
        self._handle_position = 4
        self._animation = QPropertyAnimation(self, b"handle_position")
        self._animation.setEasingCurve(QEasingCurve.InOutCubic)
        self._animation.setDuration(200)

    @Property(float)
    def handle_position(self):
        return self._handle_position

    @handle_position.setter
    def handle_position(self, pos):
        self._handle_position = pos
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_checked = not self._is_checked
            self._animation.setStartValue(self._handle_position)
            self._animation.setEndValue(34 if self._is_checked else 4)
            self._animation.start()
            self.toggled.emit(self._is_checked)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background
        painter.setPen(Qt.NoPen)
        if self._is_checked:
            painter.setBrush(QColor(0, 255, 0))
        else:
            painter.setBrush(QColor(200, 200, 200))
        painter.drawRoundedRect(0, 0, self._toggle_width, self._toggle_height, 15, 15)

        # Draw handle
        painter.setPen(QPen(Qt.white, 1))
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(QRect(int(self._handle_position), 4, 22, 22))

        # Draw ON/OFF text
        painter.setFont(QFont("Arial", 8))
        painter.setPen(Qt.white)
        if self._is_checked:
            painter.drawText(QRect(4, 0, 26, self._toggle_height), Qt.AlignCenter, "ON")
        else:
            painter.drawText(QRect(30, 0, 26, self._toggle_height), Qt.AlignCenter, "OFF")

    def isChecked(self):
        return self._is_checked

    def setChecked(self, checked):
        if self._is_checked != checked:
            self._is_checked = checked
            self._handle_position = 34 if checked else 4
            self.update()
            self.toggled.emit(self._is_checked)
