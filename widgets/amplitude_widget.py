import sys
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QMainWindow, QRadioButton, QButtonGroup

class AmplitudeWidget(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QHBoxLayout(self)

        # Create radio buttons
        self.constant_button = QRadioButton("Constant", self)
        self.ramp_button = QRadioButton("Ramp", self)
        self.function_button = QRadioButton("Function", self)

        # Create a button group for the radio buttons
        self.mode_selector = QButtonGroup(self)
        self.mode_selector.addButton(self.constant_button)
        self.mode_selector.addButton(self.ramp_button)
        self.mode_selector.addButton(self.function_button)

        main_layout.addWidget(self.constant_button)
        main_layout.addWidget(self.ramp_button)
        main_layout.addWidget(self.function_button)


        self.setLayout(main_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()

    w = AmplitudeWidget()
    window.setCentralWidget(w)
    window.setWindowTitle("Stim Train Generator")
    window.show()

    sys.exit(app.exec())
