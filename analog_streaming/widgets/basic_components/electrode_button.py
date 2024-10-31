from enum import auto, Enum
from typing import Optional

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QBrush, QPainter, QPen, QColor
from PySide6.QtWidgets import QPushButton, QWidget

class ElectrodeShape(Enum):
    """
    Defines the possible shapes for electrode buttons.
    
    Attributes:
        circle: Circular electrode shape
        rectangle: Rectangular electrode shape
    """
    circle = auto()
    rectangle = auto()


class ElectrodeButton(QPushButton):
    """
    A custom button widget representing an electrode in a stimulation array.
    
    This class extends QPushButton to create specialized electrode buttons that can be either circular or rectangular and change color when selected.
    
    Attributes:
        SIZE (int): Fixed size dimension for the button in pixels
        DEFAULT_COLOR (Qt.GlobalColor): Color used when button is not selected
        SELECTED_COLOR (QColor): Color used when button is selected
        channel_id (int): Unique identifier for the electrode
        shape_type (ElectrodeShape): Visual shape of the electrode
    """
    SIZE: int = 50
    DEFAULT_COLOR: Qt.GlobalColor = Qt.white
    SELECTED_COLOR: QColor = QColor(89, 229, 75)

    def __init__(self,
                 channel_id: int,
                 shape_type: ElectrodeShape = ElectrodeShape.circle,
                 parent: Optional[QWidget] = None) -> None:
        """
        Initialize the electrode button with specified properties.

        Args:
            channel_id: Unique identifier for this electrode
            shape_type: Visual shape to use for this electrode
            parent: Parent widget in the Qt widget hierarchy
        """
        super().__init__(parent)

        self.channel_id = channel_id
        self.shape_type = shape_type
        self.setCheckable(True)
        self.setFixedSize(self.SIZE, self.SIZE)

    def paintEvent(self, event):
        """
        Custom paint event handler for rendering the electrode button.
        
        Coordinates the painting process by setting up the painter and delegating to specialized methods for colors, shapes, and text rendering. Overrides superclass's paintEvent method.

        Args:
            event: The paint event containing details about the paint request
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        base_shape = QRect(5, 5, 40, 40)
        self._set_painter_colors(painter)
        self._draw_electrode_shape(painter, base_shape)
        self._add_channel_id(painter, base_shape)

    def _set_painter_colors(self, painter: QPainter) -> None:
        """
        Configure the painter's colors based on button state.
        
        Sets up the pen for outline drawing and the brush for fill color,
        taking into account whether the button is currently selected.
        
        Args:
            painter: The QPainter instance to configure
        """
        painter.setPen(QPen(Qt.black, 2))
        color = self.SELECTED_COLOR if self.isChecked() else self.DEFAULT_COLOR
        painter.setBrush(QBrush(color))

    def _draw_electrode_shape(self, painter: QPainter, shape: QRect) -> None:
        """
        Draw the electrode shape and channel ID.
        
        Renders either a circular or rectangular shape and adds the channel ID
        text in the center.
        
        Args:
            painter: The QPainter instance to use for drawing
            shape: The QRect instance on which to draw
        """
        if self.shape_type == ElectrodeShape.rectangle:
            painter.drawRect(shape)
        else:
            painter.drawEllipse(shape)
    
    def _add_channel_id(self, painter: QPainter, shape: QRect) -> None:
        """
        Add the channel identifier text and center it.

        Args:
            painter: The QPainter instance to use for drawing
            shape: The QRect instance on which to draw
        """
        text = "-" if self.channel_id == 0 else str(self.channel_id)
        painter.drawText(shape, Qt.AlignCenter, text)
