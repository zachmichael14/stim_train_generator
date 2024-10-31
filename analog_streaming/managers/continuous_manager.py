import threading
from typing import Optional

from PySide6.QtCore import QObject, Signal

from ..utils.data_classes import RampValues, StimEvent
from ..utils.defaults import AmplitudeDefaults, FrequencyDefaults
from ..workers.stim_worker import StimWorker


class ContinuousStimManager(QObject):
    """
    Manages continuous stimulation parameters and event generation.

    Handles parameter updates and event staging through a threaded worker,
    with support for live updates and frequency ramping.
    """
    signal_event_updated = Signal(StimEvent)

    def __init__(self) -> None:
        """
        Initializes manager with default stimulation parameters and threading setup.
        """
        super().__init__()

        self.current_channel: int = 0
        self.current_amplitude: float = AmplitudeDefaults.defaults["global_value"]
        self.current_frequency: float = FrequencyDefaults.defaults["global_value"]
        self.current_period: float = 1 / self.current_frequency

        # Ramp intervals values 
        self.frequency_ramp_values: Optional[RampValues] = None
        self.amplitude_ramp_values: Optional[RampValues] = None
        
        # Event management queues
        self.staged_events: list[StimEvent] = []
        self.events: list[StimEvent] = [StimEvent(self.current_channel,
                                                  self.current_frequency,
                                                  self.current_amplitude,
                                                  self.current_period)]

        self.worker: StimWorker = StimWorker(self)

        # Threading and state management
        self.are_updates_live: bool = False
        self._running: bool = False
        self._lock: threading.Lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None
        self._parameters_changed: bool = False

    def start(self) -> None:
        """Initializes and starts the worker thread."""
        print("Starting Thread")
        self._running = True
        self._thread = threading.Thread(target=self._run,
                                        daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """
        Stops the worker thread and ensures cleanup.
        
        Blocks until thread termination is confirmed.
        """
        print("Stopping Thread")
        self._running = False
        self.worker.stop()
        if self._thread and self._thread.is_alive():
            self._thread.join()
        self._thread = None
        print("Thread stopped and joined.")

    def get_next_event(self) -> StimEvent:
        """
        Retrieves the next stimulation event and updates GUI.
        
        Returns:
            The next stimulation event to process.
        """
        # For single events, reuse the same event for continuous stim
        if len(self.events) == 1:
            stim_event = self.events[0]
        else:
            stim_event = self.events.pop(0)
        
        # Notify UI to update with new event values
        # This is emitted when the thread worker calls this method
        self.signal_event_updated.emit(stim_event)
        return stim_event
    
    def set_channel(self, channel: int):
        with self._lock:
            self.current_channel = channel
            self._parameters_changed_callback()

    def set_amplitude(self, amplitude: float):
        with self._lock:
            self.current_amplitude = amplitude
            self._parameters_changed_callback()

    def set_frequency(self, frequency: float):
        with self._lock:
            self.current_frequency = frequency
            self._parameters_changed_callback()

    def _parameters_changed_callback(self):
        self._parameters_changed = True
        self._stage_new_stim_event()

        if self.are_updates_live:
            self.apply_changes()

    def _stage_new_stim_event(self, clear_previous: bool = True):
        if clear_previous:
            self.staged_events.clear()
    
        event = StimEvent(
                self.current_channel, 
                self.current_frequency,
                self.current_amplitude,
                1/self.current_frequency
        )
        self.staged_events.append(event)


    # def set_parameters(self,
    #                   channel: Optional[int] = None,
    #                   frequency: Optional[float] = None,
    #                   amplitude: Optional[float] = None) -> None:
    #     """
    #     Updates stimulation parameters and prepares new events.
        
    #     Only provided parameters are updated. Changes are staged and
    #     applied based on the update mode.
    #     """
    #     with self._lock:
    #         if channel is not None:
    #             self.current_channel = channel
    #         if frequency is not None:
    #             self.current_frequency = frequency
    #         if amplitude is not None:
    #             self.current_amplitude = amplitude

    #         self._parameters_changed = True
    #         self.staged_events.clear()
    #         event = StimEvent(
    #             self.current_channel, 
    #             self.current_frequency,
    #             self.current_amplitude,
    #             1/self.current_frequency
    #         )
    #         self.staged_events.append(event)

    #     if self.are_updates_live:
    #         self.apply_changes()

    def set_update_mode(self, are_updates_live: bool) -> None:
        """
        Configures whether parameter changes are applied immediately.
        
        Args:
            are_updates_live: If True, changes are applied as they occur
        """
        self.are_updates_live = are_updates_live

        # If live, apply any changes made since toggled off
        if self.are_updates_live:
            self.apply_changes()

    def apply_changes(self) -> None:
        """Applies staged parameter changes under thread lock protection."""
        with self._lock:
            if self.staged_events:
                self.events = self.staged_events.copy()

    def _run(self) -> None:
        """
        Main thread loop that processes parameter updates and runs the worker.
        
        Monitors for parameter changes in live update mode.
        """
        while self._running:
            if self._parameters_changed:
                print("paremetes changed")
                self.apply_changes()
                self._parameters_changed = False

            self.worker.run()

    def ramp_frequency(self, ramp_direction: str) -> None:
        """
        Creates a series of events to smoothly transition frequency.
        
        Args:
            ramp_destination: Target of ramp ("max", "rest", or "min")
        """
        if not self.frequency_ramp_values:
            return
        
        print("ramp frequency called")
            
        # Select ramp values based on destination
        if ramp_direction.casefold() == "max":
            ramp_values = self.frequency_ramp_values.current_to_max
        elif ramp_direction.casefold() == "rest":
            ramp_values = self.frequency_ramp_values.current_to_rest
        else:
            ramp_values = self.frequency_ramp_values.current_to_min
        
        self.events.clear()
    
        # Generate events for each frequency step
        self.events = [
            StimEvent(
                channel=self.current_channel,
                frequency=freq,
                amplitude=self.current_amplitude,
                period=1 / freq
            ) for freq in ramp_values
        ]

    def ramp_amplitude(self, ramp_direction: str) -> None:
        print("gonna ramp amplitude")

    def set_frequency_ramp_max(self, ramp_values: list):
        if not self.frequency_ramp_values:
            print("No frequency ramp values.")
            return
        self.frequency_ramp_values.current_to_max = ramp_values

    def set_frequency_ramp_rest(self, ramp_values: list):
        if not self.frequency_ramp_values:
            print("No frequency ramp values.")
            return
        self.frequency_ramp_values.current_to_rest = ramp_values
    
    def set_frequency_ramp_min(self, ramp_values: list):
        if not self.frequency_ramp_values:
            print("No frequency ramp values.")
            return
        self.frequency_ramp_values.current_to_min = ramp_values
    
    def set_amplitude_ramp_max(self, ramp_values: list):
        if not self.amplitude_ramp_values:
            print("No amplitude ramp values.")
            return
        self.amplitude_ramp_values.current_to_max = ramp_values
 
    def set_amplitude_ramp_rest(self, ramp_values: list):
        if not self.amplitude_ramp_values:
            print("No amplitude ramp values.")
            return
        self.amplitude_ramp_values.current_to_rest = ramp_values

    def set_amplitude_ramp_min(self, ramp_values: list):
        if not self.amplitude_ramp_values:
            print("No amplitude ramp values.")
            return
        self.amplitude_ramp_values.current_to_min = ramp_values



