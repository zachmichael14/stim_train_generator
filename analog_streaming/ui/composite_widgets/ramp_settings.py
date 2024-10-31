from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QGridLayout, QGroupBox, QLabel, QVBoxLayout, QWidget, QRadioButton
)

from analog_streaming.ui.basic_components.debounced_spin_box import DebouncedDoubleSpinBox

class RampSettingsWidget(QWidget):
    """
    Widget for controlling ramp parameters with adjustable settings.

    Attributes:
        signal_ramp_toggled: Emitted when ramp is toggled on or off.
        signal_ramp_requested: Emitted when a specific ramp is requested.
        signal_max_params_changed: Emitted when max ramp parameters change.
        signal_rest_params_changed: Emitted when rest ramp parameters change.
        signal_min_params_changed: Emitted when min ramp parameters change.
    """
    
    signal_ramp_toggled = Signal(bool)
    signal_ramp_requested = Signal(str)
    signal_max_params_changed = Signal(float, float)
    signal_rest_params_changed = Signal(float, float)
    signal_min_params_changed = Signal(float, float)

    def __init__(self, defaults: dict, unit: str = "Milliamps"):
        """
        Initializes the ParameterRampSettingsWidget with default values.

        Args:
            defaults: Dictionary containing default values for ramp settings.
            unit: Measurement unit for the ramp values (default: "mA").
        """
        super().__init__()
        self.unit = unit
        self.ramp_group_box = QGroupBox("Ramp Settings")

        self.max_radio = QRadioButton("Max")
        self.rest_radio = QRadioButton("Rest")
        self.min_radio = QRadioButton("Min")

        self.ramp_max = DebouncedDoubleSpinBox(max_increase=defaults["max_increase"])
        self.ramp_rest = DebouncedDoubleSpinBox(max_increase=defaults["max_increase"])
        self.ramp_min = DebouncedDoubleSpinBox(max_increase=defaults["max_increase"])

        self.to_max_duration = DebouncedDoubleSpinBox()
        self.to_rest_duration = DebouncedDoubleSpinBox()
        self.to_min_duration = DebouncedDoubleSpinBox()

        self._init_ui()
        self._set_defaults(defaults)
        self._connect_signals()       

    def _init_ui(self) -> None:
        """Initializes the user interface components."""
        ramp_group_box_layout = QGridLayout()

        # Column headers
        ramp_group_box_layout.addWidget(QLabel("Go To"), 0, 0)
        ramp_group_box_layout.addWidget(QLabel(f"{self.unit}"), 0, 1)
        ramp_group_box_layout.addWidget(QLabel("Seconds"), 0, 2)
        
        ramp_group_box_layout.addWidget(self.max_radio, 1, 0)
        ramp_group_box_layout.addWidget(self.ramp_max, 1, 1)
        ramp_group_box_layout.addWidget(self.to_max_duration, 1, 2)
        # ramp_group_box_layout.addWidget(QLabel(f"seconds"), 1, 3)

        ramp_group_box_layout.addWidget(self.rest_radio, 2, 0)
        ramp_group_box_layout.addWidget(self.ramp_rest, 2, 1)
        ramp_group_box_layout.addWidget(self.to_rest_duration, 2, 2)
        # ramp_group_box_layout.addWidget(QLabel(f"seconds"), 2, 3)

        ramp_group_box_layout.addWidget(self.min_radio, 3, 0)
        ramp_group_box_layout.addWidget(self.ramp_min, 3, 1)
        ramp_group_box_layout.addWidget(self.to_min_duration, 3, 2)
        # ramp_group_box_layout.addWidget(QLabel(f"seconds"), 3, 3)
        
        self.ramp_group_box.setLayout(ramp_group_box_layout)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.ramp_group_box)
        self.setLayout(main_layout)

    def _connect_signals(self) -> None:
        """Connects signals to their respective handler methods."""
        self.ramp_group_box.toggled.connect(self._handle_ramp_toggled)
        
        self.max_radio.toggled.connect(self._handle_ramp_requested)
        self.rest_radio.toggled.connect(self._handle_ramp_requested)
        self.min_radio.toggled.connect(self._handle_ramp_requested)

        self.ramp_max.signal_value_changed.connect(self._handle_max_params_changed)
        self.ramp_rest.signal_value_changed.connect(self._handle_rest_params_changed)
        self.ramp_min.signal_value_changed.connect(self._handle_min_params_changed)

        self.to_max_duration.signal_value_changed.connect(self._handle_max_params_changed)
        self.to_rest_duration.signal_value_changed.connect(self._handle_rest_params_changed)
        self.to_min_duration.signal_value_changed.connect(self._handle_min_params_changed)

    def _set_defaults(self, defaults: dict) -> None:
        """
        Sets default values for the ramp parameter widgets.

        Args:
            defaults: Dictionary containing default values for ramp settings.
        """
        self.ramp_group_box.setCheckable(True)
        self.ramp_group_box.setChecked(False)

        self.ramp_max.setValue(defaults["ramp_max"])
        self.ramp_rest.setValue(defaults["ramp_rest"])
        self.ramp_min.setValue(defaults["ramp_min"])

        self.to_max_duration.setValue(defaults["to_max_duration"])
        self.to_rest_duration.setValue(defaults["to_rest_duration"])
        self.to_min_duration.setValue(defaults["to_min_duration"])

    @Slot(bool)
    def _handle_ramp_toggled(self, is_toggled: bool) -> None:
        """
        Handles the toggling of the ramp settings.

        Emits signal with toggle state.

        Args:
            is_toggled: The state of the toggle (True for on, False for off).
        """
        self.signal_ramp_toggled.emit(is_toggled)

    @Slot(str)
    def _handle_ramp_requested(self, is_toggled: bool) -> None:
        """
        Handles ramp requests based on radio button selection.

        Emits a signal with str indicating ramp direction (max, rest, or min).

        Args:
            is_toggled: The state of the toggle (True for selected).
        """
        if is_toggled:
            self.signal_ramp_requested.emit(self.sender().text().casefold()) 
    
    @Slot(float, float)
    def _handle_max_params_changed(self) -> None:
        """
        Handles changes in max ramp parameters.
        
        Emits a signal with the new values.
        """
        ramp_value = self.ramp_max.value()
        duration = self.to_max_duration.value()
        self.signal_max_params_changed.emit(ramp_value, duration)

    @Slot(float, float)
    def _handle_rest_params_changed(self) -> None:
        """
        Handles changes in rest ramp parameters.
        
        Emits a signal with the new values.
        """
        ramp_value = self.ramp_rest.value()
        duration = self.to_rest_duration.value()
        self.signal_rest_params_changed.emit(ramp_value, duration)

    @Slot(float, float)
    def _handle_min_params_changed(self) -> None:
        """
        Handles changes in min ramp parameters.
        
        Emits a signal with the new values.
        """
        ramp_value = self.ramp_min.value()
        duration = self.to_min_duration.value()
        self.signal_min_params_changed.emit(ramp_value, duration)

    def is_enabled(self) -> None:
        """Returns whether or not ramping is enabled."""
        return self.ramp_group_box.isChecked()
    
    def is_ramping(self) -> bool:
        return any([self.max_radio.isChecked(),
                    self.rest_radio.isChecked(),
                    self.min_radio.isChecked()])
    
    def get_values(self) -> dict:
        """
        Retrieves current values for ramp parameters and durations.

        Returns:
            dict: Dictionary containing ramp values and durations for 
                  max, rest, and min settings.
        """
        return {
            "ramp_max": self.ramp_max.value(),
            "to_max_duration": self.to_max_duration.value(),
            "ramp_rest": self.ramp_rest.value(),
            "to_rest_duration": self.to_rest_duration.value(),
            "ramp_min": self.ramp_min.value(),
            "to_min_duration": self.to_min_duration.value(),
        }
