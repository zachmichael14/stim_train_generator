from PySide6 import QtWidgets

from .basic_widgets import ModeSelectorWidget
import widgets.type_widgets
import generation_functions

class StimTypeSelector(QtWidgets.QWidget):
    function_registry = generation_functions.FunctionRegistry()

    STIM_TYPE_MAP = {
        "pulse": widgets.type_widgets.PulseWidget,
        "burst": QtWidgets.QLabel,
        "continous": widgets.type_widgets.ContinousWidget,
    }

    def __init__(self):
        super().__init__()
        self.current_subwidget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout()


        self.init_main_layout()
        self.set_subwidget()
        
    def init_main_layout(self):
        self.setLayout(self.main_layout)

        modes = ["Pulse", "Burst", "Continous"]

        self.mode_widget = ModeSelectorWidget(modes)
        self.mode_widget.signal_mode_changed.connect(self.type_changed_callback)
        self.main_layout.addWidget(self.mode_widget)
        self.main_layout.addWidget(self.current_subwidget)


    def set_subwidget(self):
        self.current_subwidget.deleteLater()
        current_mode = self.mode_widget.get_current_mode()
        widget_class = self.STIM_TYPE_MAP[current_mode]
        self.current_subwidget = widget_class()
        self.main_layout.addWidget(self.current_subwidget)


    def type_changed_callback(self):
        self.set_subwidget()