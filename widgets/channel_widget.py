from PySide6 import QtWidgets, QtCore

class ChannelAddWidget(QtWidgets.QWidget):
    channels_selected = QtCore.Signal(list)

    def __init__(self):
        super().__init__()
        # Store the checkboxes so they can be reset later
        self.checkboxes = []
        self.selected_channels = []
        self.init_ui()

    def init_ui(self):
        # Create the GroupBox for Mode Settings
        main_layout = QtWidgets.QVBoxLayout(self)
        groupbox = QtWidgets.QGroupBox("Add Train to Channel(s)")
        groupbox_layout = QtWidgets.QHBoxLayout(groupbox)

        for i in range(1, 9):
            checkbox = QtWidgets.QCheckBox(f"Channel {i}")
            checkbox.stateChanged.connect(lambda state, id=i: self.handle_checkbox(id, state))
            groupbox_layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)

        main_layout.addWidget(groupbox)

        add_button = QtWidgets.QPushButton("Add to Channel(s)")
        add_button.clicked.connect(self.handle_add_button)
        main_layout.addWidget(add_button)

        self.setLayout(main_layout)

    def handle_checkbox(self, id, state):
        if state == 2: # checked state
            self.selected_channels.append(id)
        elif id in self.selected_channels:
            self.selected_channels.remove(id)

    def handle_add_button(self):
        self.channels_selected.emit(self.selected_channels)

    def reset(self):
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)
        self.selected_channels = []