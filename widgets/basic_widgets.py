import numpy as np
from PySide6 import QtWidgets

class SingleTextFieldWidget(QtWidgets.QWidget):

    """Widget for entering a single numeric value via a text field."""
    def __init__(self, label: str="Constant:"):
        """
        Initialize the SingleTextFieldWidget with a label and text field.
        
        Args:
            label (str): The label displayed next to the text field.
        """
        super().__init__()
        self.text_edit = QtWidgets.QLineEdit()

        main_layout = QtWidgets.QHBoxLayout()

        text_label = QtWidgets.QLabel(label)
        main_layout.addWidget(text_label)
        main_layout.addWidget(self.text_edit)

        self.setLayout(main_layout)    

    def get_values(self):
        """
        Retrieve the value entered in the text field.

        Returns:
            np.ndarray: A numpy array containing the single entered value.
        """
        try:
            return float(self.text_edit.text())
        except ValueError as e:
            print(f"SingleTextFieldWidget Error: {e}")


class LinearWidget(QtWidgets.QWidget):
    """Widget for specifying a range and generating linearly spaced values."""

    def __init__(self):
        super().__init__()
        self.start_edit = QtWidgets.QLineEdit()
        self.stop_edit = QtWidgets.QLineEdit()
        self.points_edit = QtWidgets.QLineEdit()

        main_layout = QtWidgets.QVBoxLayout()

        start_layout = QtWidgets.QHBoxLayout()
        start_label = QtWidgets.QLabel("Start:")
        start_layout.addWidget(start_label)
        start_layout.addWidget(self.start_edit)
        main_layout.addLayout(start_layout)

        stop_layout = QtWidgets.QHBoxLayout()
        stop_label = QtWidgets.QLabel("Stop:")
        stop_layout.addWidget(stop_label)
        stop_layout.addWidget(self.stop_edit)
        main_layout.addLayout(stop_layout)

        points_layout = QtWidgets.QHBoxLayout()
        points_label = QtWidgets.QLabel("Number of Points:")
        points_layout.addWidget(points_label)
        points_layout.addWidget(self.points_edit)
        main_layout.addLayout(points_layout)

        self.setLayout(main_layout)

    def get_values(self):
        """
        Retrieve the linearly spaced values based on user input.

        Returns:
            np.ndarray: A numpy array of linearly spaced values from start to stop.
        """
        try:
            start = float(self.start_edit.text())
            stop = float(self.stop_edit.text())
            points = int(self.points_edit.text())
            return np.linspace(start, stop, points)
        except ValueError as e:
            print(f"RampWidget Error: {e}")

    
class FunctionWidget(QtWidgets.QWidget):
    """Widget for selecting a function from a dropdown menu."""

    def __init__(self, options: list=["Option 1", "Option 2", "Option 3"]):
        """
        Initialize the FunctionWidget with a dropdown menu for function selection.

        Args:
            options (list): List of options to display in the dropdown menu.
        """
        super().__init__()
        self.function_dropdown = QtWidgets.QComboBox()
        self.function_dropdown.addItems(options)    

        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(self.function_dropdown)

        self.setLayout(main_layout)

    def get_values(self):
        """
        TODO: Eventually, this method will need to expose additional widgets
        that allow users to enter values for the chosen function's arguments.
        
        For now, it just retrieves the selected function name from the
        dropdown menu.

        Returns:
            dict: A dictionary containing the selected function name.
        """
        return {"function": self.function_dropdown.currentText()}
