from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QGridLayout, QGroupBox, QLabel, QVBoxLayout, QWidget
)

from analog_streaming.utils.ramp_calculator import RampCalculator
from analog_streaming.ui.basic_components.debounced_spin_box import DebouncedDoubleSpinBox
from .ramp_settings import RampSettingsWidget

class StimParameterWidget(QWidget):
    signal_current_value_changed = Signal(float)
    signal_calculate_ramp_values = Signal(float, dict)
    
    # Current value, target value, duration
    signal_ramp_max_changed = Signal(float, float, float)
    signal_ramp_rest_changed = Signal(float, float, float)
    signal_ramp_min_changed = Signal(float, float, float)

    signal_ramp_requested = Signal(str)

    def __init__(self,
                 defaults: dict[str, float],
                 parameter: str = "Amplitude", 
                 unit: str = "Milliamps"):
        super().__init__()
        
        self.unit = unit

        self.parameter_spinbox = DebouncedDoubleSpinBox(max_increase=defaults["max_increase"])
        self.parameter_spinbox.setValue(defaults["global_value"])

        self.ramp_widget = RampSettingsWidget(defaults, unit=unit)
        self.ramp_calculator = RampCalculator()
        self.group_box = QGroupBox(f"{parameter} Settings")
       
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        group_layout = QGridLayout(self.group_box)

        group_layout.addWidget(QLabel(f"Current value:"), 0, 0)
        group_layout.addWidget(self.parameter_spinbox, 0, 1)
        group_layout.addWidget(self.ramp_widget, 1, 0, 1, 2)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.group_box)
        self.setLayout(main_layout)

    def _connect_signals(self):
        self.parameter_spinbox.signal_value_changed.connect(self._handle_current_value_changed)

        self.ramp_widget.signal_ramp_toggled.connect(self._handle_ramp_toggled)
        self.ramp_widget.signal_ramp_requested.connect(self._handle_ramp_requested)

        self.ramp_widget.signal_max_params_changed.connect(self._handle_max_params_changed)
        self.ramp_widget.signal_rest_params_changed.connect(self._handle_rest_params_changed)
        self.ramp_widget.signal_min_params_changed.connect(self._handle_min_params_changed)

    @Slot(float)
    def _handle_current_value_changed(self, value: float):
        """If ramping, signal new for new intermediate calculation."""
        if self.ramp_widget.is_enabled():
            ramp_values = self.ramp_widget.get_values()
            self.signal_calculate_ramp_values.emit(value, ramp_values)
        else:     
            self.signal_current_value_changed.emit(value)

    @Slot(bool)
    def _handle_ramp_toggled(self, is_toggled: bool):
        """If it's toggled on, send the calculated ramps
        Emit None if toggled off
        """
        current_value = self.parameter_spinbox.value()
        if is_toggled:
            ramp_values = self.ramp_widget.get_values()
            self.signal_calculate_ramp_values.emit(current_value, ramp_values)
        # else:
            # self.signal_calculate_ramp_values.emit(current_value, None)

    @Slot(str)
    def _handle_ramp_requested(self, ramp_direction: str):
        self.signal_ramp_requested.emit(ramp_direction)

    @Slot(float, float)
    def _handle_max_params_changed(self,
                                   target_value: float,
                                   duration: float):
        current_value = self.parameter_spinbox.value()
        self.signal_ramp_max_changed.emit(current_value,
                                          target_value,
                                          duration)

    @Slot(float, float)
    def _handle_rest_params_changed(self,
                                    target_value: float,
                                    duration: float):
        current_value = self.parameter_spinbox.value()
        self.signal_ramp_rest_changed.emit(current_value,
                                           target_value,
                                           duration)

    @Slot(float, float)
    def _handle_min_params_changed(self,
                                   target_value: float,
                                   duration: float):
        current_value = self.parameter_spinbox.value()
        self.signal_ramp_min_changed.emit(current_value,
                                          target_value,
                                          duration)

    def is_ramping(self) -> bool:
        return self.ramp_widget.is_ramping()