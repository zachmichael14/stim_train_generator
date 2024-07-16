from PySide6 import QtWidgets, QtCore

class TrainLengthWidget(QtWidgets.QWidget):
    value_changed = QtCore.Signal(int)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        self.groupbox = QtWidgets.QGroupBox("Amplitude Repetition Settings")
        self.groupbox_layout = QtWidgets.QVBoxLayout(self.groupbox)

        self.amplitude_repetitions_label = QtWidgets.QLabel("Repetitions per Amplitude:")
        self.amplitude_repetitions_edit = QtWidgets.QLineEdit()
        self.amplitude_repetitions_edit.setPlaceholderText("Enter repetitions")

        self.amplitude_repetitions_edit.textChanged.connect(self.handle_repetition_changed)
        
        self.amplitude_repetitions_layout = QtWidgets.QHBoxLayout()
        self.amplitude_repetitions_layout.addWidget(self.amplitude_repetitions_label)
        self.amplitude_repetitions_layout.addWidget(self.amplitude_repetitions_edit)

        self.groupbox_layout.addLayout(self.amplitude_repetitions_layout)

        main_layout.addWidget(self.groupbox)
        self.setLayout(main_layout)

    def handle_repetition_changed(self):
        if self.amplitude_repetitions_edit.text() != "":
            try:
                repetitions = int(self.amplitude_repetitions_edit.text())
                self.value_changed.emit(repetitions)
            except ValueError as e:
                print(f"TrainLengthWidget can't convert repetitions to int: {e}")

    def reset(self):
        self.amplitude_repetitions_edit.clear()

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


class MiscSettingsWidget(QtWidgets.QWidget):
    value_changed = QtCore.Signal(float)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        groupbox = QtWidgets.QGroupBox("Miscellaneous Settings")
        groupbox_layout = QtWidgets.QVBoxLayout(groupbox)

        # Frequency (Hz)
        self.frequency_label = QtWidgets.QLabel("Frequency (Hz)")
        self.frequency_edit = QtWidgets.QLineEdit()
        self.frequency_edit.setPlaceholderText("Enter frequency")
        self.frequency_edit.textChanged.connect(self.handle_frequency_changed)

        self.frequency_layout = QtWidgets.QHBoxLayout()
        self.frequency_layout.addWidget(self.frequency_label)
        self.frequency_layout.addWidget(self.frequency_edit)

        # Add layouts to groupbox layout
        groupbox_layout.addLayout(self.frequency_layout)

        main_layout.addWidget(groupbox)
        self.setLayout(main_layout)

    def handle_frequency_changed(self):
        if self.frequency_edit.text() != "":
            try:
                frequency = float(self.frequency_edit.text())
                self.value_changed.emit(frequency)
            except ValueError as e:
                print(f"MiscSettingsWidget can't convert frequency to float: {e}")

    def reset(self):
        self.frequency_edit.clear()