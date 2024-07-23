from PySide6.QtWidgets import (QVBoxLayout, QLineEdit, QLabel, QPushButton, QDialog, QHBoxLayout, QDialogButtonBox)

class PulseEditDialog(QDialog):
    def __init__(self, amplitude=1, frequency=60, duration=50, parent=None):
        super().__init__(parent)
        self.amplitude = amplitude
        self.frequency = frequency
        self.duration = duration
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(f"Edit Pulse")
        layout = QVBoxLayout(self)

        self.amplitude_label = QLabel("Amplitude (mA):", self)
        self.amplitude_input = QLineEdit(str(self.amplitude), self)
        layout.addWidget(self.amplitude_label)
        layout.addWidget(self.amplitude_input)

        self.frequency_label = QLabel("Frequency (Hz):", self)
        self.frequency_input = QLineEdit(str(self.frequency), self)
        layout.addWidget(self.frequency_label)
        layout.addWidget(self.frequency_input)

        self.duration_label = QLabel("Duration (ms):", self)
        self.duration_input = QLineEdit(str(self.duration), self)
        layout.addWidget(self.duration_label)
        layout.addWidget(self.duration_input)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK", self)
        self.cancel_button = QPushButton("Cancel", self)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    def get_values(self):
        return (float(self.amplitude_input.text()),
                float(self.frequency_input.text()),
                float(self.duration_input.text()))
    

class IntervalEditDialog(QDialog):
    def __init__(self, duration=50, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Interval")
        layout = QVBoxLayout(self)
        self.duration = duration

        self.duration_input = QLineEdit(str(self.duration), self)
        layout.addWidget(QLabel("Duration (ms):"))
        layout.addWidget(self.duration_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_value(self):
        return float(self.duration_input.text())
    