from typing import Dict, Type, Union

import numpy as np
from PySide6 import QtWidgets

from widgets import basic_widgets

class IntervalWidget(QtWidgets.QWidget):
    """
    Base widget for selecting and displaying different interval modes.
    """
    
    # Map modes to their respective widgets
    MODE_MAP: Dict[str, Type[QtWidgets.QWidget]] = {
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
        # Array of user-entered values from subwidget
        self.values: np.ndarray = None

        # Visually wraps widget in a border-box labeled with title
        self.widget_groupbox = QtWidgets.QGroupBox(f"{title}")
        self.groupbox_layout = QtWidgets.QVBoxLayout()
        self.widget_groupbox.setLayout(self.groupbox_layout)

        # TODO: Modify the way the sudwiget is display such that add and remove moethods cna also be used by amplitude widget to add/remove 
        # its repetition widget
        self.subwidget: Union[QtWidgets.QWidget, None] = None
        self.show_subwidget(basic_widgets.SingleTextFieldWidget)

        self.mode_selector_widget = basic_widgets.ModeSelectorWidget()
        self.mode_selector_widget.signal_mode_changed.connect(self.mode_changed_callback)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.mode_selector_widget)
        self.main_layout.addWidget(self.widget_groupbox)
        self.setLayout(self.main_layout)

    def mode_changed_callback(self, mode: str) -> None:
        """
        Handle the mode change by updating the subwidget accordingly and
        emitting a signal that the mode has changed.
        """
        mode = mode.lower()
        self.show_subwidget(self.MODE_MAP[mode])

    def show_subwidget(self, widget_class: Type[QtWidgets.QWidget]) -> None:
        """
        Replace the current subwidget with given subwidget.

        Args:
            widget_class (Type[QtWidgets.QWidget]): The class of the widget to display.
        """  
        if self.subwidget:
            self.remove_subwidget()

        subwidget = widget_class()
        subwidget.signal_values_ready.connect(self.process_values)
        self.subwidget = subwidget
        self.groupbox_layout.addWidget(self.subwidget)

    def remove_subwidget(self) -> None:
        """
        Remove and delete the current subwidget.
        """
        self.groupbox_layout.removeWidget(self.subwidget)
        self.subwidget.deleteLater()
        self.subwidget = None

    def process_values(self, values):
        """
        Process the values based on the current mode.

        Returns:
            np.ndarray: Processed values.
        """
        self.values = values

    def reset(self) -> None:
        """
        Reset the widget to its default state with "Constant" mode selected.
        """
        self.mode_selector_widget.reset()
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

        self.repetitions = 1 # There will always be >=1 amplitude
        print(self.repetitions)

        self.repetition_widget: Union[basic_widgets.SingleTextFieldWidget, None] = basic_widgets.SingleTextFieldWidget("Total Pulses:")
        self.repetition_widget.signal_values_ready.connect(self.process_repetions)

        self.groupbox_layout.addWidget(self.repetition_widget)


    def handle_mode_buttons(self) -> None:
        """
        Handle the mode change by updating the subwidget and repetition widgets
        accordingly.
        Overridden version of IntervalWidget's method.
        """        
        mode = self.get_current_mode()
        self.show_subwidget(self.MODE_MAP[mode])
        self.show_repetition_widget(mode)

    def show_repetition_widget(self, current_mode: str) -> None:
        """
        Show the repetition subwidget based on the current mode.

        Args:
            current_mode (str): The current mode of the widget.
        """
        # Remove previous subwidget first so if mode is function, the method
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
        self.repetition_widget.signal_values_ready.connect(self.process_repetions)
        self.groupbox_layout.addWidget(self.repetition_widget)

    def process_repetions(self, repetitions: np.ndarray):
            #SingleTextFieldWidget emits repetitions as np.ndarray
            self.repetitions = int(repetitions.item())

            if self.values and self.repetitions:
                self.values = np.repeat(self.values, self.repetitions)
    
    def remove_current_subwidget(self) -> None:
        """
        Remove and delete the current repetition subwidget.
        """
        self.groupbox_layout.removeWidget(self.repetition_widget)
        self.repetition_widget.deleteLater()
        self.repetition_widget = None

    def get_label_text(self, current_mode: str) -> str:
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
    
    def reset(self) -> None:
        """
        Reset the widget to its default state, including showing the repetition widget.
        """
        super().reset()
        self.show_repetition_widget(self.get_current_mode())