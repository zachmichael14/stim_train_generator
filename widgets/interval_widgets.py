from PySide6 import QtWidgets
from widgets.base_widgets import IntervalWidget

class AmplitudeIntervalWidget(IntervalWidget):
    def __init__(self):
        super().__init__("Amplitude Settings")

    def handle_value_change(self):
        values = self.get_values()
        if self.validate_values(values):
            self.value_changed.emit(values)

    # def handle_mode_selector(self, button: QtWidgets.QRadioButton):
    #     super().handle_mode_selector(button)
    #     mode = self.get_current_mode()
    #     self.mode_changed.emit(mode)


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