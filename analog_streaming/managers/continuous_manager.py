import threading
from typing import Optional, List

from PySide6.QtCore import QObject, Signal

from analog_streaming.core.data_classes import RampValues, StimEvent
from analog_streaming.core.defaults import AmplitudeDefaults, FrequencyDefaults
from analog_streaming.core.stim_worker import StimWorker


class ContinuousStimManager(QObject):
    """
    Manages continuous stimulation parameters and event generation.

    Handles parameter updates and event staging through a threaded worker,
    with support for live updates and frequency ramping.
    """
    signal_event_updated = Signal(StimEvent)
    signal_last_ramp_event = Signal(StimEvent)


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
        if len(self.events) == 2:
            stim_event = self.events.pop(0)
            self.signal_last_ramp_event.emit(self.events[0])
            self.signal_event_updated.emit(self.events[0])

        elif len(self.events) == 1:
            stim_event = self.events[0]
        else:
            stim_event = self.events.pop(0)
            self.signal_event_updated.emit(stim_event)
        print(stim_event)
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
        if self.staged_events:
            self.events = self.staged_events.copy()

    def _run(self) -> None:
        """
        Main thread loop that processes parameter updates and runs the worker.
        
        Monitors for parameter changes in live update mode.
        """
        while self._running:
            if self._parameters_changed:
                self.apply_changes()
                self._parameters_changed = False
            self.worker.run()

    def ramp_frequency_from_direction(self, ramp_direction: str) -> None:
        """
        Creates a series of events to smoothly transition frequency.
        
        Args:
            ramp_destination: Target of ramp ("max", "rest", or "min")
        """
        if not self.frequency_ramp_values:
            return
        
        if ramp_direction in ["max", "rest", "min"]:
            ramp_values = getattr(self.frequency_ramp_values, ramp_direction)
            self.ramp_frequency_from_values(ramp_values)
        
    def ramp_frequency_from_values(self, ramp_values: List[float]):
        self.events.clear()
        events = self.make_frequency_events_from_values(ramp_values)
        self.events = events.copy()

    def ramp_amplitude_from_direction(self, ramp_direction: str) -> None:
        """
        Creates a series of events to smoothly transition amplitude.
        
        Args:
            ramp_destination: Target of ramp ("max", "rest", or "min")
        """
        if not self.amplitude_ramp_values:
            return        
        
        if ramp_direction in ["max", "rest", "min"]:
            ramp_values = getattr(self.amplitude_ramp_values, ramp_direction)
            self.ramp_amplitude_from_values(ramp_values)

    def ramp_amplitude_from_values(self, ramp_values: List[float]):
        self.events.clear()
        events = self.make_amplitude_events_from_values(ramp_values)
        self.events = events
    
    def make_amplitude_events_from_values(self, values: List[float]):
        events = [
            StimEvent(
                channel=self.current_channel,
                frequency=self.current_frequency,
                amplitude=amplitude,
                period = 1 / self.current_frequency
            ) for amplitude in values
        ]
        return events
    
    def make_frequency_events_from_values(self, values: List[float]):
        events = [
            StimEvent(
                channel=self.current_channel,
                frequency=frequency,
                amplitude=self.current_amplitude,
                period = 1 / frequency
            ) for frequency in values
        ]
        return events       