from typing import Dict

from PySide6 import QtWidgets
from PySide6.QtCore import Signal

class ChannelAddWidget(QtWidgets.QWidget):
    """
    Widget for selecting multiple channels via checkboxes and emitting the selected channels.
    
    Attributes:
        channels_selected (QtCore.Signal): Signal that emits list of selected
        channels whenever channels are toggled.
    """
    signal_values_ready = Signal()

    def __init__(self):
        """
        Initialize the ChannelAddWidget with checkboxes for channel selection.
        """
        super().__init__()
        # Values will be checked state
        self.checkboxes: Dict[QtWidgets.QCheckBox: bool] = {}
        self.init_main_layout()

    def init_main_layout(self):
        """
        Set up the user interface with a group box containing checkboxes for each channel.
        """
        main_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(main_layout)

        groupbox = QtWidgets.QGroupBox("Add Train to Channel(s)")
        groupbox_layout = QtWidgets.QHBoxLayout(groupbox)

        for i in range(1, 9):
            checkbox = QtWidgets.QCheckBox(f"Channel {i}")
            checkbox.stateChanged.connect(self.input_received_callback)

            groupbox_layout.addWidget(checkbox)
            self.checkboxes[i] = checkbox.isChecked()

        main_layout.addWidget(groupbox)

    def input_received_callback(self, state):
        """
        Update the selected channels list based on checkbox state.
        
        Args:
            id (int): The ID of the channel associated with the checkbox.
            state (int): The state of the checkbox (checked or unchecked).
        """
        checkbox = self.sender()
        self.checkboxes[checkbox] = checkbox.isChecked()

    def reset(self):
        """
        Reset all checkboxes to their default (unchecked) state and clear the selected channels list.
        """
        for checkbox in self.checkboxes.keys():
            checkbox.setChecked(False)
            self.checkboxes[checkbox] = False

    def get_active_channels(self):
        return {key: value for key, value in self.checkboxes.items() if value == True}