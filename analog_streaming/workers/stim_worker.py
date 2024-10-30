import time

from ..utils.precise_timer import PreciseTimer
from analog_streaming.daq import DAQ


class StimWorker:
    def __init__(self, manager):
        self.manager = manager
        self.running = False
        self.daq = DAQ()
        self.timer = PreciseTimer()

    def run(self) -> None:
        self.running = True
        
        while self.running:
            event = self.manager.get_next_event()
            
            start_time = time.perf_counter()  # Record start time
            self._execute_stim(event.channel, event.amplitude)
                
            # Calculate how long the stimulation took
            execution_time = time.perf_counter() - start_time
            sleep_duration = max(0, event.period - execution_time)
            self.timer.sleep(sleep_duration)

    def _execute_stim(self, channel, amplitude):
        self.daq.set_channel(channel)
        self.daq.set_amplitude(amplitude)
        self.daq.trigger()

    def stop(self):
        self.running = False
        self.daq.zero_all()
