from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox,
)

from .debounced_spin_box import DebouncedDoubleSpinBox
from .slide_toggle import SlideToggle
from ...utils.defaults import StimDefaults


class InstantaneousControlWidget(QWidget):
    signal_update_mode_changed = Signal(bool)
    signal_on_off_changed = Signal(bool)
    signal_frequency_changed = Signal(float)
    signal_amplitude_changed = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout()

        group_box = QGroupBox("Instantaneous Control")
        group_box_layout = QVBoxLayout()

        freq_layout = QHBoxLayout()
        freq_label = QLabel("Frequency (Hz)")
        self.freq_spinbox = DebouncedDoubleSpinBox(max_change_per_step=StimDefaults.FrequencyDefaults.MAX_INCREMENT_SIZE)
        self.freq_spinbox.valueChangedFinished.connect(self._handle_frequency_changed)
        self.freq_spinbox.setRange(0, StimDefaults.FrequencyDefaults.GLOBAL_MAXIMUM)
        self.freq_spinbox.setValue(StimDefaults.FrequencyDefaults.GLOBAL_FREQUENCY)

        freq_layout.addWidget(freq_label)
        freq_layout.addWidget(self.freq_spinbox)

        amp_layout = QHBoxLayout()
        amp_label = QLabel("Amplitude (mA)")
        self.amp_spinbox = DebouncedDoubleSpinBox(max_change_per_step=StimDefaults.AmplitudeDefaults.MAX_INCREMENT_SIZE)
        self.amp_spinbox.valueChangedFinished.connect(self._handle_amplitude_changed)

        self.amp_spinbox.setRange(0, StimDefaults.AmplitudeDefaults.GLOBAL_MAXIMUM)
        self.amp_spinbox.setValue(0)
        amp_layout.addWidget(amp_label)
        amp_layout.addWidget(self.amp_spinbox)

        on_off_layout = QHBoxLayout()
        onoff_label = QLabel("Stimulation:")
        onoff_button = SlideToggle()
        onoff_button.signal_toggled.connect(self.signal_on_off_changed.emit)
        on_off_layout.addWidget(onoff_label)
        on_off_layout.addWidget(onoff_button)

        update_layout = QHBoxLayout()
        update_label = QLabel("Live Update:")
        update_button = SlideToggle()
        update_button.signal_toggled.connect(self._handle_update_mode_changed)
        update_layout.addWidget(update_label)
        update_layout.addWidget(update_button)

        pause_button = QPushButton("Pause")
        self.update_button = QPushButton("Send Updates")
        self.update_button.clicked.connect(self._handle_update_button_clicked)

        group_box_layout.addLayout(freq_layout)
        group_box_layout.addLayout(amp_layout)
        group_box_layout.addLayout(on_off_layout)
        group_box_layout.addLayout(update_layout)
        group_box_layout.addWidget(self.update_button)
        group_box_layout.addWidget(pause_button)

        group_box.setLayout(group_box_layout)
        main_layout.addWidget(group_box)
        
        self.setLayout(main_layout)

    def _handle_update_button_clicked(self):
        self.signal_update_mode_changed.emit(True)
        self._handle_frequency_changed()
        self._handle_amplitude_changed()
        self.signal_update_mode_changed.emit(False)

    def _handle_frequency_changed(self):
        value = self.freq_spinbox.value()
        self.signal_frequency_changed.emit(value)

    def _handle_amplitude_changed(self):
        value = self.amp_spinbox.value()
        self.signal_amplitude_changed.emit(value)

    def _handle_update_mode_changed(self, are_updates_live: bool):
        if not are_updates_live:
            self.update_button.show()
        else:
            self.update_button.hide()
        self.signal_update_mode_changed.emit(are_updates_live)
