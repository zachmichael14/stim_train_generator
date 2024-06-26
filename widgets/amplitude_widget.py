import sys
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QMainWindow, QRadioButton, QButtonGroup, QLineEdit, QVBoxLayout

class ConstantWidget(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QHBoxLayout(self)

        self.amplitude_edit = QLineEdit(self)
        self.amplitude_edit.setPlaceholderText("Amplitude (mA)")

        main_layout.addWidget(self.amplitude_edit)
        self.setLayout(main_layout)

class RampWidget(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)

        self.amplitude_start_edit = QLineEdit(self)
        self.amplitude_start_edit.setPlaceholderText("Start (mA)")

        self.amplitude_stop_edit = QLineEdit(self)
        self.amplitude_stop_edit.setPlaceholderText("Start (mA)")

        self.amplitude_step_edit = QLineEdit(self)
        self.amplitude_step_edit.setPlaceholderText("Step")

        main_layout.addWidget(self.amplitude_start_edit)
        main_layout.addWidget(self.amplitude_stop_edit)
        main_layout.addWidget(self.amplitude_step_edit)

        self.setLayout(main_layout)    

class AmplitudeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.init_mode_selectors()

        # Constant radio button is by default
        self.subwidget = ConstantWidget()
        self.main_layout.addWidget(self.subwidget)

        self.setLayout(self.main_layout)


    
    def init_mode_selectors(self):
        self.constant_button = QRadioButton("Constant", self)
        self.constant_button.setChecked(True)

        self.ramp_button = QRadioButton("Ramp", self)
        self.function_button = QRadioButton("Function", self)

        self.mode_selector = QButtonGroup(self)
        self.mode_selector.addButton(self.constant_button)
        self.mode_selector.addButton(self.ramp_button)
        self.mode_selector.addButton(self.function_button)

        self.mode_selector.buttonClicked.connect(self.handle_mode_selector)

        self.main_layout.addWidget(self.constant_button)
        self.main_layout.addWidget(self.ramp_button)
        self.main_layout.addWidget(self.function_button)




    def handle_mode_selector(self, button: QRadioButton):
        if button == self.constant_button:
            self.subwidget = ConstantWidget()
        elif button == self.ramp_button:
            self.subwidget = RampWidget()
        else:
            self.subwidget = ""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()

    w = AmplitudeWidget()
    window.setCentralWidget(w)
    window.setWindowTitle("Stim Train Generator")
    window.show()

    sys.exit(app.exec())
