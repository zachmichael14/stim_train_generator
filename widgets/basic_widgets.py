from typing import List

import numpy as np
from PySide6 import QtWidgets
from PySide6.QtCore import Signal

import generation_functions

class SingleTextFieldWidget(QtWidgets.QWidget):
    """Widget for entering a single value via a text field."""
    signal_values_ready = Signal(np.ndarray)

    def __init__(self, text_input_label: str = "Constant:") -> None:
        """
        Initialize the SingleTextFieldWidget with a label and text field.
        
        Args:
            label (str): The label displayed next to the text field.
        """
        super().__init__()
        self.text_input = QtWidgets.QLineEdit()
        self.text_label = QtWidgets.QLabel(text_input_label)
        self.text_input.editingFinished.connect(self.input_received_callback)

        self.init_widget_layout()

    def init_widget_layout(self) -> None:
        main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(main_layout)    

        main_layout.addWidget(self.text_label)
        main_layout.addWidget(self.text_input)

    def input_received_callback(self) -> None:
        """Handle user edits to the text field, ignoring non-numeric input."""
        text = self.text_input.text()

        # Only emit value when it's numeric
        if text.isnumeric():
            self.signal_values_ready.emit(np.array(float(text)))        

    def reset(self) -> None:
        """Clear the text field to reset the widget."""
        self.text_input.clear()

    def set_label_text(self, input_label: str):
        """Set the input field's label text."""
        self.text_label.setText(input_label)


class LinearWidget(QtWidgets.QWidget):
    """
    Widget that allows users to specify a range for generating linearly spaced
    values. 
    
    Range is inclusive, so stop input will be the last point in the range.
    """
    signal_values_ready = Signal(np.ndarray)

    def __init__(self) -> None:
        super().__init__()
        self.start_input = QtWidgets.QLineEdit()
        self.stop_input = QtWidgets.QLineEdit()
        self.points_input = QtWidgets.QLineEdit()

        self.init_widget_layout()

    def init_widget_layout(self) -> None:
        main_layout = QtWidgets.QVBoxLayout()

        input_label_map = {self.start_input: "Start:",
                           self.stop_input: "Stop:",
                           self.points_input: "Number of Points:",
                           }
        for input, label in input_label_map.items():
            # Build sublayout for each attribute
            label = QtWidgets.QLabel(f"{label}")

            layout = QtWidgets.QHBoxLayout()
            layout.addWidget(label)
            layout.addWidget(input)
            main_layout.addLayout(layout)

            input.editingFinished.connect(self.input_received_callback)

        self.setLayout(main_layout)

    def input_received_callback(self) -> None:
        """Handle changes to any input field, ignoring non-numeric input."""
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
                    print(f"Number of points is not an integer: {e}")

                self.signal_values_ready.emit(np.linspace(start, stop, number_of_points))

    def reset(self) -> None:
        """Clear all text fields to reset the widget."""
        self.start_input.clear()
        self.stop_input.clear()
        self.points_input.clear()


class FunctionWidget(QtWidgets.QWidget):
    """
    Widget for selecting a custom function from a dropdown menu.

    Selected functions expose input widgets for each of the function's
    parameters (as defined in generation_functions.py).
    """
    function_registry = generation_functions.FunctionRegistry()
    signal_values_ready = Signal(np.ndarray)

    def __init__(self,
                 options: List[str] = function_registry.get_class_names(),
                ) -> None:
        """
        Initialize the FunctionWidget with a dropdown menu for function selection.

        Args:
            options (List[str]): List of options to display in the dropdown menu.
        """
        super().__init__()
        self.main_layout = QtWidgets.QVBoxLayout()

        self.function_dropdown = QtWidgets.QComboBox()
        self.function_dropdown.addItems(options)
        self.function_dropdown.currentIndexChanged.connect(self.input_received_callback)
        self.main_layout.addWidget(self.function_dropdown)

        default_function = self.function_registry.get_class(self.function_dropdown.currentText())()
        self.function_subwidget = default_function.widget

        # TODO: Connect editing signals

        self.main_layout.addWidget(self.function_subwidget)   
        self.setLayout(self.main_layout)        

    def input_received_callback(self) -> None:
        """Delete previous widgets and display new function widgets."""
        selection = self.function_dropdown.currentText()
        new_function = self.function_registry.get_class(selection)()

        self.function_subwidget.deleteLater()
        self.function_subwidget = new_function.widget

        self.main_layout.addWidget(self.function_subwidget)
        
        # TODO: Connect editing signals
        
    def reset(self) -> None:
        """Reset the dropdown to the default option (first item)."""
        self.function_dropdown.setCurrentIndex(0)


class ModeSelectorWidget(QtWidgets.QWidget):
    """
    Widget that provides radio buttons for selecting one of three modes,
    where mode determines how values are to be generated.
    
    Available modes:
        - Constant: Use only a single value
        - Linear: Space values evenly between a start and stop value, inclusive
        - Function: uUse a custom function to generate values
    """
    signal_mode_changed = Signal(str)

    def __init__(self) -> None:
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
        """Set new mode as current mode and signal that mode has changed."""
        current_mode = self.mode_buttons.checkedButton().text()
        self.signal_mode_changed.emit(current_mode.lower())

    def reset(self) -> None:
        """Reset to Constant mode"""
        self.mode_buttons.buttons()[0].setChecked(True)

    def get_current_mode(self) -> str:
        """Return the current mode."""
        return self.mode_buttons.checkedButton().text().lower()
