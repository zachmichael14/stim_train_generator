import sys
from PySide6.QtWidgets import QApplication, QComboBox, QWidget, QHBoxLayout, QMainWindow, QRadioButton, QButtonGroup, QLineEdit, QVBoxLayout, QGroupBox

class ConstantWidget(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QHBoxLayout()

        self.amplitude_edit = QLineEdit()
        self.amplitude_edit.setPlaceholderText("Amplitude (mA)")
        main_layout.addWidget(self.amplitude_edit)

        self.setLayout(main_layout)


class RampWidget(QWidget):
    def __init__(self, parent: QWidget=None):
        super().__init__()        
        main_layout = QHBoxLayout()

        self.amplitude_start_edit = QLineEdit()
        self.amplitude_start_edit.setPlaceholderText("Start (mA)")

        self.amplitude_stop_edit = QLineEdit()
        self.amplitude_stop_edit.setPlaceholderText("Start (mA)")

        self.amplitude_step_edit = QLineEdit()
        self.amplitude_step_edit.setPlaceholderText("Step")

        main_layout.addWidget(self.amplitude_start_edit)
        main_layout.addWidget(self.amplitude_stop_edit)
        main_layout.addWidget(self.amplitude_step_edit)

        self.setLayout(main_layout)


class FunctionWidget(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QHBoxLayout()

        self.function_dropdown = QComboBox()
        self.function_dropdown.addItem("Fx 1")
        self.function_dropdown.addItem("Fx 2")
        self.function_dropdown.addItem("Fx 3")
    
        main_layout.addWidget(self.function_dropdown)

        self.setLayout(main_layout)


class IntervalWidget(QWidget):
    def __init__(self, title):
        super().__init__()
        self.title = title
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)

        # Create the GroupBox for Mode Settings
        self.mode_groupbox = QGroupBox(f"{self.title}")
        self.mode_layout = QVBoxLayout(self.mode_groupbox)

        self.init_mode_selectors()

        # Create a placeholder widget to hold the subwidget
        self.subwidget_container = QWidget()
        self.subwidget_layout = QVBoxLayout(self.subwidget_container)

        # Constant radio button is by default
        self.subwidget = ConstantWidget()
        self.subwidget_layout.addWidget(self.subwidget)

        self.mode_layout.addWidget(self.subwidget_container)
        self.main_layout.addWidget(self.mode_groupbox)
        self.setLayout(self.main_layout)
    
    def init_mode_selectors(self):
        selector_layout = QHBoxLayout()

        self.constant_button = QRadioButton("Constant", self)
        self.constant_button.setChecked(True)
        self.ramp_button = QRadioButton("Ramp", self)
        self.function_button = QRadioButton("Function", self)

        self.mode_selector = QButtonGroup(self)
        self.mode_selector.addButton(self.constant_button)
        self.mode_selector.addButton(self.ramp_button)
        self.mode_selector.addButton(self.function_button)

        self.mode_selector.buttonClicked.connect(self.handle_mode_selector)

        selector_layout.addWidget(self.constant_button)
        selector_layout.addWidget(self.ramp_button)
        selector_layout.addWidget(self.function_button)

        self.mode_layout.addLayout(selector_layout)
        
    def handle_mode_selector(self, button: QRadioButton):
        if button == self.constant_button:
            self.show_widget(ConstantWidget)
        elif button == self.ramp_button:
            self.show_widget(RampWidget)
        else:
            self.show_widget(FunctionWidget)

    def show_widget(self, widget_class: QWidget):
        new_subwidget = widget_class()
        self.subwidget_layout.replaceWidget(self.subwidget, new_subwidget)
        self.subwidget.deleteLater()
        self.subwidget = new_subwidget

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Create Amplitude IntervalWidget
        amplitude_widget = IntervalWidget("Amplitude Settings")
        main_layout.addWidget(amplitude_widget)

        # Create Pulse Interval IntervalWidget
        pulse_interval_widget = IntervalWidget("Pulse Interval Settings")
        main_layout.addWidget(pulse_interval_widget)

        self.setLayout(main_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()

    w = MainWidget()
    window.setCentralWidget(w)
    window.setWindowTitle("Stim Train Generator")
    window.show()

    sys.exit(app.exec())