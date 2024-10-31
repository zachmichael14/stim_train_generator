from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Slot

from ..basic_components.electrode_selector import ElectrodeSelectorWidget
from ..basic_components.stim_parameters import StimParameterWidget
from ..basic_components.instantaneous_control import InstantaneousControlWidget
from analog_streaming.managers.continuous_manager import ContinuousStimManager

from ...utils.defaults import AmplitudeDefaults, FrequencyDefaults
from ...utils.ramp_calculator import RampCalculator
from ...utils.data_classes import StimEvent


class ContinuousStimWidget(QWidget):
    def __init__(self, continuous_stim_manager: ContinuousStimManager):
        super().__init__()

        self.stim_manager = continuous_stim_manager
        self.ramp_calculator = RampCalculator()

        self.electrode_selector = ElectrodeSelectorWidget()
        self.frequency_widget = StimParameterWidget(FrequencyDefaults.defaults,
                                                    parameter="Frequency",
                                                    unit="Hz")
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
        self.frequency_widget.signal_calculate_ramp_values.connect(self._handle_frequency_ramp_calc)
        self.frequency_widget.signal_ramp_max_changed.connect(self._handle_frequency_max_calc)
        self.frequency_widget.signal_ramp_rest_changed.connect(self._handle_frequency_rest_calc)
        self.frequency_widget.signal_ramp_min_changed.connect(self._handle_frequency_min_calc)
        self.frequency_widget.signal_ramp_requested.connect(self._handle_frequency_ramp_requested)

        self.amplitude_widget.signal_current_value_changed.connect(self._handle_current_amplitude_changed)
        self.amplitude_widget.signal_calculate_ramp_values.connect(self._handle_amplitude_ramp_calc)
        self.amplitude_widget.signal_ramp_max_changed.connect(self._handle_amplitude_max_calc)
        self.amplitude_widget.signal_ramp_rest_changed.connect(self._handle_amplitude_rest_calc)
        self.amplitude_widget.signal_ramp_min_changed.connect(self._handle_amplitude_min_calc)
        self.amplitude_widget.signal_ramp_requested.connect(self._handle_amplitude_ramp_requested)

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
        else:
            self.stim_manager.stop()

    @Slot(bool)
    def _handle_update_mode_changed(self, are_updates_live):
        # The signal from the toggle button is True if the button is not on the
        # default option (i.e., live updates).
        self.stim_manager.set_update_mode(are_updates_live=are_updates_live)

    @Slot(float)
    def _handle_current_frequency_changed(self, new_value: float):
        """Current frequency changed when not ramping."""
        self.stim_manager.set_frequency(frequency=new_value)

    @Slot(float)
    def _handle_frequency_ramp_calc(self,
                                    new_value: float,
                                    ramp_values: dict):
        """Current frequency changed when ramping."""
        self.stim_manager.set_frequency(frequency=new_value)

        ramp_values = self.ramp_calculator.generate_all_frequency_ramps(new_value, ramp_values)
        self.stim_manager.frequency_ramp_values = ramp_values
    
    @Slot(float, float, float)
    def _handle_frequency_max_calc(self, 
                                   current_value: float,
                                   target_value: float,
                                   duration: float):
        """Only the max ramping intermediates need to be calculated"""
        intermediates = self.ramp_calculator.generate_single_frequency_ramp(duration, current_value, target_value)
        self.stim_manager.set_frequency_ramp_max(intermediates)

    @Slot(float, float, float)
    def _handle_frequency_rest_calc(self, 
                                   current_value: float,
                                   target_value: float,
                                   duration: float):
        """Only the rest ramping intermediates need to be calculated"""
        intermediates = self.ramp_calculator.generate_single_frequency_ramp(duration, current_value, target_value)
        self.stim_manager.set_frequency_ramp_rest(intermediates)
   
    @Slot(float, float, float)
    def _handle_frequency_min_calc(self, 
                                   current_value: float,
                                   target_value: float,
                                   duration: float):
        """Only the min ramping intermediates need to be calculated"""
        intermediates = self.ramp_calculator.generate_single_frequency_ramp(duration, current_value, target_value)
        self.stim_manager.set_frequency_ramp_min(intermediates)

    @Slot(str)
    def _handle_frequency_ramp_requested(self, ramp_direction: str):
        """Frequency ramp requested from current to ramp_direction"""
        self.stim_manager.ramp_frequency(ramp_direction)

    @Slot(float)
    def _handle_current_amplitude_changed(self, new_value: float):
        """Current amplitude changed when not ramping."""
        self.stim_manager.set_amplitude(amplitude=new_value)

    @Slot(float)
    def _handle_amplitude_ramp_calc(self,
                                    new_value: float,
                                    ramp_values: dict):
        """Current amplitude changed when ramping."""
        # ramp_values = self.ramp_calculator.generate_all_ramp_intermediates(new_value, ramp_values)
        self.stim_manager.amplitude_ramp_values = ramp_values

    @Slot(float, float, float)
    def _handle_amplitude_max_calc(self, 
                                   current_value: float,
                                   target_value: float,
                                   duration: float):
        """Only the max ramping intermediates need to be calculated"""
        # intermediates = self.ramp_calculator.generate_single_ramp_intermediates(duration, current_value, target_value)
        # self.stim_manager.set_amplitude_ramp_max(intermediates)

    @Slot(float, float, float)
    def _handle_amplitude_rest_calc(self, 
                                   current_value: float,
                                   target_value: float,
                                   duration: float):
        """Only the rest ramping intermediates need to be calculated"""
        # intermediates = self.ramp_calculator.generate_single_ramp_intermediates(duration, current_value, target_value)
        # self.stim_manager.set_amplitude_ramp_rest(intermediates)
   
    @Slot(float, float, float)
    def _handle_amplitude_min_calc(self, 
                                   current_value: float,
                                   target_value: float,
                                   duration: float):
        """Only the min ramping intermediates need to be calculated"""
        # intermediates = self.ramp_calculator.generate_single_ramp_intermediates(duration, current_value, target_value)
        # self.stim_manager.set_amplitude_ramp_min(intermediates)
    
    @Slot(str)
    def _handle_amplitude_ramp_requested(self, ramp_direction: str):
        print(f"amp ramp requested from current to {ramp_direction}")
        # self.stim_manager.ramp_amplitude(ramp_direction)

    def _update_ui(self, event: StimEvent):
        freq_ramp = self.frequency_widget.is_ramping()
        amp_ramp =  self.amplitude_widget.is_ramping()

        self.frequency_widget.parameter_spinbox.setReadOnly(freq_ramp)
        self.amplitude_widget.parameter_spinbox.setReadOnly(amp_ramp)

        if freq_ramp:
            self.frequency_widget.parameter_spinbox.setValue(event.frequency)

        if amp_ramp:
            self.amplitude_widget.parameter_spinbox.setValue(event.amplitude)

        