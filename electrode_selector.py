from enum import Enum

from PySide6.QtCore import QRect, QSize, Qt, Signal, Slot
from PySide6.QtGui import QBrush, QPainter, QPen
from PySide6.QtWidgets import QGridLayout, QPushButton, QWidget 

class ElectrodeShape(Enum):
    circle = 1
    rectangle = 2


class ElectrodeButton(QPushButton):
    SIZE = 50

    def __init__(self, channel_id: int, shape_type: ElectrodeShape = ElectrodeShape.circle, parent=None):
        super().__init__(parent)
        self.channel_id = channel_id
        self.shape_type = shape_type
        self.setCheckable(True)
        self.setFixedSize(self.SIZE, self.SIZE)

    def paintEvent(self, event):
        """Override base class's paintEvent method."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self._set_colors(painter)
        self._draw_shape(painter)
        
    def _set_colors(self, painter: QPainter):
        """Set the electrode's background (i.e., brush) to green if it's
        selected - set it to white otherwise.
        Additionally, set electrode's border and text color (i.e., pen).     
        """ 
        painter.setPen(QPen(Qt.black, 2))

        if self.isChecked():
            painter.setBrush(QBrush(Qt.green))
        else:
            painter.setBrush(QBrush(Qt.white))

    def _draw_shape(self, painter: QPainter):
        """ Draw the electrode as a circle or rectangle.
        Write the channel id inside the electrode.
        """
        rect = QRect(5, 5, 40, 40)

        if self.shape_type == ElectrodeShape.rectangle:
            painter.drawRect(rect)
        else:
            painter.drawEllipse(rect)

        painter.drawText(rect, Qt.AlignCenter, str(self.channel_id))


class ElectrodeSelectorWidget(QWidget):
    signal_shape_selected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        self.setLayout(layout)

        shapes = [
            (1, ElectrodeShape.circle, 0, 1), 
            (2, ElectrodeShape.circle, 0, 2),
            (7, ElectrodeShape.rectangle, 1, 0), 
            (3, ElectrodeShape.circle, 1, 1),
            (4, ElectrodeShape.circle, 1, 2), 
            (8, ElectrodeShape.rectangle, 1, 3),
            (5, ElectrodeShape.circle, 2, 1), 
            (6, ElectrodeShape.circle, 2, 2)
        ]

        for channel_id, shape_type, row, col in shapes:
            button = ElectrodeButton(channel_id, shape_type)
            button.toggled.connect(self.toggle_callback)
            layout.addWidget(button, row, col)

    @Slot(bool)
    def toggle_callback(self, checked):
        sender = self.sender()
        if checked:
            for button in self.findChildren(ElectrodeButton):
                if button != sender:
                    button.setChecked(False)
            self.signal_shape_selected.emit(sender.channel_id)

    def sizeHint(self):
        return QSize(220, 180)
