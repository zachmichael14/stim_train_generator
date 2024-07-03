import sys
from PySide6.QtWidgets import QApplication, QComboBox, QWidget, QHBoxLayout, QMainWindow, QRadioButton, QButtonGroup, QLineEdit, QVBoxLayout, QGroupBox, QCheckBox, QGridLayout

from PySide6.QtCore import Signal
#If contstnat amplitude:
    # - number of unique Amps = 1
# if ramp:
    # calcualte number of unique amps stims


# if repetitions and 
    # calculate 


class ConstantWidget(QWidget):
    def __init__(self, placeholder_text: str="Constant value"):
        super().__init__()
        main_layout = QHBoxLayout()

        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText(placeholder_text)
        main_layout.addWidget(self.text_edit)

        self.setLayout(main_layout)

    def get_values(self):
        return {"constant": self.text_edit.text()}


class RampWidget(QWidget):
    def __init__(self,
                 start_placeholder_text: str="Start value",
                 stop_placeholder_text: str="Stop value",
                 step_placeholder_text: str="Step value"
                 ):
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

    def get_values(self):
        return {
            "start": self.start_edit.text(),
            "stop": self.stop_edit.text(),
            "step": self.step_edit.text()
        }


class FunctionWidget(QWidget):
    def __init__(self, options: list=["Option 1", "Option 2", "Option 3"]):
        super().__init__()
        main_layout = QHBoxLayout()

        self.function_dropdown = QComboBox()
        self.function_dropdown.addItems(options)    
        main_layout.addWidget(self.function_dropdown)
        self.setLayout(main_layout)

        # TODO: Will likely need methods for interacting with dropdown options
    def get_values(self):
        return {"function": self.function_dropdown.currentText()}


class IntervalWidget(QWidget):
    value_changed = Signal(dict)

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

        # Connect to the subwidget's textChanged signal if it's a QLineEdit
        if isinstance(new_subwidget, (ConstantWidget, RampWidget)):
            for child in new_subwidget.findChildren(QLineEdit):
                child.textChanged.connect(self.emit_value_changed)
        
        # Connect to the subwidget's currentTextChanged signal if it's a QComboBox
        elif isinstance(new_subwidget, FunctionWidget):
            new_subwidget.function_dropdown.currentTextChanged.connect(self.emit_value_changed)
    
    def emit_value_changed(self):
        # Emit the custom signal with the current values
        self.value_changed.emit(self.get_values())

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


class TrainLengthWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Create the GroupBox for Mode Settings
        main_layout = QVBoxLayout(self)
        self.groupbox = QGroupBox("Train Length Settings")
        self.groupbox_layout = QHBoxLayout(self.groupbox)

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
        groupbox = QGroupBox("Add Train to Channel(s)")
        groupbox_layout = QHBoxLayout(groupbox)

        for i in range(1, 9):
            checkbox = QCheckBox(f"Channel {i}")
            groupbox_layout.addWidget(checkbox)

        main_layout.addWidget(groupbox)
        self.setLayout(main_layout)


class MiscSettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        groupbox = QGroupBox("Miscellaneuous Settings")
        groupbox_layout = QVBoxLayout(groupbox)

        self.frequency_edit = QLineEdit()
        self.frequency_edit.setPlaceholderText("Frequency (Hz)")

        groupbox_layout.addWidget(self.frequency_edit)

        main_layout.addWidget(groupbox)

        self.setLayout(main_layout)


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QGridLayout(self)

        # Left side widgets (Amplitude Settings and Pulse Interval Settings)
        amplitude_widget = IntervalWidget("Amplitude Settings")
        pulse_length_widget = IntervalWidget("Pulse Length Settings")
        interpulse_interval = IntervalWidget("Inter-pulse Interval Settings")

        amplitude_widget.value_changed.connect(self.handle_interval_change)
        pulse_length_widget.value_changed.connect(self.handle_interval_change)
        interpulse_interval.value_changed.connect(self.handle_interval_change)

        main_layout.addWidget(amplitude_widget, 0, 0)
        main_layout.addWidget(pulse_length_widget, 1, 0)
        main_layout.addWidget(interpulse_interval, 2, 0)

        # Right side widgets (Train Length Widget and Misc Settings Widget)
        train_length_widget = TrainLengthWidget()
        misc_settings_widget = MiscSettingsWidget()

        main_layout.addWidget(train_length_widget, 0, 1)  # row 0, column 1
        main_layout.addWidget(misc_settings_widget, 1, 1)  # row 1, column 1

        # Bottom widget spanning full width (Channel Add Widget)
        channel_add_widget = ChannelAddWidget()

        main_layout.addWidget(channel_add_widget, 3, 0, 1, 2)  # row 2, spanning from column 0 to column 1

        self.setLayout(main_layout)

    def handle_interval_change(self, values):
        # This method will be called whenever an IntervalWidget's values change
        print("IntervalWidget changed:", values)

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtCore import Qt, QRectF, Signal

