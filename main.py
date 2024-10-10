import sys
import threading
import time
import heapq
from enum import Enum

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QSpinBox, QDoubleSpinBox, QApplication, QStyleFactory
)
import pandas as pd
from electrode_selector import ElectrodeSelectorWidget
from stim_parameter_widget import StimParameterWidget
from daq import DAQ
from slide_toggle import SlideToggle

class StimLoopMode(Enum):
    NO_LOOP = 1
    LOOP_LAST = 2
    LOOP_ALL = 3

class StimWorker:
    def __init__(self) -> None:
        self.running = False
        self.daq = DAQ()
        self.loop_mode = StimLoopMode.LOOP_ALL
        self.channel = None
        self.frequency = 2.0
        self.amplitude = 0.0
        self.scheduled_stim_events = [("foo", "barr", self.amplitude, (1/self.frequency))]
        self.uploaded_stims = pd.DataFrame(self.scheduled_stim_events)

    def run(self) -> None:
        self.running = True
        execution_delay_start_time = time.perf_counter()
        # timer_offset = 0.00001

        while self.running:
            if not self.scheduled_stim_events:
                self._handle_end_of_events()
                if not self.scheduled_stim_events:
                    break

            _, _, amplitude, expected_period = self.scheduled_stim_events[0]

            self.daq.set_channel(self.channel)
            self.daq.set_amplitude(amplitude)
            self.daq.trigger()

            self._precise_sleep(expected_period - (time.perf_counter() - execution_delay_start_time))
            
            heapq.heappop(self.scheduled_stim_events)
            execution_delay_start_time = time.perf_counter()

    def _precise_sleep(self, duration: float) -> None:
        end_time = time.perf_counter() + duration
        while time.perf_counter() < end_time:
            remaining = end_time - time.perf_counter()
            if remaining > 0.001:
                time.sleep(0.0005)
            else:
                pass

    def _handle_end_of_events(self) -> None:
        if self.loop_mode == StimLoopMode.NO_LOOP:
            return
        elif self.loop_mode == StimLoopMode.LOOP_LAST:
            last_stim = self.uploaded_stims.iloc[-1]
            self._schedule_single_event(last_stim)
        elif self.loop_mode == StimLoopMode.LOOP_ALL:
            self._schedule_all_events()

    def _schedule_all_events(self) -> None:
        for _, row in self.uploaded_stims.iterrows():
            self._schedule_single_event(row)

    def _schedule_single_event(self, stim_data):
        timepoint, frequency, amplitude, delay = stim_data
        heapq.heappush(self.scheduled_stim_events, (timepoint, frequency, amplitude, delay))

    def schedule_events(self, data):
        self.uploaded_stims = pd.DataFrame(data)
        self.scheduled_stim_events = []
        self._schedule_all_events()

    def set_parameters(self, channel=None, frequency=None, amplitude=None):
        if channel is not None:
            self.channel = channel
        if frequency is not None:
            self.frequency = frequency
        if amplitude is not None:
            self.amplitude = amplitude
        
        self.schedule_events([(0, self.frequency, self.amplitude, 1/self.frequency)])

    def set_mode(self, mode: StimLoopMode):
        self.loop_mode = mode

    def stop(self):
        self.running = False
        self.daq.zero_all()


class ContinuousStimManager(QObject):
    parameters_updated = Signal()

    def __init__(self):
        super().__init__()
        self.channel = None
        self.amplitude = 0.0
        self.frequency = 30.0
        self.worker = StimWorker()
        self.batch_updates = False
        self._running = False
        self._lock = threading.Lock()
        self._thread = None
        self._parameters_changed = False

    def start(self):
        print("Starting Thread")
        self._running = True
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        print("Stopping Thread")
        self._running = False
        self.worker.stop()
        if self._thread and self._thread.is_alive():
            self._thread.join()
        self._thread = None
        print("Thread stopped and joined.")

    def set_parameters(self,
                       channel: int = None,
                       frequency: float = None,
                       amplitude: float = None,
                       batch_updates: bool = None,
                       ):
        with self._lock:
            if channel is not None:
                self.channel = channel
            if frequency is not None:
                self.frequency = frequency
            if amplitude is not None:
                self.amplitude = amplitude
            if batch_updates is not None:
                self.batch_updates = batch_updates

            # Setting this to True assumes params are different from previous.
            # While this method shouldn't be called unless params are actually
            # changing, this assumption could be erroneous.
            self._parameters_changed = True

        if not self.batch_updates:
            self.apply_changes()

    def apply_changes(self):
        with self._lock:
            self.worker.set_parameters(self.channel,
                                       self.frequency,
                                       self.amplitude)
            # self.parameters_updated.emit()

    def _run(self):
        while self._running:
            if not self.batch_updates and self._parameters_changed:
                self.apply_changes()
                self._parameters_changed = False

            self.worker.run()


class StimControlWidget(QWidget):
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

class ContinuousStimWidget(QWidget):
    def __init__(self, continuous_stim_manager: ContinuousStimManager):
        super().__init__()
        self.stim_manager = continuous_stim_manager
        main_layout = QHBoxLayout()

        self.electrode_selector = ElectrodeSelectorWidget()
        self.electrode_selector.signal_electrode_selected.connect(self._handle_electrode_selected)

        self.amplitude_widget = StimParameterWidget()
        self.frequency_widget = StimParameterWidget(parameter="Frequency",
                                                    unit="Hz", default_max=100, default_rest=30, default_min=1)

        main_layout.addWidget(self.electrode_selector)
        main_layout.addWidget(self.amplitude_widget)
        main_layout.addWidget(self.frequency_widget)

        widget = StimControlWidget()
        widget.signal_update_mode_changed.connect(self._handle_update_mode_changed)
        widget.signal_on_off_changed.connect(self._handle_on_off_changed)
        main_layout.addWidget(widget)
        widget.signal_frequency_changed.connect(self._handle_frequency_changed)
        widget.signal_amplitude_changed.connect(self._handle_amplitude_changed)

        self.setLayout(main_layout)

    def _handle_electrode_selected(self, channel: int):
        self.stim_manager.set_parameters(channel=channel)

    def _handle_on_off_changed(self, is_on):
        if is_on:

            self.stim_manager.start()
        else:
            self.stim_manager.stop()

    def _handle_frequency_changed(self, frequency: float):
        self.stim_manager.set_parameters(frequency=frequency)

    def _handle_amplitude_changed(self, amplitude: float):
        print(f"setting amplitude")
        self.stim_manager.set_parameters(amplitude=amplitude)

    def _handle_update_mode_changed(self, is_batch_mode):
        # The signal from the toggle button is True if the button is not on the
        # default option (i.e., live updates).
        self.stim_manager.set_parameters(batch_updates=is_batch_mode)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create("Fusion"))

    continuous_stim_manager = ContinuousStimManager()
    main_window = ContinuousStimWidget(continuous_stim_manager)

    main_window.show()

    sys.exit(app.exec())