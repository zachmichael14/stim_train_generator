import sys
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QMainWindow, QRadioButton, QButtonGroup

class AmplitudeWidget(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QHBoxLayout(self)

        self.constant_button = QRadioButton("Constant", self)
        self.ramp_button = QRadioButton("Ramp", self)
        self.function_button = QRadioButton("Function", self)

        self.mode_selector = QButtonGroup(self)
        self.mode_selector.addButton(self.constant_button)
        self.mode_selector.addButton(self.ramp_button)
        self.mode_selector.addButton(self.function_button)

        self.mode_selector.buttonClicked.connect(self.handle_mode_selector)

        main_layout.addWidget(self.constant_button)
        main_layout.addWidget(self.ramp_button)
        main_layout.addWidget(self.function_button)

        self.setLayout(main_layout)

    def handle_mode_selector(self, button):
        if button == self.constant_button:
            print("constant")
        elif button == self.ramp_button:
            print("ramp")
        else:
            print("function_button")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()

    w = AmplitudeWidget()
    window.setCentralWidget(w)
    window.setWindowTitle("Stim Train Generator")
    window.show()

    sys.exit(app.exec())
