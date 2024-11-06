from PySide6.QtCore import Slot
from PySide6.QtWidgets import QHBoxLayout, QWidget

from analog_streaming.managers.continuous_manager import ContinuousStimManager
from analog_streaming.core.data_classes import StimEvent
from analog_streaming.core.defaults import AmplitudeDefaults, FrequencyDefaults
from analog_streaming.widgets.composite_widgets.electrode_selector import ElectrodeSelectorWidget
from analog_streaming.widgets.composite_widgets.instantaneous_control import InstantaneousControlWidget
from analog_streaming.widgets.composite_widgets.stim_parameters import StimParameterWidget
from analog_streaming.utils.ramp_calculator import RampCalculator

class ContinuousStimWidget(QWidget):
    def __init__(self, continuous_stim_manager: ContinuousStimManager):
        super().__init__()

        self.stim_manager = continuous_stim_manager
        self.ramp_calculator = RampCalculator()

        self.electrode_selector = ElectrodeSelectorWidget()
        self.frequency_widget = StimParameterWidget(FrequencyDefaults.defaults,
                                                    parameter="Frequency",
                                                    unit="Hertz")
        self.amplitude_widget = StimParameterWidget(AmplitudeDefaults.defaults)
        self.instantaneous_widget = InstantaneousControlWidget()

        self._init_ui()
        self._connect_signals()
        
    def _init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.electrode_selector)
        main_layout.addWidget(self.frequency_widget)
        main_layout.addWidget(self.amplitude_widget)
        main_layout.addWidget(self.instantaneous_widget)
        self.setLayout(main_layout)

    def _connect_signals(self):
        self.stim_manager.signal_event_updated.connect(self._update_ui)

        self.electrode_selector.signal_electrode_selected.connect(self._handle_electrode_selected)

        self.instantaneous_widget.signal_on_off_changed.connect(self._handle_on_off_changed)
        self.instantaneous_widget.signal_update_mode_changed.connect(self._handle_update_mode_changed)

        self.frequency_widget.signal_current_value_changed.connect(self._handle_current_frequency_changed)
        self.frequency_widget.signal_ramp_params_changed.connect(self._handle_frequency_ramp_params_changed)
        self.frequency_widget.signal_ramp_requested.connect(self._handle_frequency_ramp_requested)

        self.amplitude_widget.signal_current_value_changed.connect(self._handle_current_amplitude_changed)
        self.amplitude_widget.signal_ramp_params_changed.connect(self._handle_amplitude_ramp_params_changed)
        self.amplitude_widget.signal_ramp_requested.connect(self._handle_amplitude_ramp_requested)

    def _update_ui(self, event: StimEvent):
        freq_ramp = self.frequency_widget.is_ramping()
        amp_ramp =  self.amplitude_widget.is_ramping()

        self.frequency_widget.parameter_spinbox.setReadOnly(freq_ramp)
        self.amplitude_widget.parameter_spinbox.setReadOnly(amp_ramp)

        if freq_ramp:
            self.frequency_widget.parameter_spinbox.setValue(event.frequency)
            self.stim_manager.set_frequency(event.frequency)

        if amp_ramp:
            self.amplitude_widget.parameter_spinbox.setValue(event.amplitude)
            self.stim_manager.set_amplitude(event.frequency)

    @Slot(int)
    def _handle_electrode_selected(self, channel: int):
        # -1 is deselection flag. Since no electrode is selected, stop stim
        if channel < 0:
            self.stim_manager.stop()
            self.instantaneous_widget.onoff_button.setChecked(False)
        else:
            self.stim_manager.set_channel(channel=channel)

    @Slot(bool)
    def _handle_on_off_changed(self, is_on):
        if is_on:
            self.stim_manager.start()
            self.electrode_selector.handle_stim_on()
        else:
            self.stim_manager.stop()

    @Slot(bool)
    def _handle_update_mode_changed(self, are_updates_live):
        # The signal from the toggle button is True if the button is not on the
        # default option (i.e., live updates).
        self.stim_manager.set_update_mode(are_updates_live=are_updates_live)

    @Slot(float, dict)
    def _handle_current_frequency_changed(self,
                                          new_value: float,
                                          ramp_values: dict = None):
        """Current frequency changed when not ramping."""
        if ramp_values:
            self._update_all_frequency_ramps(new_value, ramp_values)
        else:
            print("no ramp values, just change frequency")
        # Amplitude is only dependent on current frequency
        # So recalculate when current value changes        
        if self.amplitude_widget.is_enabled():
            self._update_all_amplitude_ramps()

    @Slot(str, float, float, float)
    def _handle_frequency_ramp_params_changed(self,
                                              ramp_param: str,
                                              current_value: float,
                                              ramp_target_value: float,
                                              ramp_duration: float):
        intermediates = self.ramp_calculator.generate_single_frequency_ramp(ramp_duration, current_value, ramp_target_value)
        print(f"Parameter {ramp_param} changed for frequency")

        # self.stim_manager.set_frequency_ramp_max(intermediates)

    @Slot(str)
    def _handle_frequency_ramp_requested(self, ramp_direction: str):
        """Frequency ramp requested from current to ramp_direction"""
        self.stim_manager.ramp_frequency(ramp_direction)

    @Slot(float)
    def _update_all_frequency_ramps(self,
                                new_value: float,
                                ramp_values: dict):
        """Current frequency changed when ramping."""

        print("Frequecy is ramping, calculate all ramp")
        # self.stim_manager.set_frequency(frequency=new_value)

        # ramp_values = self.ramp_calculator.generate_all_frequency_ramps(new_value, ramp_values)
        # self.stim_manager.frequency_ramp_values = ramp_values

        # if self.amplitude_widget.is_ramping():
        #     self._update_amplitude_ramps()

    @Slot(float, dict)
    def _handle_current_amplitude_changed(self,
                                          new_value: float,
                                          ramp_values: dict):
        """Current amplitude changed when not ramping."""
        if ramp_values:
            self._update_all_amplitude_ramps()
        else:
            print("no ramp values, just change amplitude")

    @Slot(str, float, float, float)
    def _handle_amplitude_ramp_params_changed(self,
                                              ramp_param: str,
                                              current_value: float,
                                              target_value: float,
                                              duration: float):
        """Only the max ramping intermediates need to be calculated"""
        current_amplitude = self.amplitude_widget.get_current_value()
        # intermediates = self.ramp_calculator.generate_single_amplitude_ramp(
        #     current_value,
        #     target_value,
        #     duration,
        #     current_)
        print(f"Parameter {ramp_param} changed for ampltidue")
        # self.stim_manager.set_amplitude_ramp_max(intermediates)

    def _update_all_amplitude_ramps(self):
        """Recalculate amplitude values when frequency is changed.
        
        This method gets values directly from widgets rather than from signals because it's also called when frequency changes and those values aren't emitted.
        """
        print("amplitude is ramping  calculate all")

        current_frequency = self.frequency_widget.get_current_value()
        current_amplitude = self.amplitude_widget.get_current_value()
        ramp_values = self.amplitude_widget.get_ramp_values()
          
        self.ramp_calculator.generate_all_amplitude_ramps(current_amplitude,
                                                          ramp_values,current_frequency)
        # self.stim_manager.amplitude_ramp_values = ramp_values


    @Slot(str)
    def _handle_amplitude_ramp_requested(self, ramp_direction: str):
        """Frequency ramp requested from current to ramp_direction"""
        self.stim_manager.ramp_amplitude(ramp_direction)