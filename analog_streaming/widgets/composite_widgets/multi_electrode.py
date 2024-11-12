from typing import Optional

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QGridLayout, QWidget

from analog_streaming.widgets.basic_components.electrode_button import ElectrodeButton, ElectrodeShape

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
        Since this method is called twice when switching electrodes (first
        to toggle the new button on and next to turn the old one off), this 
        method checks if any buttons are currently toggled before sending
        deselection flag. Otherwise, the toggle off would always send the
        flag, even when switching between buttons, since the toggle off occurs
        last.
        
        Args:
            checked: Whether the button was checked or unchecked
        """
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
    