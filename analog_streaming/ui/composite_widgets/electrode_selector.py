from enum import Enum
from typing import Optional

from PySide6.QtCore import QSize, Signal, Slot
from PySide6.QtWidgets import QComboBox, QGroupBox, QVBoxLayout, QWidget

from .single_electrode import SingleElectrodeWidget
from .multi_electrode import MultiElectrodeWidget

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
        self._mode_changed(ElectrodeMode.SINGLE.value)

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
        self.mode_selector.currentTextChanged.connect(self._mode_changed)

    def _mode_changed(self, mode_text: str):
        """
        Updates the electrode layout based on the selected mode.

        Args:
            mode_text: Text representing the selected mode from ElectrodeMode
        """
        self._hide_widget()
        
        if mode_text == ElectrodeMode.SINGLE.value:
            self.electrode_layout.addWidget(self.single_widget)
            # Select the electrode by default since there is only one
            self.single_widget.set_defaults()
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
    
    def handle_stim_on(self):
        """
        Select electrode when stim is turned on in single electrode mode.

        In multi-electrode mode, stim can't be delivered without an electrode
        selected because the D188 can prevent pulse delivery since it stands 
        between the DS8R and the electrodes. In single electrode mode, 
        however, there is nothing between the DS8R and the electrodes. 

        This means that toggling stim on in single electrode mode will deliver stimulation even with the electrode deselected becuase the 'channel' stim parameter provided by the electrode selector would be irrelevant.

        Regardless of mode, toggling an electrode off will stop stimulation.

        This method ensures the electrode is selected by default when stim is 
        turned on in single electrode mode.
        """
        if self.mode_selector.currentText() == ElectrodeMode.SINGLE.value:
            self.single_widget.set_defaults()
