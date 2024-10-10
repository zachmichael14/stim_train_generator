from PySide6.QtWidgets import QDoubleSpinBox, QGridLayout, QGroupBox, QLabel, QLineEdit, QRadioButton, QVBoxLayout, QHBoxLayout, QTextEdit, QWidget

class StimParameterWidget(QWidget):
    def __init__(self,
                 parameter: str = "Amplitude", 
                 unit: str = "mA",
                 default_max: float = 1.0,
                 default_rest: float = 0.5,
                 default_min: float = 0.0,
                 default_start_to_max: float = 120,
                 default_rest_to_max: float = 10):
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

        self.min_edit.editingFinished.connect(self.update_minimum)
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

    def update_minimum(self) -> None:
        try:
            value = float(self.min_edit.text())
            print(f"Updating minimum {value}")
        except ValueError:
            pass

    def update_maximum(self) -> None:
        try:
            value = float(self.max_edit.text())
            print(f"Updating maximum {value}")

        except ValueError:
            pass

    def update_rest_value(self) -> None:
        try:
            rest_value = float(self.rest_edit.text())
            print(f"Updating rest value: ensure this is between min and max.")
        except ValueError:
            pass

    def go_to_min(self) -> None:
        if self.min_radio.isChecked():
            print("Ramping to min")

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

    def update_slider_value_label(self) -> None:
        print("Updating current value")
