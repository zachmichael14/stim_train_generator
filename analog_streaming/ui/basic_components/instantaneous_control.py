from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QSpinBox, QDoubleSpinBox
)

from .slide_toggle import SlideToggle

class InstantaneousControlWidget(QWidget):
    signal_update_mode_changed = Signal(bool)
    signal_on_off_changed = Signal(bool)
    signal_frequency_changed = Signal(float)
    signal_amplitude_changed = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout()
        
        freq_layout = QHBoxLayout()
        freq_label = QLabel("Frequency")
        self.freq_spinbox = QDoubleSpinBox()
        self.freq_spinbox.editingFinished.connect(self._handle_frequency_changed)
        self.freq_spinbox.setRange(0, 500)
        self.freq_spinbox.setSuffix(" Hz")
        self.freq_spinbox.setValue(30)

        freq_layout.addWidget(freq_label)
        freq_layout.addWidget(self.freq_spinbox)
        
        amp_layout = QHBoxLayout()
        amp_label = QLabel("Amplitude")
        self.amp_spinbox = QSpinBox()
        self.freq_spinbox.editingFinished.connect(self._handle_amplitude_changed)

        self.amp_spinbox.setRange(0, 1000)
        self.amp_spinbox.setSuffix(" mA")
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
        update_button.signal_toggled.connect(self.signal_update_mode_changed.emit)
        update_layout.addWidget(update_label)
        update_layout.addWidget(update_button)

        pause_button = QPushButton("Pause")
        
        main_layout.addLayout(freq_layout)
        main_layout.addLayout(amp_layout)
        main_layout.addLayout(on_off_layout)
        main_layout.addLayout(update_layout)
        main_layout.addWidget(pause_button)
        
        self.setLayout(main_layout)

    def _handle_frequency_changed(self):
        value = self.freq_spinbox.value()
        self.signal_frequency_changed.emit(value)

    def _handle_amplitude_changed(self):
        value = self.amp_spinbox.value()
        self.signal_amplitude_changed.emit(value)
