from PySide6.QtWidgets import QDoubleSpinBox, QGridLayout, QGroupBox, QLabel, QLineEdit, QRadioButton, QVBoxLayout, QWidget

from double_slider import DoubleSlider

class StimParameterWidget(QWidget):
    def __init__(self,
                 parameter: str = "Amplitude", 
                 unit: str = "mA",
                 default_max: float = 1.0,
                 default_rest: float = 0.5,
                 default_min: float = 0.0):
        super().__init__()
        self.unit = unit
        self.default_max = default_max
        self.default_rest = default_rest
        self.default_min = default_min

        layout = QVBoxLayout()

        group_box = QGroupBox(f"{parameter}")
        group_box.setCheckable(True)
        group_box.setChecked(False)
        group_layout = QGridLayout(group_box)
    
        self.slider = DoubleSlider()
        self.slider.setMinimum(self.default_min)
        self.slider.setMaximum(self.default_max)
        self.slider.setValue(self.default_rest)
        self.slider.signal_value_changed.connect(self.slider_callback)
        group_layout.addWidget(self.slider, 0, 0, 3, 1)

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

        self.step_spinbox = QDoubleSpinBox()
        self.step_spinbox.setRange(0.01, self.default_max)
        self.step_spinbox.setValue(1.00)
        self.step_spinbox.setDecimals(2)
        self.slider.setSingleStep(self.step_spinbox.value())

        group_layout.addWidget(QLabel(f"Step ({self.unit}):"), 4, 0, 1, 2)
        group_layout.addWidget(self.step_spinbox, 4, 2, 1, 2)

        self.slider_value_label = QLabel(f"Value: {self.default_rest} {self.unit}")
        group_layout.addWidget(self.slider_value_label, 0, 4, 1, 2)

        self.min_edit.editingFinished.connect(self.update_minimum)
        self.max_edit.editingFinished.connect(self.update_maximum)
        self.rest_edit.editingFinished.connect(self.update_rest_value)

        self.step_spinbox.valueChanged.connect(self.update_slider_step)

        self.min_radio.toggled.connect(self.go_to_min)
        self.max_radio.toggled.connect(self.go_to_max)
        self.rest_radio.toggled.connect(self.go_to_rest)

        self.slider.valueChanged.connect(self.update_slider_value_label)

        layout.addWidget(group_box)
        self.setLayout(layout)

    def slider_callback(self, value: float):
        self.slider_value_label.setText(f"Value: {value} {self.unit}")

    def update_minimum(self) -> None:
        try:
            value = float(self.min_edit.text())
            self.slider.setMinimum(value)
        except ValueError:
            pass

    def update_maximum(self) -> None:
        try:
            value = float(self.max_edit.text())
            self.slider.setMaximum(value)
            # A step that results in going higher than the max is illogical
            self.step_spinbox.setMaximum(value)
        except ValueError:
            pass

    def update_rest_value(self) -> None:
        try:
            rest_value = float(self.rest_edit.text())
            if self.slider.minimum() <= rest_value <= self.slider.maximum():
                self.rest_value = rest_value
        except ValueError:
            pass

    def update_slider_step(self, value) -> None:
        self.slider.setSingleStep(value)

    def go_to_min(self) -> None:
        if self.min_radio.isChecked():
            self.slider.setValue(self.slider.minimum())

    def go_to_max(self) -> None:
        if self.max_radio.isChecked():
            self.slider.setValue(self.slider.maximum())

    def go_to_rest(self) -> None:
        if self.rest_radio.isChecked():
            try:
                rest_value = float(self.rest_edit.text())
                self.slider.setValue(rest_value)
            except ValueError:
                pass

    def update_slider_value_label(self) -> None:
        current_value = self.slider.value()
        self.slider_value_label.setText(f"Value: {current_value:.2f} {self.unit}")
