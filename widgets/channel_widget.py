from typing import Dict, Tuple, Type

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
        # Checkboxes dictionary format:
        # {Checkbox widget: {"id": channel id, "state": checked state}}
        self.checkboxes: Dict[Type[QtWidgets.QCheckBox]: Dict[str: int,
                                                              str: bool]] = {}
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
            self.checkboxes[checkbox] = {"id": i, "state": checkbox.isChecked()}

        main_layout.addWidget(groupbox)

    def input_received_callback(self, state):
        """
        Update the selected channels list based on checkbox state.
        
        Args:
            id (int): The ID of the channel associated with the checkbox.
            state (int): The state of the checkbox (checked or unchecked).
        """
        checkbox = self.sender()
        self.checkboxes[checkbox]["state"] = checkbox.isChecked()

    def reset(self):
        """
        Reset all checkboxes to their default (unchecked) state and clear the selected channels list.
        """
        for checkbox in self.checkboxes.keys():
            checkbox.setChecked(False)
            self.checkboxes[checkbox]["state"] = False

    def get_active_channels(self):
        # Other widgets should only be concerned with the ID of active
        # channels, so there shouldn't be a need to send the checkboxes
        return [value["id"] for value in self.checkboxes.values() if value["state"] == True]