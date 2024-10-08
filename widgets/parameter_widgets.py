from typing import Dict, Type, Union

import numpy as np
from PySide6 import QtWidgets

from widgets import basic_widgets

class StimulationParameterWidget(QtWidgets.QWidget):
    """
    Widget for selecting a parameter generation function (i.e., mode).
    Appropriate input subwidgets will be displayed based on the selected mode.
    
    Modes:
        Constant: a single parameter value (default)

        Linear: multiple values that are spaced equally

        Function: values are generated by a custom function
    """

    # Map modes to their respective subwidgets
    MODE_MAP: Dict[str, Type[QtWidgets.QWidget]] = {
        "constant": basic_widgets.SingleTextFieldWidget,
        "linear": basic_widgets.LinearWidget,
        "function": basic_widgets.FunctionWidget,
    }

    def __init__(self, title: str):
        """
        Initialize the StimulationParameterWidget inside a border-box
        labeled with title.

        Args:
            title (str): title for the widget's border box
        """
        super().__init__()
        # Selected mode determines displayed input subwidget
        self.mode_selector_subwidget = basic_widgets.ModeSelectorWidget()
        self.mode_selector_subwidget.signal_mode_changed.connect(self.mode_changed_callback)

        self.input_subwidget = basic_widgets.SingleTextFieldWidget()
        self.input_subwidget.signal_values_ready.connect(self.input_ready_callback)
        self.input_values: np.ndarray = None

        self.subwidget_container_layout = QtWidgets.QVBoxLayout()

        # Visually wrap all subwidgets in a border-box labeled with title
        subwidget_container = QtWidgets.QGroupBox(f"{title}")
        subwidget_container.setLayout(self.subwidget_container_layout)

        self.subwidget_container_layout.addWidget(self.mode_selector_subwidget)
        self.subwidget_container_layout.addWidget(self.input_subwidget)
        
        # The subwidget container must be added to a parent layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(subwidget_container)
        self.setLayout(self.main_layout)

    def mode_changed_callback(self, mode: str) -> None:
        """
        Update the subwidget accordingly after a mode change.
        """
        self.show_subwidget(self.MODE_MAP[mode])

    def get_current_mode(self):
        return self.mode_selector_subwidget.get_current_mode()

    def show_subwidget(self, widget_class: Type[QtWidgets.QWidget]) -> None:
        """
        Replace the current subwidget with given subwidget.

        Args:
            widget_class (Type[QtWidgets.QWidget]): the class of the widget to display.
        """ 
        self.input_subwidget.deleteLater()

        self.input_subwidget = widget_class()
        self.input_subwidget.signal_values_ready.connect(self.input_ready_callback)
        self.subwidget_container_layout.addWidget(self.input_subwidget)

    def input_ready_callback(self, input_values: np.ndarray) -> None:
        self.input_values = input_values

    def reset(self) -> None:
        """
        Reset the widget to its default state.
        """
        self.mode_selector_subwidget.reset()
        self.show_subwidget(basic_widgets.SingleTextFieldWidget)
        self.input_subwidget.reset()


