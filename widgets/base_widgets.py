from abc import abstractmethod

from PySide6 import QtWidgets
from PySide6 import QtCore

class ConstantWidget(QtWidgets.QWidget):
    def __init__(self, placeholder_text: str="Constant value"):
        super().__init__()
        main_layout = QtWidgets.QHBoxLayout()

        self.text_edit = QtWidgets.QLineEdit()
        self.text_edit.setPlaceholderText(placeholder_text)
        main_layout.addWidget(self.text_edit)

        self.setLayout(main_layout)

    def get_values(self):
        return {"constant": self.text_edit.text()}


class RampWidget(QtWidgets.QWidget):
    def __init__(self,
                 start_placeholder_text: str="Start value",
                 stop_placeholder_text: str="Stop value",
                 step_placeholder_text: str="Number of Points"
                 ):
        super().__init__()        
        main_layout = QtWidgets.QHBoxLayout()

        self.start_edit = QtWidgets.QLineEdit()
        self.start_edit.setPlaceholderText(start_placeholder_text)

        self.stop_edit = QtWidgets.QLineEdit()
        self.stop_edit.setPlaceholderText(stop_placeholder_text)

        self.points_edit = QtWidgets.QLineEdit()
        self.points_edit.setPlaceholderText(step_placeholder_text)

        main_layout.addWidget(self.start_edit)
        main_layout.addWidget(self.stop_edit)
        main_layout.addWidget(self.points_edit)

        self.setLayout(main_layout)

    def get_values(self):
        return {
            "start": self.start_edit.text(),
            "stop": self.stop_edit.text(),
            "points": self.points_edit.text()
        }


class FunctionWidget(QtWidgets.QWidget):
    def __init__(self, options: list=["Option 1", "Option 2", "Option 3"]):
        super().__init__()
        main_layout = QtWidgets.QHBoxLayout()

        self.function_dropdown = QtWidgets.QComboBox()
        self.function_dropdown.addItems(options)    
        main_layout.addWidget(self.function_dropdown)
        self.setLayout(main_layout)

    def get_values(self):
        return {"function": self.function_dropdown.currentText()}
        

class IntervalWidget(QtWidgets.QWidget):
    value_changed = QtCore.Signal(dict)
    mode_changed = QtCore.Signal(str)

    def __init__(self, title):
        super().__init__()
        self.title = title
        self.subwidget = None
        self.init_ui()
        
    def init_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.mode_groupbox = QtWidgets.QGroupBox(f"{self.title}")
        self.mode_layout = QtWidgets.QVBoxLayout(self.mode_groupbox)

        self.init_mode_selectors()

        self.subwidget_container = QtWidgets.QWidget()
        self.subwidget_layout = QtWidgets.QVBoxLayout(self.subwidget_container)

        # ConstantWidget is default
        self.subwidget = ConstantWidget()
        self.subwidget_layout.addWidget(self.subwidget)
        self.connect_subwidget_signals(self.subwidget)

        self.mode_layout.addWidget(self.subwidget_container)
        self.main_layout.addWidget(self.mode_groupbox)
        self.setLayout(self.main_layout)       

    def init_mode_selectors(self):
        selector_layout = QtWidgets.QHBoxLayout()

        self.constant_button = QtWidgets.QRadioButton("Constant", self)
        self.constant_button.setChecked(True)
        self.ramp_button = QtWidgets.QRadioButton("Ramp", self)
        self.function_button = QtWidgets.QRadioButton("Function", self)

        self.mode_selector = QtWidgets.QButtonGroup(self)
        self.mode_selector.addButton(self.constant_button)
        self.mode_selector.addButton(self.ramp_button)
        self.mode_selector.addButton(self.function_button)

        self.mode_selector.buttonClicked.connect(self.handle_mode_selector)

        selector_layout.addWidget(self.constant_button)
        selector_layout.addWidget(self.ramp_button)
        selector_layout.addWidget(self.function_button)

        self.mode_layout.addLayout(selector_layout)
        
    def handle_mode_selector(self, button: QtWidgets.QRadioButton):
        if button == self.constant_button:
            self.show_widget(ConstantWidget)
            self.mode_changed.emit
        elif button == self.ramp_button:
            self.show_widget(RampWidget)
        else:
            self.show_widget(FunctionWidget)

    def show_widget(self, widget_class: QtWidgets.QWidget):
        new_subwidget = widget_class()
        self.subwidget_layout.replaceWidget(self.subwidget, new_subwidget)
        self.subwidget.deleteLater()
        self.subwidget = new_subwidget
        self.connect_subwidget_signals(self.subwidget)

    def connect_subwidget_signals(self, widget):
        # Connect to the QLineEdit's textChanged signal
        if isinstance(widget, (ConstantWidget, RampWidget)):
            for child in widget.findChildren(QtWidgets.QLineEdit):
                child.textChanged.connect(self.validate_and_emit)
        
        # Connect to the QComboBox's currentTextChanged signal
        elif isinstance(widget, FunctionWidget):
            widget.function_dropdown.currentTextChanged.connect(self.validate_and_emit)

    def validate_and_emit(self):
        # Emit the custom signal with the current values
        values = self.get_values()
        if self.validate_values(values):
            self.value_changed.emit(values)

    def get_values(self):
        mode = self.get_current_mode()
        subwidget_values = self.subwidget.get_values()
        return {"mode": mode, "values": subwidget_values}
    
    def get_current_mode(self):
        if self.constant_button.isChecked():
            return "constant"
        elif self.ramp_button.isChecked():
            return "ramp"
        else:
            return "function"

    def validate_values(self, values):
        # Implement amplitude-specific validation
        if values["mode"].lower() == "constant":
            try:
                interval = float(values["values"]["constant"])
                # return 0 <= amplitude <= 100  # Example range
                return True
            except ValueError:
                return False
        elif values["mode"].lower() == "ramp":
            try:
                start = float(values["values"]["start"])
                stop = float(values["values"]["stop"])
                points = int(values["values"]["points"])
                return True
            except ValueError:
                return False
            
        elif values["mode"].lower() == "function":
            print("function selected")
            print(values["values"])

    def reset(self):
        self.constant_button.setChecked(True)
        self.show_widget(ConstantWidget)
        self.subwidget.text_edit.clear()

    @abstractmethod
    def handle_value_change(self):
        pass