class StimTrainPlotter(QWidget):
    parameterChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 200)
        self.amplitude_settings = None
        self.pulse_interval_settings = None
        self.train_length_settings = None
        self.misc_settings = None
        self.channel_settings = None

    def update_parameters(self, amplitude_widget, pulse_length_widget, train_length_widget, misc_settings_widget, channel_add_widget):
        self.amplitude_settings = amplitude_widget
        self.pulse_interval_settings = pulse_length_widget
        self.train_length_settings = train_length_widget
        self.misc_settings = misc_settings_widget
        self.channel_settings = channel_add_widget
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if not all([self.amplitude_settings, self.pulse_interval_settings, self.train_length_settings, self.misc_settings, self.channel_settings]):
            painter.drawText(self.rect(), Qt.AlignCenter, "Waiting for parameters...")
            return

        self.draw_stim_train(painter)

    def draw_stim_train(self, painter):
        width = self.width()
        height = self.height()
        
        # Get parameters
        total_stims = int(self.train_length_settings.total_stim_edit.text() or "0")
        frequency = float(self.misc_settings.frequency_edit.text() or "0")
        pulse_width = float(self.misc_settings.pulse_width_edit.text() or "0")

        if total_stims == 0 or frequency == 0:
            painter.drawText(self.rect(), Qt.AlignCenter, "Invalid parameters")
            return

        # Calculate timings
        total_duration = (total_stims - 1) * (1000 / frequency) + pulse_width
        time_scale = width / total_duration

        # Draw time axis
        painter.drawLine(0, height - 20, width, height - 20)
        for i in range(0, int(total_duration) + 1, 100):
            x = i * time_scale
            painter.drawLine(int(x), height - 25, int(x), height - 15)
            painter.drawText(int(x) - 20, height - 5, f"{i}ms")

        # Draw stim pulses
        pulse_height = height * 0.6
        baseline = height * 0.7

        amplitude = self.get_amplitude()
        
        for i in range(total_stims):
            start_time = i * (1000 / frequency)
            x1 = start_time * time_scale
            x2 = (start_time + pulse_width) * time_scale
            
            painter.drawLine(int(x1), baseline, int(x1), baseline - pulse_height * amplitude)
            painter.drawLine(int(x1), baseline - pulse_height * amplitude, int(x2), baseline - pulse_height * amplitude)
            painter.drawLine(int(x2), baseline - pulse_height * amplitude, int(x2), baseline)

    def get_amplitude(self):
        if self.amplitude_settings.constant_button.isChecked():
            return float(self.amplitude_settings.subwidget.text_edit.text() or "0")
        elif self.amplitude_settings.ramp_button.isChecked():
            # For simplicity, we'll just use the start value of the ramp
            return float(self.amplitude_settings.subwidget.start_edit.text() or "0")
        else:
            # For function, we'll need to implement more complex logic
            return 1.0  # Placeholder

    def mousePressEvent(self, event):
        # Implement interactive features here
        pass

    def mouseReleaseEvent(self, event):
        self.parameterChanged.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()

    w = MainWidget()
    window.setCentralWidget(w)
    window.setWindowTitle("Stim Train Generator")
    window.show()

    sys.exit(app.exec())