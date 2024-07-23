from PySide6 import QtWidgets
from widgets.basic_widgets import IntervalWidget

class AmplitudeIntervalWidget(IntervalWidget):
    def __init__(self):
        super().__init__("Amplitude Settings")
        self.repetition_widget = None
        self.show_subwidget()

        self.mode_changed.connect(self.show_subwidget)

    def remove_current_subwidget(self):
        self.subwidget_layout.removeWidget(self.repetition_widget)
        self.repetition_widget.deleteLater()
        self.repetition_widget = None

    def show_subwidget(self):
        if self.repetition_widget:
            self.remove_current_subwidget()

        current_mode = self.get_current_mode()

        if current_mode == "function":
            # No subwidget for function mode
            return

        # Create new subwidget
        self.repetition_widget = QtWidgets.QWidget()
        extra_layout = QtWidgets.QHBoxLayout(self.repetition_widget)

        label = QtWidgets.QLabel()
        textbox = QtWidgets.QLineEdit()

        if current_mode == "constant":
            label.setText("Total pulses:")
            textbox.setPlaceholderText("Total pulses")
        elif current_mode == "ramp":
            label.setText("Pulses per Amplitude:")
            textbox.setPlaceholderText("Pulses per Amplitude")


        extra_layout.addWidget(label)
        extra_layout.addWidget(textbox)

        # Add new subwidget to layout
        self.subwidget_layout.addWidget(self.repetition_widget)

        # Connect textbox signal
        textbox.textChanged.connect(self.validate_and_emit)

    def handle_value_change(self):
        values = self.get_values()
        if self.validate_values(values):
            self.value_changed.emit(values)
            self.show_subwidget()

class PulseLengthIntervalWidget(IntervalWidget):
    def __init__(self):
        super().__init__("Pulse Length Settings")

    def handle_value_change(self):
        values = self.get_values()
        if self.validate_values(values):
            self.value_changed.emit(values)


class InterPulseIntervalWidget(IntervalWidget):
    def __init__(self):
        super().__init__("Inter-pulse Interval Settings")

    def handle_value_change(self):
        values = self.get_values()
        if self.validate_values(values):
            self.value_changed.emit(values)