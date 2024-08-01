from PySide6 import QtWidgets
from PySide6.QtCore import Signal

class SingleTextFieldWidget(QtWidgets.QWidget):
    """Widget for entering a single numeric value via a text field."""
    values_ready_signal= Signal(str)

    def __init__(self, label: str="Constant:"):
        """
        Initialize the SingleTextFieldWidget with a label and text field.
        
        Args:
            label (str): The label displayed next to the text field.
        """
        super().__init__()
        self.text: str = None
        self.text_input = QtWidgets.QLineEdit()
        self.text_input.textEdited.connect(self.handle_field_edited)

        main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(main_layout)    

        text_label = QtWidgets.QLabel(label)
        main_layout.addWidget(text_label)
        main_layout.addWidget(self.text_input)

    def handle_field_edited(self, text: str):
        self.text = text
        if self.text:
            self.values_ready_signal.emit(self.text)

    def get_values(self):
        """
        Retrieve the value entered in the text field.

        Returns:
            str: The value entered in the text field
        """
        return self.text

    def reset(self):
        """
        Clear the text field to reset the widget.
        """
        self.text_input.clear()


class LinearWidget(QtWidgets.QWidget):
    """Widget for specifying a range for generating linearly spaced values."""
    values_ready_signal = Signal(dict)

    def __init__(self):
        super().__init__()
        self.start: str = None
        self.stop: str = None
        self.points: str = None

        self.start_input = QtWidgets.QLineEdit()
        self.stop_input = QtWidgets.QLineEdit()
        self.points_input = QtWidgets.QLineEdit()

        # Attribute map allows inputs to be mapped to attributes dyamically;
        # it's especially useful when handling edits to inputs
        self.attribute_map = {
            self.start_input: "start",
            self.stop_input: "stop",
            self.points_input: "points",
        }

        self.init_main_layout()

    def init_main_layout(self):
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        for input, label in self.attribute_map.items():
            # Build sublayout for each attribute
            layout = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(f"{label.capitalize()}:")
            layout.addWidget(label)
            layout.addWidget(input)
            main_layout.addLayout(layout)

            # Connect handler to inputs
            input.editingFinished.connect(self.handle_field_edited)

    def handle_field_edited(self):
        # Sender is the method caller (i.e, the widget calling the function)
        sender = self.sender()
        setattr(self, self.attribute_map[sender], sender.text())

        if all([self.start, self.stop, self.points]):
            self.values_ready_signal.emit(self.get_values())

    def get_values(self):
        """
        Retrieve the linearly spaced values based on user input.

        Returns:
            np.ndarray: A numpy array of linearly spaced values from start to stop.
        """
        return {"start": self.start, "stop": self.stop, "points": self.points}

    def reset(self):
        """
        Clear all text fields to reset the widget.
        """
        self.start_input.clear()
        self.stop_input.clear()
        self.points_input.clear()


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
        self.setLayout(main_layout)

        main_layout.addWidget(self.function_dropdown)

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

    def reset(self):
        """
        Reset the dropdown to the default option (first item).
        """
        self.function_dropdown.setCurrentIndex(0)