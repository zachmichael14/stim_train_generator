from enum import Enum, auto
from typing import Optional

from PySide6.QtCore import QRect, QSize, Qt, Signal, Slot
from PySide6.QtGui import QBrush, QPainter, QPen, QColor
from PySide6.QtWidgets import (
    QGridLayout, QGroupBox, QPushButton, QVBoxLayout, QWidget,
    QComboBox
)


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


class SingleElectrodeWidget(QWidget):
    """
    Widget displaying a single electrode button.
    
    This widget shows a centered, selectable electrode button

    Signals:
        signal_electrode_selected: Emitted with channel ID when initialized
    """
    signal_electrode_selected = Signal(int)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the single electrode widget.

        Args:
            parent: Parent widget in the Qt widget hierarchy
        """
        super().__init__(parent)

        self.electrode = ElectrodeButton(0, ElectrodeShape.circle)
        self.electrode.setChecked(True)

        self.electrode.toggled.connect(self._handle_toggle)
        self._init_ui()

    def _init_ui(self):
        """
        Initialize the user interface layout.
        
        Creates and configures a grid layout with a centered electrode button.
        """
        layout = QGridLayout()        
        layout.addWidget(self.electrode, 0, 0, Qt.AlignCenter)
        self.setLayout(layout)

    @Slot(bool)
    def _handle_toggle(self, checked: bool):
        """
        Handle electrode button toggle events.
        
        Emits selection signal (0) or deselection flag (-1) conditionally
        
        Args:
            checked: Whether the button was checked or unchecked
        """
        if checked:
            self.signal_electrode_selected.emit(0)
        else:
            self.signal_electrode_selected.emit(-1)

class MultiElectrodeWidget(QWidget):
    """
    Widget displaying an interactive grid of electrode buttons.
    
    This widget allows users to select one electrode at a time from an
    arrangement of electrodes. Electrodes correspond to D188 switcher channels.
    
    Signals:
        signal_electrode_selected: Emitted with selected electrode's channel ID
    """
    signal_electrode_selected = Signal(int)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the multi-electrode widget.

        Args:
            parent: Parent widget in the Qt widget hierarchy
        """
        super().__init__(parent)
        self._setup_electrode_grid()

    def _setup_electrode_grid(self):
        """
        Configures the electrode button grid layout.
        
        Creates and positions electrode buttons according in a grid, connecting 
        toggle handlers for mutual exclusion behavior.
        """
        electrode_layout = [    
            (1, ElectrodeShape.circle, 0, 1),
            (2, ElectrodeShape.circle, 0, 2),
            (7, ElectrodeShape.rectangle, 1, 0),
            (3, ElectrodeShape.circle, 1, 1),
            (4, ElectrodeShape.circle, 1, 2),
            (8, ElectrodeShape.rectangle, 1, 3),
            (5, ElectrodeShape.circle, 2, 1),
            (6, ElectrodeShape.circle, 2, 2)
        ]

        grid = QGridLayout()
        for channel_id, shape, row, col in electrode_layout:
            button = ElectrodeButton(channel_id, shape)
            button.toggled.connect(self._handle_toggle)
            grid.addWidget(button, row, col)

        self.setLayout(grid)

    @Slot(bool)
    def _handle_toggle(self, checked: bool):
        """
        Handle electrode button toggle events.
        
        Implements mutual exclusion behavior and emits selection signal.
        
        Args:
            checked: Whether the button was checked or unchecked
        """
        print(f"{self.sender()} is toggling {checked}")
        if checked:
            sender = self.sender()
            self._deselect_all_but_one(sender)
            self.signal_electrode_selected.emit(sender.channel_id)
        elif not self._any_electrodes_checked():
            # -1 acts as deselection flag
            self.signal_electrode_selected.emit(-1)
    
    def _deselect_all_but_one(self, selected_button: ElectrodeButton) -> None:
        """
        Ensure only one button remains selected.

        Deselects all electrode buttons except for the specified button.

        Args:
            selected_button: The ElectrodeButton that should remain selected
        """
        for button in self.findChildren(ElectrodeButton):
            if button is not selected_button:
                button.setChecked(False)

    def _any_electrodes_checked(self) -> bool:
        """
        Determine if any electrode buttons are checked.

        Iterates through all electrode buttons in the widget and checks their
        state. Returns True if at least one button is checked, otherwise False.

        Returns:
            bool: True if any electrode is checked; False otherwise
        """
        return any(button.isChecked() for button in self.findChildren(ElectrodeButton))


class ElectrodeMode(Enum):
    """
    Defines available electrode selection modes.
    
    Attributes:
        SINGLE: Mode for single electrode selection
        MULTI: Mode for multiple electrode selection
    """
    SINGLE = "DS8R - Single Electrode"
    MULTI = "D188 - Multiple Electrodes"


class ElectrodeSelectorWidget(QWidget):
    """
    Main widget for electrode selection with switchable modes.
    
    This widget manages switching between single and multiple electrode
    selection modes.
    
    Signals:
        signal_electrode_selected: Forwarded from active mode widget
    """
    signal_electrode_selected = Signal(int)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the electrode selector widget.

        Args:
            parent: Parent widget in the Qt widget hierarchy
        """
        super().__init__(parent)

        self.single_widget = SingleElectrodeWidget()
        self.multi_widget = MultiElectrodeWidget()

        self._init_ui()
        self._connect_signals()
        
        # Initialize with single electrode mode
        self.mode_changed(ElectrodeMode.SINGLE.value)

    def _init_ui(self):
        """
        Initialize the user interface components.
        
        Sets up the group box, mode selector dropdown, and container for
        electrode widgets.
        """
        self.group_box = QGroupBox("Cathode Selector")
        layout = QVBoxLayout()

        self.mode_selector = QComboBox()
        self.mode_selector.addItems([mode.value for mode in ElectrodeMode])
        layout.addWidget(self.mode_selector)

        self.electrode_container = QWidget()
        self.electrode_layout = QVBoxLayout(self.electrode_container)
        layout.addWidget(self.electrode_container)
        
        self.group_box.setLayout(layout)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.group_box)
        self.setLayout(main_layout)

    def _connect_signals(self):
        """
        Connect widget signals to their respective slots.
        
        Sets up signal connections between the mode selector and electrode
        widgets to handle mode changes and electrode selection events.
        """
        self.single_widget.signal_electrode_selected.connect(self.signal_electrode_selected.emit)
        self.multi_widget.signal_electrode_selected.connect(self.signal_electrode_selected.emit)
        self.mode_selector.currentTextChanged.connect(self.mode_changed)

    @Slot(str)
    def mode_changed(self, mode_text: str):
        """
        Updates the electrode layout based on the selected mode.

        Args:
            mode_text: Text representing the selected mode from ElectrodeMode
        """
        self._hide_widget()
        
        if mode_text == ElectrodeMode.SINGLE.value:
            self.electrode_layout.addWidget(self.single_widget)
            self.single_widget.show()
        else:
            self.electrode_layout.addWidget(self.multi_widget)
            self.multi_widget.show()

    def _hide_widget(self) -> None:
        """
        Hides all widgets currently in the layout.
        
        Removes and hides any widgets present in the electrode layout to
        prepare for showing a different mode's widget.
        """
        while self.electrode_layout.count():
            item = self.electrode_layout.takeAt(0)
            if item.widget():
                item.widget().hide()

    def sizeHint(self) -> QSize:
        """
        Provide recommended widget size.
        
        Overrides superclass's sizeHint method to suggest an appropriate
        size for the widget.
        
        Returns:
            QSize: Recommended widget dimensions (50x50 pixels)
        """
        return QSize(50, 50)