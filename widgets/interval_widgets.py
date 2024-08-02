import numpy as np
from PySide6 import QtWidgets

from widgets import basic_widgets

## TODO: Using Enum for modes might be beneficial, 

class IntervalWidget(QtWidgets.QWidget):
    """
    Base widget for selecting and displaying different interval modes.
    """
    # Map modes to their respective widgets
    MODE_MAP = {
        "constant": basic_widgets.SingleTextFieldWidget,
        "linear": basic_widgets.LinearWidget,
        "function": basic_widgets.FunctionWidget,
    }

    def __init__(self, title: str):
        """
        Initialize the IntervalWidget with a title for the mode group.
        "Constant" mode is selected by default.

        Args:
            title (str): Title for the widget.
        """
        super().__init__()
        # Wraps entire widget in a box labeled with title
        self.widget_groupbox = QtWidgets.QGroupBox(f"{title}")

        # As a QButtonGroup, mode_buttons makes buttons mutually exclusive. 
        self.mode_buttons = QtWidgets.QButtonGroup(self.widget_groupbox)
        self.mode_buttons.buttonClicked.connect(self.handle_mode_buttons)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.init_mode_buttons()

        self.subwidget = None
        self.show_subwidget(basic_widgets.SingleTextFieldWidget)

        self.groupbox_layout = QtWidgets.QVBoxLayout()
        self.groupbox_layout.addLayout(self.button_layout)
        self.groupbox_layout.addWidget(self.subwidget)
        self.widget_groupbox.setLayout(self.groupbox_layout)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.widget_groupbox)
        self.setLayout(self.main_layout)

    def init_mode_buttons(self):
        for mode in self.MODE_MAP:
            button = QtWidgets.QRadioButton(mode.capitalize())
            self.mode_buttons.addButton(button)
            self.button_layout.addWidget(button)

        # Set "Constant" mode as default
        self.mode_buttons.buttons()[0].setChecked(True)

    def handle_mode_buttons(self):
        """
        Handle the mode change by updating the subwidget accordingly and
        emitting a signal that the mode has changed.

        Args:
            button (QtWidgets.QRadioButton): The button that was clicked.
        """
        mode = self.get_current_mode()
        self.show_subwidget(self.MODE_MAP[mode])

    def show_subwidget(self, widget_class: QtWidgets.QWidget):
        """
        Replace the current subwidget with given subwidget.

        Args:
            widget_class (QtWidgets.QWidget): The class of the widget to display.
        """  
        if self.subwidget:
            self.remove_subwidget()

        subwidget = widget_class()
        subwidget.values_ready_signal.connect(self.process_values)
        self.subwidget = subwidget

    def remove_subwidget(self):
        self.groupbox_layout.removeWidget(self.subwidget)
        self.subwidget.deleteLater()
        self.subwidget = None

    def process_values(self):
        sender = self.sender()

        function_map = {
            self.MODE_MAP["constant"]: self.get_constant_values,
            self.MODE_MAP["linear"]: self.get_linear_values,
            self.MODE_MAP["function"]: self.get_function_values,
        }

        values = function_map[type(sender)]()
        return values
    
    def get_constant_values(self):
        """
        Get values for constant mode.
        """
        constant_value = float(self.subwidget.get_values()['constant'])
        return np.array([constant_value])

    def get_linear_values(self):
        """
        Get values for linear mode.
        """
        values = self.subwidget.get_values()
        start = float(values['start'])
        stop = float(values['stop'])
        points = int(values['points'])
        return np.linspace(start, stop, points)

    def get_function_values(self):
        """
        Get values for function mode.
        Note: This is a placeholder as functions are not yet written
        """
        function_name = self.subwidget.get_values()['function']
        # For now, just return an empty array
        return np.array([])

    def get_current_mode(self):
        """
        Retrieve the currently selected mode.

        Returns:
            str: The current mode, which can be "constant", "linear", or "function".
        """
        return(self.mode_buttons.checkedButton().text().lower())

    def reset(self):
        """
        Reset the widget to its default state with "Constant" mode selected.
        """
        self.mode_buttons.buttons()[0].setChecked(True)
        self.show_subwidget(basic_widgets.SingleTextFieldWidget)
        self.subwidget.reset()


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
        self.repetition_widget = basic_widgets.SingleTextFieldWidget("Total Pulses:")
        self.groupbox_layout.addWidget(self.repetition_widget)

    def handle_mode_buttons(self):
        """
        Handle the mode change by updating the subwidget and repetition widgets
        accordingly.
        Overridden version of IntervalWidget's method.
        """        
        mode = self.get_current_mode()
        self.show_subwidget(self.MODE_MAP[mode])
        self.show_repetition_widget(mode)

    def show_repetition_widget(self, current_mode):
        """
        Show the repetition subwidget based on the current mode.
        """
        # Remove preivous subwidget first so if mode is function, the method
        # can return without a widget
        if self.repetition_widget:
            self.remove_current_subwidget()

        if current_mode == "function":
            # No subwidget for function mode currently
            # TODO: Eventually, this will need to display
            # fields for entering function arguments
            return

        label_text = self.get_label_text(current_mode)
        self.repetition_widget = basic_widgets.SingleTextFieldWidget(label_text)
        self.groupbox_layout.addWidget(self.repetition_widget)

    def remove_current_subwidget(self):
        """
        Remove and delete the current repetition subwidget.
        """
        self.groupbox_layout.removeWidget(self.repetition_widget)
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
        amplitudes = self.process_values()
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
