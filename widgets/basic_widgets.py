from abc import ABC, ABCMeta, abstractmethod
from typing import Dict

from PySide6 import QtWidgets
from PySide6.QtCore import QObject, Signal

class QtABCMeta(type(QObject), ABCMeta):
    pass

class BaseWidget(ABC, metaclass=QtABCMeta):
    values_ready_signal = Signal(dict)

    @abstractmethod
    def handle_values_edited(self):
        """
        Handle changes to field values. Must be implemented in subclasses.
        """
        raise NotImplementedError("Subclasses must implement a `handle_values_edited` method.")

    @abstractmethod
    def get_values(self) -> Dict:
        """
        Retrieve current values. Must be implemented in subclasses.

        Returns:
            Dict: A dictionary of current values.
        """
        raise NotImplementedError("Subclasses must implement a `get_values` method.")

    @abstractmethod
    def reset(self):
        """
        Reset the widget to its default state. Must be implemented in subclasses.
        """
        raise NotImplementedError("Subclasses must implement a `reset` method.")

class SingleTextFieldWidget(QtWidgets.QWidget, BaseWidget):
    """Widget for entering a single numeric value via a text field."""

    def __init__(self, label: str="Constant:"):
        """
        Initialize the SingleTextFieldWidget with a label and text field.
        
        Args:
            label (str): The label displayed next to the text field.
        """
        QtWidgets.QWidget.__init__(self)
        BaseWidget.__init__(self)
        self.text: str = None
        self.text_input = QtWidgets.QLineEdit()
        self.text_input.textEdited.connect(self.handle_values_edited)

        main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(main_layout)    

        text_label = QtWidgets.QLabel(label)
        main_layout.addWidget(text_label)
        main_layout.addWidget(self.text_input)

    def handle_values_edited(self, text: str):
        self.text = text
        if self.text:
            self.values_ready_signal.emit(self.get_values())

    def get_values(self):
        """
        Retrieve the value entered in the text field.

        Returns:
            str: The value entered in the text field
        """
        return {"constant": self.text}

    def reset(self):
        """
        Clear the text field to reset the widget.
        """
        self.text_input.clear()


class LinearWidget(QtWidgets.QWidget, BaseWidget):
    """Widget for specifying a range for generating linearly spaced values."""
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        BaseWidget.__init__(self)
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

            # Connect handler method to each attribute input field
            input.editingFinished.connect(self.handle_values_edited)

    def handle_values_edited(self):
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


class FunctionWidget(QtWidgets.QWidget, BaseWidget):
    """Widget for selecting a function from a dropdown menu."""
    def __init__(self, options: list=["Option 1", "Option 2", "Option 3"]):
        """
        Initialize the FunctionWidget with a dropdown menu for function selection.

        Args:
            options (list): List of options to display in the dropdown menu.
        """
        QtWidgets.QWidget.__init__(self)
        BaseWidget.__init__(self)
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
        self.values_ready_signal.emit({"function": self.function_dropdown.currentText()})
        return {"function": self.function_dropdown.currentText()}

    def reset(self):
        """
        Reset the dropdown to the default option (first item).
        """
        self.function_dropdown.setCurrentIndex(0)