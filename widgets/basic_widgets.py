from PySide6 import QtWidgets
import numpy as np

class ConstantWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.text_edit = QtWidgets.QLineEdit()
        self.init_ui()
    
    def init_ui(self):
        main_layout = QtWidgets.QHBoxLayout()

        text_label = QtWidgets.QLabel(f"Constant:")

        main_layout.addWidget(text_label)
        main_layout.addWidget(self.text_edit)

        self.setLayout(main_layout)

    def get_values(self):
        """Return 1-D numpy array."""
        try:
            return np.array(float(self.text_edit.text()))
        except ValueError as e:
            print(f"ConstantWidget Error: {e}")


class RampWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.start_edit = QtWidgets.QLineEdit()
        self.stop_edit = QtWidgets.QLineEdit()
        self.points_edit = QtWidgets.QLineEdit()
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout()
        start_layout = QtWidgets.QHBoxLayout()
        stop_layout = QtWidgets.QHBoxLayout()
        points_layout = QtWidgets.QHBoxLayout()

        start_label = QtWidgets.QLabel("Start:")
        stop_label = QtWidgets.QLabel("Stop:")
        points_label = QtWidgets.QLabel("Number of Points:")

        start_layout.addWidget(start_label)
        start_layout.addWidget(self.start_edit)
        stop_layout.addWidget(stop_label)
        stop_layout.addWidget(self.stop_edit)
        points_layout.addWidget(points_label)
        points_layout.addWidget(self.points_edit)
    
        main_layout.addLayout(start_layout)
        main_layout.addLayout(stop_layout)
        main_layout.addLayout(points_layout)

        self.setLayout(main_layout)

    def get_values(self):
        """Return a numpy array of linearly spaced values."""
        try:
            start = float(self.start_edit.text())
            stop = float(self.stop_edit.text())
            points = int(self.points_edit.text())

            return np.linspace(start, stop, points)
        except ValueError as e:
            print(f"RampWidget Error: {e}")

    def get_raw_values_dict(self):
        """Return a dictionary of user-entered values."""
        try:
            start = float(self.start_edit.text())
            stop = float(self.stop_edit.text())
            points = float(self.points_edit.text())

            return {
                "start": start,
                "stop": stop,
                "points": points,
            }
        except ValueError as e:
            print(f"RampWidget Error: {e}")

    
class FunctionWidget(QtWidgets.QWidget):
    def __init__(self, options: list=["Option 1", "Option 2", "Option 3"]):
        super().__init__()
        main_layout = QtWidgets.QHBoxLayout()

        self.function_dropdown = QtWidgets.QComboBox()
        self.function_dropdown.addItems(options)    
        main_layout.addWidget(self.function_dropdown)
        self.setLayout(main_layout)

    def get_values(self):
        return {"function": self.function_dropdown.currentText()}


class RepetitionWidget(QtWidgets.QWidget):
    def __init__(self, label_text):
        super().__init__()
        self.label = QtWidgets.QLabel(label_text)
        self.textbox = QtWidgets.QLineEdit()
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(self.label)
        main_layout.addWidget(self.textbox)
        self.setLayout(main_layout)

    def get_values(self):
        try:
            return int(self.textbox.text())
        except ValueError as e:
            print(f"RepetitionWidget Error: {e}")