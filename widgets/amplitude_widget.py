import sys
from PySide6.QtWidgets import QApplication, QComboBox, QWidget, QHBoxLayout, QMainWindow, QRadioButton, QButtonGroup, QLineEdit, QVBoxLayout, QGroupBox, QCheckBox

class ConstantWidget(QWidget):
    def __init__(self, placeholder_text: str="Constant value"):
        super().__init__()
        main_layout = QHBoxLayout()

        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText(placeholder_text)
        main_layout.addWidget(self.text_edit)

        self.setLayout(main_layout)


class RampWidget(QWidget):
    def __init__(self,
                 start_placeholder_text: str="Start value",
                 stop_placeholder_text: str="Stop value",
                 step_placeholder_text: str="Step value"):
        super().__init__()        
        main_layout = QHBoxLayout()

        self.start_edit = QLineEdit()
        self.start_edit.setPlaceholderText(start_placeholder_text)

        self.stop_edit = QLineEdit()
        self.stop_edit.setPlaceholderText(stop_placeholder_text)

        self.step_edit = QLineEdit()
        self.step_edit.setPlaceholderText(step_placeholder_text)

        main_layout.addWidget(self.start_edit)
        main_layout.addWidget(self.stop_edit)
        main_layout.addWidget(self.step_edit)

        self.setLayout(main_layout)


class FunctionWidget(QWidget):
    def __init__(self, options: list=["Option 1", "Option 2", "Option 3"]):
        super().__init__()
        main_layout = QHBoxLayout()

        self.function_dropdown = QComboBox()
        self.function_dropdown.addItems(options)    
        main_layout.addWidget(self.function_dropdown)
        self.setLayout(main_layout)

        # TODO: Will likely need methods for interacting with dropdown options


class IntervalWidget(QWidget):
    def __init__(self, title):
        super().__init__()
        self.title = title
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.mode_groupbox = QGroupBox(f"{self.title}")
        self.mode_layout = QVBoxLayout(self.mode_groupbox)

        self.init_mode_selectors()

        # Create a placeholder widget to hold the subwidget
        self.subwidget_container = QWidget()
        self.subwidget_layout = QVBoxLayout(self.subwidget_container)

        # Constant radio button is by default
        self.subwidget = ConstantWidget()
        self.subwidget_layout.addWidget(self.subwidget)

        self.mode_layout.addWidget(self.subwidget_container)
        self.main_layout.addWidget(self.mode_groupbox)
        self.setLayout(self.main_layout)
    
    def init_mode_selectors(self):
        selector_layout = QHBoxLayout()

        self.constant_button = QRadioButton("Constant", self)
        self.constant_button.setChecked(True)
        self.ramp_button = QRadioButton("Ramp", self)
        self.function_button = QRadioButton("Function", self)

        self.mode_selector = QButtonGroup(self)
        self.mode_selector.addButton(self.constant_button)
        self.mode_selector.addButton(self.ramp_button)
        self.mode_selector.addButton(self.function_button)

        self.mode_selector.buttonClicked.connect(self.handle_mode_selector)

        selector_layout.addWidget(self.constant_button)
        selector_layout.addWidget(self.ramp_button)
        selector_layout.addWidget(self.function_button)

        self.mode_layout.addLayout(selector_layout)
        
    def handle_mode_selector(self, button: QRadioButton):
        if button == self.constant_button:
            self.show_widget(ConstantWidget)
        elif button == self.ramp_button:
            self.show_widget(RampWidget)
        else:
            self.show_widget(FunctionWidget)

    def show_widget(self, widget_class: QWidget):
        new_subwidget = widget_class()
        self.subwidget_layout.replaceWidget(self.subwidget, new_subwidget)
        self.subwidget.deleteLater()
        self.subwidget = new_subwidget

class TrainLengthWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Create the GroupBox for Mode Settings
        main_layout = QVBoxLayout(self)
        self.groupbox = QGroupBox("Train Length Settings")
        self.groupbox_layout = QVBoxLayout(self.groupbox)

        self.total_amplitude_edit = QLineEdit()
        self.total_amplitude_edit.setPlaceholderText("Total Number of Unique Amplitudes")

        self.amplitude_repetitions_edit = QLineEdit()
        self.amplitude_repetitions_edit.setPlaceholderText("Repetitions per Amplitude")

        self.total_stim_edit = QLineEdit()
        self.total_stim_edit.setPlaceholderText("Total Number of Stims")

        self.groupbox_layout.addWidget(self.total_stim_edit)
        self.groupbox_layout.addWidget(self.total_amplitude_edit)
        self.groupbox_layout.addWidget(self.amplitude_repetitions_edit)
        self.groupbox_layout.addWidget(self.total_stim_edit)

        main_layout.addWidget(self.groupbox)
        self.setLayout(main_layout)

class ChannelAddWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Create the GroupBox for Mode Settings
        main_layout = QVBoxLayout(self)
        self.groupbox = QGroupBox("Add Train to Channel(s)")
        self.groupbox_layout = QHBoxLayout(self.groupbox)


        for i in range(1, 9):
            checkbox = QCheckBox(f"Channel {i}")
            self.groupbox_layout.addWidget(checkbox)


        main_layout.addWidget(self.groupbox)
        self.setLayout(main_layout)


class MiscSettingWidget(QWidget)

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Create Amplitude IntervalWidget
        amplitude_widget = IntervalWidget("Amplitude Settings")
        main_layout.addWidget(amplitude_widget)

        # Create Pulse Interval IntervalWidget
        pulse_interval_widget = IntervalWidget("Pulse Interval Settings")
        main_layout.addWidget(pulse_interval_widget)

        train_length_widget = TrainLengthWidget()
        main_layout.addWidget(train_length_widget)

        channel_add_widget = ChannelAddWidget()
        main_layout.addWidget(channel_add_widget)

        self.setLayout(main_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()

    w = MainWidget()
    window.setCentralWidget(w)
    window.setWindowTitle("Stim Train Generator")
    window.show()

    sys.exit(app.exec())