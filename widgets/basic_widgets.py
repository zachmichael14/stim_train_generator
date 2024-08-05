import numpy as np
from PySide6 import QtWidgets
from PySide6.QtCore import Signal

class SingleTextFieldWidget(QtWidgets.QWidget):
    """Widget for entering a single value via a text field."""
    signal_values_ready = Signal(np.ndarray)

    def __init__(self, text_input_label: str="Constant:"):
        """
        Initialize the SingleTextFieldWidget with a label and text field.
        
        Args:
            label (str): The label displayed next to the text field.
        """
        super().__init__()
        self.text_input = QtWidgets.QLineEdit()
        self.text_label = QtWidgets.QLabel(text_input_label)
        self.text_input.editingFinished.connect(self.input_received_callback)

        self.init_widget_layout(text_input_label)

    def init_widget_layout(self, text_input_label: str):
        main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(main_layout)    

        main_layout.addWidget(self.text_label)
        main_layout.addWidget(self.text_input)

    def input_received_callback(self):
        """
        Handle changes to the text field.

        Args:
            text (str): The current text in the input field.
        """
        text = self.text_input.text()

        if text.isnumeric():
            self.signal_values_ready.emit(np.array(float(text)))        

    def reset(self):
        """
        Clear the text field to reset the widget.
        """
        self.text_input.clear()

    def set_label_text(self, input_label: str):
        self.text_label.setText(input_label)


class LinearWidget(QtWidgets.QWidget):
    """Widget that allows users to specify a range for generating linearly
    spaced values."""

    signal_values_ready = Signal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.start_input = QtWidgets.QLineEdit()
        self.stop_input = QtWidgets.QLineEdit()
        self.points_input = QtWidgets.QLineEdit()

        self.init_widget_layout()

    def init_widget_layout(self):
        main_layout = QtWidgets.QVBoxLayout()

        input_label_map = {
            self.start_input: "Start:",
            self.stop_input: "Stop:",
            self.points_input: "Number of Points:",
        }
        for input, label in input_label_map.items():
            # Build sublayout for each attribute
            layout = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(f"{label}")
            layout.addWidget(label)
            layout.addWidget(input)
            main_layout.addLayout(layout)

            # Connect handler method to each attribute input field
            input.editingFinished.connect(self.input_received_callback)

        self.setLayout(main_layout)

    def input_received_callback(self):
        """
        Handle changes to any of the input fields.
        """
        start = self.start_input.text()
        stop = self.stop_input.text()
        number_of_points = self.points_input.text()

        # Only emit the signal when all inputs contain numerical values 
        if all([start.isnumeric(),
                stop.isnumeric(),
                number_of_points.isnumeric(),
                ]):

                start = float(start)
                stop = float(stop)
                try:
                    number_of_points = int(number_of_points)
                except ValueError as e:
                    print(f"Point is not int: {e}")

                self.signal_values_ready.emit(np.linspace(start, stop, number_of_points))

    def reset(self):
        """
        Clear all text fields to reset the widget.
        """
        self.start_input.clear()
        self.stop_input.clear()
        self.points_input.clear()


class FunctionWidget(QtWidgets.QWidget):
    """Widget for selecting a function from a dropdown menu."""

    signal_values_ready = Signal(np.ndarray)

    def __init__(self, options: list=["Option 1", "Option 2", "Option 3"]):
        """
        Initialize the FunctionWidget with a dropdown menu for function selection.

        Args:
            options (List[str]): List of options to display in the dropdown menu.
        """
        super().__init__()
        self.function_dropdown = QtWidgets.QComboBox()
        self.function_dropdown.addItems(options)
        self.function_dropdown.currentIndexChanged.connect(self.input_received_callback)

        self.init_widget_layout()

    def init_widget_layout(self):
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(self.function_dropdown)

        self.setLayout(main_layout)

    def input_received_callback(self):
        print("This is just a placeholder for now")
        self.signal_values_ready.emit(np.ndarray([]))

    def reset(self):
        """
        Reset the dropdown to the default option (first item).
        """
        self.function_dropdown.setCurrentIndex(0)


class ModeSelectorWidget(QtWidgets.QWidget):
    signal_mode_changed = Signal(str)

    def __init__(self):
        super().__init__()
        # As a QButtonGroup, mode_buttons makes buttons mutually exclusive
        self.mode_buttons = QtWidgets.QButtonGroup()

        self.init_widget_layout()

        # Set "Constant" mode as default
        self.mode_buttons.buttons()[0].setChecked(True)
        self.mode_buttons.buttonClicked.connect(self.mode_changed_callback)

    def init_widget_layout(self) -> None:
        button_layout = QtWidgets.QHBoxLayout()

        constant_button = QtWidgets.QRadioButton("Constant")
        self.mode_buttons.addButton(constant_button)
        button_layout.addWidget(constant_button)

        linear_button = QtWidgets.QRadioButton("Linear")
        self.mode_buttons.addButton(linear_button)
        button_layout.addWidget(linear_button)

        function_button = QtWidgets.QRadioButton("Function")
        self.mode_buttons.addButton(function_button)
        button_layout.addWidget(function_button)

        self.setLayout(button_layout)

    def mode_changed_callback(self) -> None:
        current_mode = self.mode_buttons.checkedButton().text()
        self.signal_mode_changed.emit(current_mode.lower())

    def reset(self) -> None:
        self.mode_buttons.buttons()[0].setChecked(True)

    def get_current_mode(self) -> str:
        return self.mode_buttons.checkedButton().text().lower()