class AmplitudeParameterWidget(QtWidgets.QWidget):
    """
    Widget for selecting a amplitude generation function (i.e., mode).
    Appropriate input subwidgets will be displayed based on the selected mode.

    Some modes also require the user to specify how many repetitions of each
    unique amplitude should occur, which is unique to the amplitude widget as
    compared to other parameter widgets.
    
    Modes:
        Constant (default): a single parameter value
            - also displays a "Total Pulses" input subwidget

        Linear: multiple values that are spaced equally
            - also displays a "Pulses per Amplitude" input subwidget

        Function:  values are generated by a custom function
            - assumes function outputs all amplitudes; no additional subwidgets
    """
    # Map modes to their respective subwidgets
    MODE_MAP: Dict[str, Type[QtWidgets.QWidget]] = {
        "constant": basic_widgets.SingleTextFieldWidget,
        "linear": basic_widgets.LinearWidget,
        "function": basic_widgets.FunctionWidget,
    }

    def __init__(self, title: str):
        """
        Initialize the StimulationParameterWidget inside a border-box
        labeled with title.

        Args:
            title (str): Title for the widget's border box.
        """
        super().__init__()
        # Selected mode determines displayed input subwidget
        self.mode_selector_subwidget = basic_widgets.ModeSelectorWidget()
        self.mode_selector_subwidget.signal_mode_changed.connect(self.mode_changed_callback)

        self.input_subwidget = basic_widgets.SingleTextFieldWidget()
        self.input_subwidget.signal_values_ready.connect(self.input_ready_callback)
        self.input_values: np.ndarray = None

        self.repetition_subwidget = basic_widgets.SingleTextFieldWidget("Total Pulses:")
        self.repetition_subwidget.signal_values_ready.connect(self.repetitions_ready_callback)
        self.repetitions = 1 # A repetition of 1 means a single amplitude value

        self.subwidget_container_layout = QtWidgets.QVBoxLayout()

        # Visually wrap all subwidgets in a border-box labeled with title
        subwidget_container = QtWidgets.QGroupBox(f"{title}")
        subwidget_container.setLayout(self.subwidget_container_layout)

        self.subwidget_container_layout.addWidget(self.mode_selector_subwidget)
        self.subwidget_container_layout.addWidget(self.input_subwidget)
        self.subwidget_container_layout.addWidget(self.repetition_subwidget)
  
        # The subwidget container must be added to a parent layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(subwidget_container)
        self.setLayout(self.main_layout)

    def mode_changed_callback(self, mode: str) -> None:
        """
        Update the subwidget accordingly after a mode change.
        """
        self.show_subwidget(self.MODE_MAP[mode])
        self.show_repetition_subwidget(mode)

    def get_current_mode(self):
        return self.mode_selector_subwidget.get_current_mode()

    def show_subwidget(self, widget_class: Type[QtWidgets.QWidget]) -> None:
        """
        Replace the current subwidget with given subwidget.

        Args:
            widget_class (Type[QtWidgets.QWidget]): The class of the widget to display.
        """ 
        self.input_subwidget.deleteLater()

        self.input_subwidget = widget_class()
        self.input_subwidget.signal_values_ready.connect(self.input_ready_callback)
        self.subwidget_container_layout.addWidget(self.input_subwidget)

    def show_repetition_subwidget(self, mode: str) -> None:
        """
        Replace the current subwidget with given subwidget.

        Args:
            widget_class (Type[QtWidgets.QWidget]): The class of the widget to display.
        """
        # Deleting repetition subwiget first regardless of mode ensures
        # it still appears underneath input_subwidget after that widget
        # has been deleted
        if self.repetition_subwidget:
            self.repetition_subwidget.deleteLater()
            self.repetition_subwidget = None

        if mode == "constant":
            self.repetition_subwidget = basic_widgets.SingleTextFieldWidget("Total Pulses:")
            self.repetition_subwidget.signal_values_ready.connect(self.repetitions_ready_callback)
            self.subwidget_container_layout.addWidget(self.repetition_subwidget)
        elif mode == "linear":
            self.repetition_subwidget = basic_widgets.SingleTextFieldWidget("Pulses per Amplitude:")
            self.repetition_subwidget.signal_values_ready.connect(self.repetitions_ready_callback)
            self.subwidget_container_layout.addWidget(self.repetition_subwidget)
            
    def input_ready_callback(self, input_values: np.ndarray) -> None:
        self.input_values = np.repeat(input_values, self.repetitions)

    def repetitions_ready_callback(self, repetitions: np.ndarray) -> None:
        # Get int from array sent by repetition_subwidget
        self.repetitions = int(repetitions.item())
        
        # If repetitions is edited >1, overwrite previous array
        # (i.e., don't do repetitions of previous repetitions)
        if self.input_values is not None:
            amplitudes = np.unique(self.input_values)
            self.input_values = np.repeat(amplitudes, self.repetitions)

    def reset(self) -> None:
        """
        Reset the widget to its default state with "Constant" mode selected.
        """
        self.mode_selector_subwidget.reset()
        self.show_subwidget(basic_widgets.SingleTextFieldWidget)
        self.show_repetition_subwidget(self.mode_selector_subwidget.get_current_mode())
