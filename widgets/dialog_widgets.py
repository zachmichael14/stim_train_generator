from PySide6 import QtWidgets
from PySide6.QtCore import QObject

class PulseEditDialog(QtWidgets.QDialog):
    """
    Pop-up dialog for editing pulse amplitude, frequency, and duration.
    """

    def __init__(self,
                 amplitude: float = 0,
                 frequency: float = 60,
                 duration: float = 50,
                 parent: QObject = None):
        """
        Initialize with the given parameters.

        Args:
            amplitude (float): Initial amplitude value in mA.
            frequency (float): Initial frequency value in Hz.
            duration (float): Initial duration value in ms.
            parent (QObject, optional): Parent widget/window for the dialog. Default is None.
        """
        super().__init__(parent)
        self.setWindowTitle(f"Edit Pulse")

        self.amplitude = amplitude
        self.frequency = frequency
        self.duration = duration

        self.amplitude_input = QtWidgets.QLineEdit(str(self.amplitude), self)
        self.frequency_input = QtWidgets.QLineEdit(str(self.frequency), self)
        self.duration_input = QtWidgets.QLineEdit(str(self.duration), self)

        self.init_main_layout()

    def init_main_layout(self):
        """
        Set up the main layout for the dialog, including input fields for
        amplitude, frequency, and duration.
        """
        main_layout = QtWidgets.QVBoxLayout(self)

        amplitude_label = QtWidgets.QLabel("Amplitude (mA):", self)
        main_layout.addWidget(amplitude_label)
        main_layout.addWidget(self.amplitude_input)

        frequency_label = QtWidgets.QLabel("Frequency (Hz):", self)
        main_layout.addWidget(frequency_label)
        main_layout.addWidget(self.frequency_input)

        duration_label = QtWidgets.QLabel("Duration (ms):", self)
        main_layout.addWidget(duration_label)
        main_layout.addWidget(self.duration_input)

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                             QtWidgets.QDialogButtonBox.Cancel,
                                             self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addLayout(buttons)

    def get_values(self):
        """
        Retrieve the current values of amplitude, frequency, and duration from the input fields.

        Returns:
            tuple (float, float, float): A tuple containing amplitude (mA), frequency (Hz), and duration (ms).
        """
        return (float(self.amplitude_input.text()),
                float(self.frequency_input.text()),
                float(self.duration_input.text()))


class IntervalEditDialog(QtWidgets.QDialog):
    """
    Pop-up dialog for editing the time between bursts.

    Attributes:
        duration (float): Duration of the interval in milliseconds.
    """

    def __init__(self, duration: float = 50, parent: QObject = None):
        """
        Initialize with the given duration.

        Args:
            duration (float): Initial duration value in ms.
            parent (QObject, optional): Parent widget/window for the dialog. Default is None.
        """
        super().__init__(parent)
        self.setWindowTitle("Edit Inter-burst Interval")

        self.duration = duration
        self.duration_input = QtWidgets.QLineEdit(str(self.duration), self)
        self.init_main_layout()

    def init_main_layout(self):
        """
        Set up the main layout with an input field for the duration.
        """
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(QtWidgets.QLabel("Duration (ms):"))
        main_layout.addWidget(self.duration_input)

        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                             QtWidgets.QDialogButtonBox.Cancel,
                                             self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

    def get_value(self):
        """
        Retrieve the current interval duration from the input field.

        Returns:
            float: The interval duration in milliseconds.
        """
        return float(self.duration_input.text())
