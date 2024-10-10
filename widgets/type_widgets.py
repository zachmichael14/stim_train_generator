from typing import List

import numpy as np
from PySide6 import QtWidgets
from PySide6.QtCore import Signal

from .basic_widgets import DropdownWidget, SingleTextFieldWidget

import generation_functions

class PulseWidget(QtWidgets.QWidget):
    function_registry = generation_functions.FunctionRegistry()

    def __init__(self):
        super().__init__()
        main_layout = QtWidgets.QVBoxLayout()

        # Visually wrap all subwidgets in a labeled border-box
        self.subwidget_container_layout = QtWidgets.QVBoxLayout()
        subwidget_container = QtWidgets.QGroupBox(f"Amplitude Settings")
        subwidget_container.setLayout(self.subwidget_container_layout)


        amplitude_function_classes = self.function_registry.get_category_functions("Amplitude")
        amplitude_widget = DropdownWidget([cls.name for cls in amplitude_function_classes])
        self.subwidget_container_layout.addWidget(amplitude_widget)

        rest_period = SingleTextFieldWidget("Time Between Pulses:")
        self.subwidget_container_layout.addWidget(rest_period)
           
        main_layout.addWidget(subwidget_container)
        self.setLayout(main_layout)


class ContinousWidget(QtWidgets.QWidget):
    function_registry = generation_functions.FunctionRegistry()

    def __init__(self):
        super().__init__()
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        # Visually wrap all subwidgets in a labeled border-box
        self.amplitude_container_layout = QtWidgets.QVBoxLayout()
        amplitude_container = QtWidgets.QGroupBox("Amplitude Settings")
        amplitude_container.setLayout(self.amplitude_container_layout)


        amplitude_function_classes = self.function_registry.get_category_functions("Amplitude")
        amplitude_widget = DropdownWidget([cls.name for cls in amplitude_function_classes])
        self.amplitude_container_layout.addWidget(amplitude_widget)

        rest_period = SingleTextFieldWidget("Time Between Pulses:")
        self.amplitude_container_layout.addWidget(rest_period)

        main_layout.addWidget(amplitude_container)

        ramp_amplitude_checkbox = QtWidgets.QCheckBox("Ramp Amplitude?")
        ramp_amplitude_checkbox.setChecked(True)
        self.amplitude_container_layout.addWidget(ramp_amplitude_checkbox)


        ramp_amplitude_start = SingleTextFieldWidget("Starting Amplitude")
        self.amplitude_container_layout.addWidget(ramp_amplitude_start)

        ramp_amplitude_end = SingleTextFieldWidget("Final Ramped Amplitude:")
        self.amplitude_container_layout.addWidget(ramp_amplitude_end)

        ramp_amplitude_duration = SingleTextFieldWidget("Amplitude Ramp Duration:")
        self.amplitude_container_layout.addWidget(ramp_amplitude_duration)

        


        self.frequency_container_layout = QtWidgets.QVBoxLayout()
        frequency_container = QtWidgets.QGroupBox("Frequency Settings")
        frequency_container.setLayout(self.frequency_container_layout)


        frequency_function_classes = self.function_registry.get_category_functions("Frequency")
        frequency_widget = DropdownWidget([cls.name for cls in frequency_function_classes])
        self.frequency_container_layout.addWidget(frequency_widget)

        main_layout.addWidget(frequency_container)

        ramp_frequency_checkbox = QtWidgets.QCheckBox("Ramp Frequency?")
        ramp_frequency_checkbox.setChecked(True)
        self.frequency_container_layout.addWidget(ramp_frequency_checkbox)


        ramp_frequency_start = SingleTextFieldWidget("Starting Frequency")
        self.frequency_container_layout.addWidget(ramp_frequency_start)

        ramp_frequency_end = SingleTextFieldWidget("Final Ramped Frequency:")
        self.frequency_container_layout.addWidget(ramp_frequency_end)

        ramp_frequency_duration = SingleTextFieldWidget("Frequency Ramp Duration:")
        self.frequency_container_layout.addWidget(ramp_frequency_duration)

        
    

