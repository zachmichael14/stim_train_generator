from time import sleep
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
        self.stim_manager.signal_last_ramp_event.connect(self._handle_ramp_finished)

        self.electrode_selector.signal_electrode_selected.connect(self._handle_electrode_selected)

        self.instantaneous_widget.signal_on_off_changed.connect(self._handle_on_off_changed)
        self.instantaneous_widget.signal_update_mode_changed.connect(self._handle_update_mode_changed)
        self.instantaneous_widget.signal_update_button_clicked.connect(self._handle_update_button_clicked)

        self.frequency_widget.signal_current_value_changed.connect(self._handle_current_frequency_changed)
        self.frequency_widget.signal_ramp_params_changed.connect(self._handle_frequency_ramp_params_changed)
        self.frequency_widget.signal_ramp_requested.connect(self._handle_frequency_ramp_requested)
        self.frequency_widget.signal_check_radio_state.connect(self._handle_radio_state)

        self.amplitude_widget.signal_current_value_changed.connect(self._handle_current_amplitude_changed)
        self.amplitude_widget.signal_ramp_params_changed.connect(self._handle_amplitude_ramp_params_changed)
        self.amplitude_widget.signal_ramp_requested.connect(self._handle_amplitude_ramp_requested)
        self.amplitude_widget.signal_check_radio_state.connect(self._handle_radio_state)

    def _handle_radio_state(self):
        self._enable_ramp_radio_buttons(self.instantaneous_widget.is_on())

    @Slot(float)
    def _handle_update_button_clicked(self, duration: float):
        if duration == 0:
            self.stim_manager.apply_changes()
        else:
            current_frequency = self.stim_manager.events[0].frequency
            current_amplitude = self.stim_manager.events[0].amplitude

            new_frequency = self.stim_manager.staged_events[0].frequency
            new_amplitude = self.stim_manager.staged_events[0].amplitude
            
            frequency_ramp = self.ramp_calculator.generate_single_frequency_ramp(current_frequency, new_frequency, duration)


            # Use new frequency becuase frequency ramp will occur before amplitude ramp
            amplitude_ramp = self.ramp_calculator.generate_single_amplitude_ramp(current_amplitude, new_amplitude, duration, new_frequency)
            

            self.stim_manager.ramp_frequency_from_values(frequency_ramp)

            amplitude_events = [StimEvent(
                channel=self.stim_manager.current_channel,
                frequency=new_frequency,
                amplitude=amplitude,
                period = 1 / new_frequency
            ) for amplitude in amplitude_ramp
            ]

            self.stim_manager.staged_events = amplitude_events.copy()
    def _update_ui(self, event: StimEvent):
        self.frequency_widget.parameter_spinbox.setValue(event.frequency)
        self.amplitude_widget.parameter_spinbox.setValue(event.amplitude)

        self.frequency_widget.parameter_spinbox.setReadOnly(self.frequency_widget.is_ramping())
        self.amplitude_widget.parameter_spinbox.setReadOnly(self.amplitude_widget.is_ramping())

    def _handle_ramp_finished(self, event: StimEvent):
        self._handle_current_frequency_changed(event.frequency,
                                               self.frequency_widget.get_ramp_values())
        
        self.frequency_widget.deselect_ramp_buttons()
        self.amplitude_widget.deselect_ramp_buttons()   

        if self.stim_manager.staged_events:
            self.stim_manager.apply_changes()
     

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
        self._enable_ramp_radio_buttons(is_on)
        if is_on:
            self.stim_manager.start()
            self.electrode_selector.handle_stim_on()
        else:
            self.stim_manager.stop()

    def _enable_ramp_radio_buttons(self, is_on: bool):
        self.frequency_widget.set_all_radio_enabled_state(is_on)
        self.amplitude_widget.set_all_radio_enabled_state(is_on)

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
        self.stim_manager.set_frequency(new_value)
        
        if ramp_values:
            self._update_all_frequency_ramps(new_value, ramp_values)
       
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
        intermediates = self.ramp_calculator.generate_single_frequency_ramp(current_value, ramp_target_value, ramp_duration)

        if ramp_param in ["max", "rest", "min"]:
            setattr(self.stim_manager.frequency_ramp_values, ramp_param, intermediates)

    @Slot(str)
    def _handle_frequency_ramp_requested(self, ramp_direction: str):
        """Frequency ramp requested from current to ramp_direction"""
        self.stim_manager.ramp_frequency_from_direction(ramp_direction)

    @Slot(float)
    def _update_all_frequency_ramps(self,
                                new_value: float,
                                ramp_values: dict):
        """Current frequency changed when ramping."""
        ramp_values = self.ramp_calculator.generate_all_frequency_ramps(new_value, ramp_values)
        self.stim_manager.frequency_ramp_values = ramp_values

    @Slot(float, dict)
    def _handle_current_amplitude_changed(self,
                                          new_value: float,
                                          ramp_values: dict):
        """Current amplitude changed when not ramping."""
        self.stim_manager.set_amplitude(new_value)

        if ramp_values:
            self._update_all_amplitude_ramps()
    
    @Slot(str, float, float, float)
    def _handle_amplitude_ramp_params_changed(self,
                                              ramp_param: str,
                                              current_value: float,
                                              target_value: float,
                                              duration: float):
        """Only the max ramping intermediates need to be calculated"""
        current_frequency = self.frequency_widget.get_current_value()

        intermediates = self.ramp_calculator.generate_single_amplitude_ramp(
            current_value,
            target_value,
            duration,
            current_frequency)

        if ramp_param in ["max", "rest", "min"]:
            setattr(self.stim_manager.amplitude_ramp_values, ramp_param, intermediates)

    def _update_all_amplitude_ramps(self):
        """Recalculate amplitude values when frequency is changed.
        
        This method gets values directly from widgets rather than from signals because it's also called when frequency changes and those values aren't emitted.
        """
        current_frequency = self.frequency_widget.get_current_value()
        current_amplitude = self.amplitude_widget.get_current_value()
        ramp_values = self.amplitude_widget.get_ramp_values()
          
        intermediates = self.ramp_calculator.generate_all_amplitude_ramps(current_amplitude, ramp_values, current_frequency)
        self.stim_manager.amplitude_ramp_values = intermediates

    @Slot(str)
    def _handle_amplitude_ramp_requested(self, ramp_direction: str):
        """Frequency ramp requested from current to ramp_direction"""
        self.stim_manager.ramp_amplitude_from_direction(ramp_direction)
