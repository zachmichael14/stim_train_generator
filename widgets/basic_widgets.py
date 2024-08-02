from abc import ABC, ABCMeta, abstractmethod
from typing import Dict

from PySide6 import QtWidgets
from PySide6.QtCore import QObject, Signal

class QtABCMeta(type(QObject), ABCMeta):
    """
    A metaclass that combines ABCMeta and QObject's metaclass to allow for
    creating abstract base classes that are compatible with PyQt's object system.
    """
    pass

class BaseWidget(ABC, metaclass=QtABCMeta):
    """
    An abstract base class for widgets that emit values.
    
    This class defines the interface for widgets that expose input fields to
    the user and retrieve current values for those fields. Values are emitted
    for by signal for processing elsewhere. These widgets can also be reset to
    a default state.
    """

    values_ready_signal = Signal(dict)

    @abstractmethod
    def handle_values_edited(self):
        """
        Handle changes to field values. This method should be called whenever
        the widget's values are edited.
        Must be implemented in subclasses.
        """
        raise NotImplementedError("Subclass must implement a `handle_values_edited` method.")

    @abstractmethod
    def get_values(self) -> Dict:
        """
        Retrieve current values. Must be implemented in subclasses.

        Returns:
            Dict: A dictionary of current values.
        """
        raise NotImplementedError("Subclass must implement a `get_values` method.")

    @abstractmethod
    def reset(self):
        """
        Reset the widget to its default state. This method should clear all
        fields or set them to default values.
        Must be implemented in subclasses.
        """
        raise NotImplementedError("Subclass must implement a `reset` method.")

class SingleTextFieldWidget(QtWidgets.QWidget, BaseWidget):
    """Widget for entering a single value via a text field."""

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
        """
        Handle changes to the text field.

        Args:
            text (str): The current text in the input field.
        """
        self.text = text
        if self.text:
            self.values_ready_signal.emit(self.get_values())

    def get_values(self):
        """
        Retrieve the value entered in the text field.

        Returns:
            Dict[str, str]: A dictionary with the key 'constant' and the entered value.
        """
        return {"constant": self.text}

    def reset(self):
        """
        Clear the text field to reset the widget.
        """
        self.text_input.clear()


class LinearWidget(QtWidgets.QWidget, BaseWidget):
    """Widget that allows users to specify a range for generating linearly
    spaced values."""

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
        """
        Handle changes to any of the input fields.
        """
        # Sender is the method caller (i.e, the widget calling the function)
        sender = self.sender()
        setattr(self, self.attribute_map[sender], sender.text())

        # Only emit the signal after all values have been edited
        if all([self.start, self.stop, self.points]):
            self.values_ready_signal.emit(self.get_values())

    def get_values(self):
        """
        Retrieve spacing values based on user input.

        Returns:
            Dict[str, str]: A dictionary containing 'start', 'stop', and 'points' values.
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
            options (List[str]): List of options to display in the dropdown menu.
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
        Retrieve the selected function name from the dropdown menu.

        TODO: Eventually, this method will need to expose additional widgets
        that allow users to enter values for the chosen function's arguments.

        Returns:
            Dict[str, str]: A dictionary containing the selected function name.
        """
        self.values_ready_signal.emit({"function": self.function_dropdown.currentText()})
        return {"function": self.function_dropdown.currentText()}

    def reset(self):
        """
        Reset the dropdown to the default option (first item).
        """
        self.function_dropdown.setCurrentIndex(0)
