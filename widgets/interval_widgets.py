from abc import abstractmethod

from PySide6 import QtWidgets, QtCore
import numpy as np

from widgets.basic_widgets import ConstantWidget, RampWidget, FunctionWidget, RepetitionWidget

class IntervalWidget(QtWidgets.QWidget):
    mode_changed = QtCore.Signal()

    def __init__(self, title):
        super().__init__()
        self.title = title
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.subwidget = ConstantWidget() # ConstantWidget is default
        
        # Widget mode group buttons
        self.constant_button = QtWidgets.QRadioButton("Constant", self)
        self.ramp_button = QtWidgets.QRadioButton("Ramp", self)
        self.function_button = QtWidgets.QRadioButton("Function", self)
        self.constant_button.setChecked(True)

        self.subwidget_container = QtWidgets.QWidget()
        self.subwidget_layout = QtWidgets.QVBoxLayout(self.subwidget_container)
        self.subwidget_layout.addWidget(self.subwidget)

        self.init_ui()
        
    def init_ui(self):
        mode_groupbox = QtWidgets.QGroupBox(f"{self.title}")
        mode_layout = QtWidgets.QVBoxLayout(mode_groupbox)
        
        self.init_mode_selectors(mode_layout)
        mode_layout.addWidget(self.subwidget_container)
        
        self.main_layout.addWidget(mode_groupbox)

        self.setLayout(self.main_layout)       

    def init_mode_selectors(self, layout):
        mode_selector = QtWidgets.QButtonGroup(self)
        mode_selector.addButton(self.constant_button)
        mode_selector.addButton(self.ramp_button)
        mode_selector.addButton(self.function_button)

        mode_selector.buttonClicked.connect(self.handle_mode_selector)

        selector_layout = QtWidgets.QHBoxLayout()
        selector_layout.addWidget(self.constant_button)
        selector_layout.addWidget(self.ramp_button)
        selector_layout.addWidget(self.function_button)

        layout.addLayout(selector_layout)
        
    def handle_mode_selector(self, button: QtWidgets.QRadioButton):
        if button == self.constant_button:
            self.show_widget(ConstantWidget)
        elif button == self.ramp_button:
            self.show_widget(RampWidget)
        else:
            self.show_widget(FunctionWidget)
        self.mode_changed.emit()

    def show_widget(self, widget_class: QtWidgets.QWidget):
        self.subwidget.deleteLater()
        new_subwidget = widget_class()
        self.subwidget_layout.replaceWidget(self.subwidget, new_subwidget)
        self.subwidget = new_subwidget

    def get_current_mode(self):
        if self.constant_button.isChecked():
            return "constant"
        elif self.ramp_button.isChecked():
            return "ramp"
        else:
            return "function"
        
    def reset(self):
        self.constant_button.setChecked(True)
        self.show_widget(ConstantWidget)
        self.subwidget.text_edit.clear()

    @abstractmethod
    def get_values(self):
        pass


class AmplitudeIntervalWidget(IntervalWidget):
    def __init__(self):
        super().__init__("Amplitude Settings")
        self.repetition_widget = None
        self.show_repetition_widget()
        self.mode_changed.connect(self.show_repetition_widget)

    def show_repetition_widget(self):
        if self.repetition_widget:
            self.remove_current_subwidget()

        current_mode = self.get_current_mode()
        if current_mode == "function":
            # No subwidget for function mode
            return
        
        label_text = self.get_label_text(current_mode)
        self.repetition_widget = RepetitionWidget(label_text)
        self.subwidget_layout.addWidget(self.repetition_widget)

    def remove_current_subwidget(self):
        self.subwidget_layout.removeWidget(self.repetition_widget)
        self.repetition_widget.deleteLater()
        self.repetition_widget = None

    def get_label_text(self, current_mode):
        if current_mode == "constant":
            label_text = "Total Pulses:"
        elif current_mode == "ramp":
            label_text = "Pulses per Amplitude:"
        return label_text
    
    def get_values(self):
        amplitudes = self.subwidget.get_values()
        
        repetitions = 1
        if self.repetition_widget:
            repetitions = self.repetition_widget.get_values()

        return np.repeat(amplitudes, repetitions)


class PulseLengthIntervalWidget(IntervalWidget):
    def __init__(self):
        super().__init__("Pulse Duration Settings")

    def get_values(self):
        pass


class InterPulseIntervalWidget(IntervalWidget):
    def __init__(self):
        super().__init__("Inter-pulse Interval Settings")

    def get_values(self):
        pass


class FrequencyWidget(IntervalWidget):
    def __init__(self):
        super().__init__("Frequency Settings")
        
    def get_values(self):
        pass
