from PySide6.QtWidgets import QGridLayout, QGroupBox, QLabel, QLineEdit, QRadioButton, QVBoxLayout, QHBoxLayout, QWidget

from PySide6.QtCore import Signal, Slot
from ...utils.defaults import StimDefaults

class StimParameterWidget(QWidget):
    signal_parameter_toggled = Signal(bool)
    
    signal_max_updated = Signal(float)
    signal_rest_updated = Signal(float)
    signal_min_updated = Signal(float)

    signal_ramp_requested = Signal(float, float)

    def __init__(self,
                 parameter: str = "Amplitude", 
                 unit: str = "mA",
                 default_max: float = StimDefaults.AmplitudeDefaults.RAMP_MAX,
                 default_rest: float = StimDefaults.AmplitudeDefaults.RAMP_REST,
                 default_min: float = StimDefaults.AmplitudeDefaults.RAMP_MIN,
                 default_start_to_max: float = StimDefaults.GLOBAL_MIN_TO_MAX_RAMP_TIME,
                 default_rest_to_max: float = StimDefaults.GLOBAL_REST_TO_RAMP_TIME):
        super().__init__()
        self.unit = unit
        self.default_max = default_max
        self.default_rest = default_rest
        self.default_min = default_min

        layout = QVBoxLayout()

        # Main parameter group box
        group_box = QGroupBox(f"{parameter}")
        group_box.setCheckable(True)
        group_box.setChecked(False)
        group_layout = QGridLayout(group_box)
        group_box.toggled.connect(self._handle_parameter_toggled)
    
        self.max_radio = QRadioButton()
        self.rest_radio = QRadioButton()
        self.min_radio = QRadioButton()

        group_layout.addWidget(self.max_radio, 0, 1)
        group_layout.addWidget(self.rest_radio, 1, 1)
        group_layout.addWidget(self.min_radio, 2, 1)

        group_layout.addWidget(QLabel(f"Max ({self.unit}):"), 0, 2)
        group_layout.addWidget(QLabel(f"Rest ({self.unit}):"), 1, 2)
        group_layout.addWidget(QLabel(f"Min ({self.unit}):"), 2, 2)

        self.max_edit = QLineEdit(str(self.default_max))
        self.max_edit.setMaximumWidth(60)
        self.rest_edit = QLineEdit(str(self.default_rest))
        self.rest_edit.setMaximumWidth(60)
        self.min_edit = QLineEdit(str(self.default_min))
        self.min_edit.setMaximumWidth(60)

        group_layout.addWidget(self.max_edit, 0, 3)
        group_layout.addWidget(self.rest_edit, 1, 3)
        group_layout.addWidget(self.min_edit, 2, 3)


        self.slider_value_label = QLabel(f"Current: {self.default_rest} {self.unit}")
        group_layout.addWidget(self.slider_value_label, 0, 4, 1, 2)

        self.min_edit.editingFinished.connect(self._update_minimum)
        self.max_edit.editingFinished.connect(self.update_maximum)
        self.rest_edit.editingFinished.connect(self.update_rest_value)

        self.min_radio.toggled.connect(self.go_to_min)
        self.max_radio.toggled.connect(self.go_to_max)
        self.rest_radio.toggled.connect(self.go_to_rest)

        # Adding the Ramp Period section (incorporating the former RampPeriodWidget functionality)
        ramp_group_box = QGroupBox("Ramp Period (seconds)")
        ramp_group_layout = QVBoxLayout()

        from_start_layout = QHBoxLayout()
        from_rest_layout = QHBoxLayout()

        self.start_to_max_time = QLineEdit()
        self.start_to_max_time.setText(str(default_start_to_max))
        self.rest_to_max_time = QLineEdit()
        self.rest_to_max_time.setText(str(default_rest_to_max))

        from_start_layout.addWidget(QLabel("Start to Max:"))
        from_start_layout.addWidget(self.start_to_max_time)

        from_rest_layout.addWidget(QLabel("Rest to Max:"))
        from_rest_layout.addWidget(self.rest_to_max_time)

        ramp_group_layout.addLayout(from_start_layout)
        ramp_group_layout.addLayout(from_rest_layout)

        ramp_group_box.setLayout(ramp_group_layout)

        # Adding both the StimParameter group box and the RampPeriod group box to the main layout
        group_layout.addWidget(ramp_group_box, 5, 0, 1, -1)
        layout.addWidget(group_box)
        # layout.addWidget(ramp_group_box)

        self.setLayout(layout)

    @Slot(bool)
    def _handle_parameter_toggled(self, is_on: bool):
        self.signal_parameter_toggled.emit(is_on)

    @Slot(float)
    def _update_minimum(self) -> None:
        try:
            value = float(self.min_edit.text())
            self.signal_min_updated.emit(value)
            print(f"Updating minimum {value}")
        except ValueError:
            pass

    @Slot(float)
    def update_maximum(self) -> None:
        try:
            value = float(self.max_edit.text())
            self.signal_max_updated.emit(value)
        except ValueError:
            pass

    @Slot(float)
    def update_rest_value(self) -> None:
        try:
            value = float(self.rest_edit.text())
            if not self.min_edit.text() < value < self.max_edit.text():
                print("Rest value is not between min and max")
                pass
            self.signal_rest_updated.emit(value)
        except ValueError:
            pass

    def go_to_min(self) -> None:
        if self.min_radio.isChecked():
            print("Ramping to min")
            # minimum = float(self.min_edit.text())
            # time = float(self.min)
            # self.signal_ramp_requested(float(self.min_edit.text()), )

    def go_to_max(self) -> None:
        if self.max_radio.isChecked():
            print("Ramping to max")

    def go_to_rest(self) -> None:
        if self.rest_radio.isChecked():
            try:
                rest_value = float(self.rest_edit.text())
                print("Ramping to rest")
            except ValueError:
                pass
