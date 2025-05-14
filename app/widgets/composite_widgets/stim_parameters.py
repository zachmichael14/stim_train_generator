from typing import Optional, Dict

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QGridLayout, QGroupBox, QLabel, QVBoxLayout, QWidget, QSizePolicy
)

from analog_streaming.widgets.composite_widgets.ramp_settings import RampSettingsWidget
from analog_streaming.widgets.basic_components.debounced_spin_box import DebouncedDoubleSpinBox
from analog_streaming.utils.ramp_calculator import RampCalculator

class StimParameterWidget(QWidget):
    # current value, ramp values
    signal_current_value_changed = Signal(float, dict)

    # ramp_param, current_value, target_value, duration
    signal_ramp_params_changed = Signal(str, float, float, float)

    signal_ramp_requested = Signal(str)

    signal_check_radio_state = Signal()

    def __init__(self,
                 defaults: dict[str, float],
                 parameter: str = "Amplitude", 
                 unit: str = "Milliamps"):
        super().__init__()
        
        self.unit = unit

        self.parameter_spinbox = DebouncedDoubleSpinBox(max_increase=defaults["max_increase"])
        self.parameter_spinbox.setValue(defaults["global_value"])
        self.parameter_spinbox.setFixedWidth(100)


        self.step_spinbox = DebouncedDoubleSpinBox(max_value=defaults["max_increase"])
        self.step_spinbox.setValue(1.0)
        self.step_spinbox.setSingleStep(0.1)
        self.step_spinbox.setFixedWidth(100)

        self.ramp_widget = RampSettingsWidget(defaults, unit=unit)
        self.ramp_calculator = RampCalculator()
        self.group_box = QGroupBox(f"{parameter} Settings")
       
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        group_layout = QGridLayout(self.group_box)

        group_layout.addWidget(QLabel("Current Value"), 0, 0)
        group_layout.addWidget(QLabel("Step"), 0, 1)

        group_layout.addWidget(self.parameter_spinbox, 1, 0)
        group_layout.addWidget(self.step_spinbox, 1, 1)

        group_layout.addWidget(self.ramp_widget, 2, 0, 1, 2)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.group_box)
        self.setLayout(main_layout)

    def _connect_signals(self):
        self.parameter_spinbox.signal_value_changed.connect(self._handle_current_value_changed)
        
        self.step_spinbox.signal_value_changed.connect(self._handle_step_changed)

        self.ramp_widget.signal_ramp_toggled.connect(self._handle_ramp_toggled)
        self.ramp_widget.signal_ramp_requested.connect(self._handle_ramp_requested)

        self.ramp_widget.signal_ramp_params_changed.connect(self._handle_ramp_params_changed)

    @Slot(float)
    def _handle_current_value_changed(self, value: float):
        """If ramping, signal new for new intermediate calculation."""
        if self.ramp_widget.is_enabled():
            print("is enabled")
            self.set_all_radio_enabled_state(True)
            ramp_values = self.ramp_widget.get_values()
            self.signal_current_value_changed.emit(value, ramp_values)
        else:
            self.signal_current_value_changed.emit(value, None)

    @Slot(str, float, float)
    def _handle_ramp_params_changed(self,
                                    ramp_param: str,
                                    ramp_target_value: float,
                                    ramp_duration: float):
        current_value = self.parameter_spinbox.value()
        self.signal_ramp_params_changed.emit(ramp_param,
                                             current_value,
                                             ramp_target_value,
                                             ramp_duration)

    @Slot(float)
    def _handle_step_changed(self, new_step: float):
        self.parameter_spinbox.setSingleStep(new_step)

    @Slot(bool)
    def _handle_ramp_toggled(self, is_toggled: bool):
        """Send widget ramp values and current value if ramp is toggled on."""
        current_value = self.parameter_spinbox.value()

        if is_toggled:
            self.signal_check_radio_state.emit()
            ramp_values = self.ramp_widget.get_values()
            self.signal_current_value_changed.emit(current_value, ramp_values)
        else:
            self.signal_current_value_changed.emit(current_value, None)

    @Slot(str)
    def _handle_ramp_requested(self, ramp_direction: str):
        self.signal_ramp_requested.emit(ramp_direction)

    def is_enabled(self) -> bool:
        return self.ramp_widget.is_enabled()
    
    def is_ramping(self) -> bool:
        return self.ramp_widget.is_ramping()
    
    def get_current_value(self) -> float:
        return self.parameter_spinbox.value()

    def get_ramp_values(self) -> dict:
        values = self.ramp_widget.get_values()
        return values
    
    def deselect_ramp_buttons(self) -> None:
        self.ramp_widget.deselect_ramp_buttons()

    def set_all_radio_enabled_state(self, is_enabled: bool):
        if self.ramp_widget.is_enabled():
            self.ramp_widget.set_all_radio_enabled_state(is_enabled)