import time

from analog_streaming.core.daq import DAQ


class StimWorker:
    """
    Worker for managing and executing stimulation events.

    This class continuously retrieves stimulation events from the manager and 
    executes them in a loop while respecting each event's defined period.
    
    Attributes:
        manager (ContinuousStimManager): Event manager that supplies 
        stimulation events.
        running (bool): Indicates whether the worker is actively running.
        daq (DAQ): Data acquisition device interface for stimulation control.
    """

    def __init__(self, manager) -> None:
        """
        Initialize the StimWorker with a manager.

        Args:
            manager: The event manager providing stimulation events.
        """
        self.manager = manager
        self.running = False
        # self.daq = DAQ()

    def run(self) -> None:
        """
        Start the worker loop to process stimulation events.

        Continuously retrieves the next event from the manager and executes 
        stimulation on the specified channel with the defined amplitude. 
        Ensures the loop waits to maintain each event's defined period.
        """
        self.running = True
        
        while self.running:
            event = self.manager.get_next_event()
            start_time = time.perf_counter()  # Record start time of stimulation

            # Execute stimulation based on event parameters
            self._execute_stim(event.channel, event.amplitude)
                
            # Calculate and apply remaining sleep duration to respect event period
            execution_time = time.perf_counter() - start_time
            sleep_duration = max(0, event.period - execution_time)
            self._sleep(sleep_duration)

    def _execute_stim(self, channel: int, amplitude: float) -> None:
        """
        Execute stimulation on a specified channel with a given amplitude.

        Args:
            channel: Channel number for the stimulation.
            amplitude: Amplitude value for the stimulation.
        """
        # self.daq.set_channel(channel)
        # self.daq.set_amplitude(amplitude)
        # self.daq.trigger()
        pass

    def _sleep(self, duration: float) -> None:
        # Turn duration into a time that can be meaningfully compared
        end_time = time.perf_counter() + duration

        while time.perf_counter() < end_time:
            sleep_remaining = end_time - time.perf_counter()
            if sleep_remaining > 0.001:
                time.sleep(0.0005)
            # Busy wait for the last sub-millisecond 
            else:
                pass

    def stop(self) -> None:
        """
        Stop the worker and reset the DAQ.

        Terminates the main worker loop and sets all channels to zero.
        """
        self.running = False
        # self.daq.zero_all()
