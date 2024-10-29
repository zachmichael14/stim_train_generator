from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QPushButton, QGroupBox, QToolButton
)

from .debounced_spin_box import DebouncedDoubleSpinBox
from .slide_toggle import SlideToggle
from ...utils.defaults import StimDefaults


class InstantaneousControlWidget(QWidget):
    signal_on_off_changed = Signal(bool)
    signal_pause_toggled = Signal(bool)
    signal_update_mode_changed = Signal(bool)
    signal_frequency_changed = Signal(float)
    signal_amplitude_changed = Signal(float)
    signal_toggle_thread_pause = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.onoff_button = SlideToggle()
        self.live_update_toggle = SlideToggle()

        # self.freq_spinbox = DebouncedDoubleSpinBox(max_increase=StimDefaults.FrequencyDefaults.MAX_INCREMENT_SIZE)
        # self.amp_spinbox = DebouncedDoubleSpinBox(max_increase=StimDefaults.AmplitudeDefaults.MAX_INCREMENT_SIZE)
        
        self.send_update_button = QPushButton("Send Updates")
        self.pause_button = QToolButton()

        self._setup_ui()
        self._set_widget_settings()
        self._connect_signals()

    def _setup_ui(self):
        main_layout = QVBoxLayout()
        group_box = QGroupBox("Instantaneous Control")
        form_layout = QFormLayout()

        form_layout.addRow("Stimulation:", self.onoff_button)
        form_layout.addRow("Live Update:", self.live_update_toggle)
        # form_layout.addRow("Frequency (Hz):", self.freq_spinbox)
        # form_layout.addRow("Amplitude (mA):", self.amp_spinbox)
        form_layout.addRow(self.send_update_button)
        form_layout.addRow(self.pause_button)

        group_box.setLayout(form_layout)
        main_layout.addWidget(group_box)
        self.setLayout(main_layout)

    def _set_widget_settings(self):
        # self.freq_spinbox.setRange(0, StimDefaults.FrequencyDefaults.GLOBAL_MAXIMUM)
        # self.freq_spinbox.setValue(StimDefaults.FrequencyDefaults.GLOBAL_FREQUENCY)

        # self.amp_spinbox.setRange(0, StimDefaults.AmplitudeDefaults.GLOBAL_MAXIMUM)
        # self.amp_spinbox.setValue(StimDefaults.AmplitudeDefaults.GLOBAL_AMPLITUDE)

        self.pause_button.setText("Pause Thread")
        # QToolButtons are slightly smaller than QPushButtons
        self.pause_button.setSizePolicy(self.send_update_button.sizePolicy())
        self.pause_button.setCheckable(True) 

    def _connect_signals(self):
        self.onoff_button.signal_toggled.connect(self._handle_on_off_toggle)
        self.live_update_toggle.signal_toggled.connect(self._handle_update_mode_changed)

        # self.freq_spinbox.signal_value_changed.connect(self._handle_frequency_changed)
        # self.amp_spinbox.signal_value_changed.connect(self._handle_amplitude_changed)

        self.send_update_button.clicked.connect(self._handle_update_button_clicked)
        self.pause_button.clicked.connect(self._handle_pause_button_clicked)

    def _handle_on_off_toggle(self, is_on: bool):
        self.signal_on_off_changed.emit(is_on)

    def _handle_pause_button_clicked(self, is_paused: bool):
        self.signal_pause_toggled.emit(is_paused)
        self.pause_button.setText("Resume Thread" if is_paused else "Pause Thread")

    def _handle_update_button_clicked(self):
        self.signal_update_mode_changed.emit(True)
        
        # self._handle_frequency_changed()
        # self._handle_amplitude_changed()
        self.signal_update_mode_changed.emit(False)

    # def _handle_frequency_changed(self):
    #     value = self.freq_spinbox.value()
    #     self.signal_frequency_changed.emit(value)

    # def _handle_amplitude_changed(self):
    #     value = self.amp_spinbox.value()
    #     self.signal_amplitude_changed.emit(value)

    def _handle_update_mode_changed(self, are_updates_live: bool):
        self.signal_update_mode_changed.emit(are_updates_live)
        # Button is only enable when updates are not live
        self.send_update_button.setEnabled(not are_updates_live)
        self.send_update_button.setText("Updates Are Live" if are_updates_live else "Send Updates")
