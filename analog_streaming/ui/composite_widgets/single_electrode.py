from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QGridLayout, QWidget

from ..basic_components.electrode_button import ElectrodeButton, ElectrodeShape

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

        self.electrode.toggled.connect(self._handle_toggle)
        self._init_ui()
        self.set_defaults()

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

    def set_defaults(self):
        self.electrode.setChecked(True)
        self.signal_electrode_selected.emit(0)
