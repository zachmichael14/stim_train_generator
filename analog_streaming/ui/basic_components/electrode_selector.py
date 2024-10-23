from enum import Enum
from PySide6.QtCore import QRect, QSize, Qt, Signal, Slot
from PySide6.QtGui import QBrush, QPainter, QPen, QColor
from PySide6.QtWidgets import (
    QGridLayout, QGroupBox, QPushButton, QVBoxLayout, QWidget,
    QComboBox
)

class ElectrodeMode(Enum):
    SINGLE = "Single Electrode"
    MULTI = "Multi Electrode"

class ElectrodeShape(Enum):
    circle = 1
    rectangle = 2

class ElectrodeButton(QPushButton):
    SIZE = 50
    DEFAULT_COLOR = Qt.white
    SELECTED_COLOR = QColor(89, 229, 75)  # green

    def __init__(self, channel_id: int, shape_type: ElectrodeShape = ElectrodeShape.circle, parent=None):
        super().__init__(parent)
        self.channel_id = channel_id
        self.shape_type = shape_type
        self.setCheckable(True)
        self.setFixedSize(self.SIZE, self.SIZE)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self._set_painter_colors(painter)
        self._draw_electrode_shape(painter)
    
    def _set_painter_colors(self, painter: QPainter):
        painter.setPen(QPen(Qt.black, 2))
        if self.isChecked():
            painter.setBrush(QBrush(self.SELECTED_COLOR))
        else:
            painter.setBrush(QBrush(self.DEFAULT_COLOR))

    def _draw_electrode_shape(self, painter: QPainter):
        rect = QRect(5, 5, 40, 40)
        if self.shape_type == ElectrodeShape.rectangle:
            painter.drawRect(rect)
        else:
            painter.drawEllipse(rect)
        # Display "-" for single electrode mode, otherwise show channel_id
        text = "-" if self.channel_id == 0 else str(self.channel_id)
        painter.drawText(rect, Qt.AlignCenter, text)

class SingleElectrodeWidget(QWidget):
    signal_electrode_selected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout()
        
        # Create a single, centered, selected electrode
        self.electrode = ElectrodeButton(0, ElectrodeShape.circle)
        self.electrode.setChecked(True)
        self.electrode.setEnabled(False)  # Make it non-interactive
        
        layout.addWidget(self.electrode, 0, 0, Qt.AlignCenter)
        self.setLayout(layout)

class MultiElectrodeWidget(QWidget):
    signal_electrode_selected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_electrodes()

        # Enable channel 1 by default
        self.signal_electrode_selected.emit(1)

    def setup_electrodes(self):
        # channel id, shape, row, col
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

        grid_layout = QGridLayout()
        for channel_id, shape_type, row, col in shapes:
            button = ElectrodeButton(channel_id, shape_type)
            if channel_id == 1:
                button.setChecked(True)
            button.toggled.connect(self.toggle_callback)
            grid_layout.addWidget(button, row, col)


        self.setLayout(grid_layout)

    @Slot(bool)
    def toggle_callback(self, checked):
        sender = self.sender()
        if checked:
            for button in self.findChildren(ElectrodeButton):
                if button != sender:
                    button.setChecked(False)
            self.signal_electrode_selected.emit(sender.channel_id)

class ElectrodeSelectorWidget(QWidget):
    signal_electrode_selected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # Create group box
        self.group_box = QGroupBox("Cathode Selector")
        group_box_layout = QVBoxLayout()

        # Add mode selector dropdown inside the group box
        self.mode_selector = QComboBox()
        self.mode_selector.addItems([mode.value for mode in ElectrodeMode])
        self.mode_selector.currentTextChanged.connect(self.mode_changed)
        group_box_layout.addWidget(self.mode_selector)

        # Create container widget for electrode layouts
        self.electrode_container = QWidget()
        self.electrode_layout = QVBoxLayout(self.electrode_container)
        
        # Create both widget types
        self.single_widget = SingleElectrodeWidget()
        self.multi_widget = MultiElectrodeWidget()
        
        # Connect signals
        self.single_widget.signal_electrode_selected.connect(self.signal_electrode_selected)
        self.multi_widget.signal_electrode_selected.connect(self.signal_electrode_selected)

        # Add electrode container to group box layout
        group_box_layout.addWidget(self.electrode_container)
        self.group_box.setLayout(group_box_layout)

        # Add group box to main layout
        main_layout.addWidget(self.group_box)
        self.setLayout(main_layout)

        # Set initial mode
        self.mode_changed(ElectrodeMode.SINGLE.value)

    @Slot(str)
    def mode_changed(self, mode_text):
        # Clear the current electrode layout
        while self.electrode_layout.count():
            item = self.electrode_layout.takeAt(0)
            if item.widget():
                item.widget().hide()

        # Add appropriate widget based on mode
        if mode_text == ElectrodeMode.SINGLE.value:
            self.electrode_layout.addWidget(self.single_widget)
            self.single_widget.show()
        else:
            self.electrode_layout.addWidget(self.multi_widget)
            self.multi_widget.show()

    def sizeHint(self):
        return QSize(50, 50)