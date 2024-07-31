from abc import abstractmethod

import numpy as np
from PySide6 import QtWidgets
from PySide6.QtCore import Signal

from widgets import basic_widgets

## TODO: Using Enum for modes might be beneficial, 
## but it also seems to impact readability a bit. It's worth looking into more.

## TODO: It also might be worth factoring out the mode_changed signal from the 
## base class into the AmplitudeWidget class since that is the only subclass
## that makes use of that signal.

class IntervalWidget(QtWidgets.QWidget):
    """
    Base widget for selecting and displaying different interval modes.
    
    Attributes:
        mode_changed (QtCore.Signal): Signal emitted when the mode is changed.
            This is primarily used by the AmplitudeWidget subclass for
            conditionally displaying an additional amplitude repetition widget.

        subwidget (QtWidgets.QWidget): Current subwidget based on the selected
            mode.
    """
    mode_changed = Signal()

    def __init__(self, title: str):
        """
        Initialize the IntervalWidget with a title for the mode group.
        "Constant" mode is selected by default.

        Args:
            title (str): Title for the widget.
        """
        super().__init__()
        self.constant_button = QtWidgets.QRadioButton("Constant", self)
        self.constant_button.setChecked(True)
        self.linear_button = QtWidgets.QRadioButton("Linear", self)
        self.function_button = QtWidgets.QRadioButton("Function", self)

        # Default to constant mode
        self.subwidget = basic_widgets.SingleTextFieldWidget()  
        subwidget_container = QtWidgets.QWidget()
        self.subwidget_layout = QtWidgets.QVBoxLayout(subwidget_container)
        self.subwidget_layout.addWidget(self.subwidget)

        self.init_main_layout(title, subwidget_container)

    def init_main_layout(self,
                         title: str,
                         subwidget_container: QtWidgets.QWidget):
        """
        Initialize the main layout for the widget.

        Args:
            title (str): Title for the mode group.
            subwidget_container (QtWidgets.QWidget): Container for the subwidget.
        """
        main_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(main_layout)

        mode_groupbox = QtWidgets.QGroupBox(f"{title}")
        mode_layout = QtWidgets.QVBoxLayout(mode_groupbox)

        # As a QButtonGroup, mode_selector makes buttons mutually exclusive. 
        mode_selector = QtWidgets.QButtonGroup(self)
        mode_selector.buttonClicked.connect(self.handle_mode_selector)
        mode_selector.addButton(self.constant_button)
        mode_selector.addButton(self.linear_button)
        mode_selector.addButton(self.function_button)

        selector_layout = QtWidgets.QHBoxLayout()
        selector_layout.addWidget(self.constant_button)
        selector_layout.addWidget(self.linear_button)
        selector_layout.addWidget(self.function_button)
        mode_layout.addLayout(selector_layout)

        mode_layout.addWidget(subwidget_container)

        main_layout.addWidget(mode_groupbox)

    def handle_mode_selector(self, button: QtWidgets.QRadioButton):
        """
        Handle the mode change by updating the subwidget accordingly and
        emitting a signal that the mode has changed.

        Args:
            button (QtWidgets.QRadioButton): The button that was clicked.
        """
        button_map = {
            self.constant_button: basic_widgets.SingleTextFieldWidget,
            self.linear_button: basic_widgets.LinearWidget,
            self.function_button: basic_widgets.FunctionWidget,
        }

        self.show_new_subwidget(button_map[button])
        self.mode_changed.emit()

    def show_new_subwidget(self, widget_class: QtWidgets.QWidget):
        """
        Replace the current subwidget with given subwidget.

        Args:
            widget_class (QtWidgets.QWidget): The class of the widget to display.
        """
        self.subwidget.deleteLater()
        new_subwidget = widget_class()
        self.subwidget_layout.replaceWidget(self.subwidget, new_subwidget)
        self.subwidget = new_subwidget

    def get_current_mode(self):
        """
        Retrieve the currently selected mode.

        Returns:
            str: The current mode, which can be "constant", "linear", or "function".
        """
        if self.constant_button.isChecked():
            return "constant"
        elif self.linear_button.isChecked():
            return "linear"
        else:
            return "function"
        
    def reset(self):
        """
        Reset the widget to its default state with "Constant" mode selected.
        """
        self.constant_button.setChecked(True)
        self.show_new_subwidget(basic_widgets.SingleTextFieldWidget)
        self.subwidget.reset()

    def get_values(self):
        """
        Retrieve subwidget values.

        Returns:
            The values from the subwidget.
        """
        values = self.subwidget.get_values()
        return values


class AmplitudeWidget(IntervalWidget):
    """
    Widget for configuring amplitude settings, including repetition.

    Inherits from IntervalWidget and includes an additional subwidget
    for configuring repetition settings based on the current mode.
    """

    def __init__(self):
        """
        Initialize the AmplitudeWidget with a title and connect mode change signal.
        """
        super().__init__("Amplitude Settings")
        self.repetition_widget = None

        self.show_repetition_widget()
        self.mode_changed.connect(self.show_repetition_widget)

    def show_repetition_widget(self):
        """
        Show the repetition subwidget based on the current mode.
        """
        if self.repetition_widget:
            self.remove_current_subwidget()

        current_mode = self.get_current_mode()
        if current_mode == "function":
            # No subwidget for function mode
            return
        
        label_text = self.get_label_text(current_mode)
        self.repetition_widget = basic_widgets.SingleTextFieldWidget(label_text)
        self.subwidget_layout.addWidget(self.repetition_widget)

    def remove_current_subwidget(self):
        """
        Remove and delete the current repetition subwidget.
        """
        self.subwidget_layout.removeWidget(self.repetition_widget)
        self.repetition_widget.deleteLater()
        self.repetition_widget = None

    def get_label_text(self, current_mode):
        """
        Get the label text for the repetition subwidget based on the current mode.

        Args:
            current_mode (str): The current mode of the widget.

        Returns:
            str: The label text for the repetition subwidget.
        """
        if current_mode == "constant":
            label_text = "Total Pulses:"
        elif current_mode == "linear":
            label_text = "Pulses per Amplitude:"
        return label_text
    
    def get_values(self):
        """
        Retrieve the amplitude values and repetition settings.

        Returns:
            np.ndarray: An array of amplitude values repeated according to the repetition settings.
        """
        amplitudes = self.subwidget.get_values()
        repetitions = 1

        if self.repetition_widget:
            repetitions = self.repetition_widget.get_values()
        return np.repeat(amplitudes, repetitions)
    
    def reset(self):
        """
        Reset the widget to its default state, including showing the repetition widget.
        """
        super().reset()
        self.show_repetition_widget()
