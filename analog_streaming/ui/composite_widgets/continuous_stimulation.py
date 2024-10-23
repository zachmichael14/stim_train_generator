from PySide6.QtWidgets import QWidget, QHBoxLayout

from ..basic_components.electrode_selector import ElectrodeSelectorWidget
from ..basic_components.parameter_ramp import ParameterRampWidget
from ..basic_components.instantaneous_control import InstantaneousControlWidget
from analog_streaming.managers.continuous_manager import ContinuousStimManager

from ...utils.defaults import StimDefaults


class ContinuousStimWidget(QWidget):
    def __init__(self, continuous_stim_manager: ContinuousStimManager):
        super().__init__()

        self.stim_manager = continuous_stim_manager

        self.electrode_selector = ElectrodeSelectorWidget()
        self.frequency_widget = ParameterRampWidget(parameter="Frequency",
                                                    unit="Hz", default_max=StimDefaults.FrequencyDefaults.RAMP_MAX,
                                                    default_rest=StimDefaults.FrequencyDefaults.RAMP_REST,
                                                    default_min=StimDefaults.FrequencyDefaults.RAMP_MIN)
        self.amplitude_widget = ParameterRampWidget()
        self.instantaneous_widget = InstantaneousControlWidget()

        self._connect_signals()
        
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.electrode_selector)
        main_layout.addWidget(self.frequency_widget)
        main_layout.addWidget(self.amplitude_widget)
        main_layout.addWidget(self.instantaneous_widget)
        self.setLayout(main_layout)

    def _connect_signals(self):
        self.electrode_selector.signal_electrode_selected.connect(self._handle_electrode_selected)

        self.instantaneous_widget.signal_update_mode_changed.connect(self._handle_update_mode_changed)
        self.instantaneous_widget.signal_on_off_changed.connect(self._handle_on_off_changed)
        self.instantaneous_widget.signal_frequency_changed.connect(self._handle_frequency_changed)
        self.instantaneous_widget.signal_amplitude_changed.connect(self._handle_amplitude_changed)

        self.amplitude_widget.signal_parameter_toggled.connect(self._handle_amplitude_ramping)
        self.frequency_widget.signal_parameter_toggled.connect(self._handle_frequency_ramping)

    def _handle_frequency_ramping(self, parameter_is_on: bool):
        self.stim_manager.set_frequency_ramping(parameter_is_on)
        if not parameter_is_on:
            return
        
        if not self.amplitude_widget.is_enabled():
            print("Ramping frequency only")

    def _handle_amplitude_ramping(self, parameter_is_on: bool):
        self.stim_manager.set_amplitude_ramping(parameter_is_on)
        if not parameter_is_on:
            return
        
        if not self.frequency_widget.is_enabled():
            print("Ramping amplitude only")


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
        self.stim_manager.set_parameters(amplitude=amplitude)

    def _handle_update_mode_changed(self, are_updates_live):
        # The signal from the toggle button is True if the button is not on the
        # default option (i.e., live updates).
        self.stim_manager.set_parameters(are_updates_live=are_updates_live)