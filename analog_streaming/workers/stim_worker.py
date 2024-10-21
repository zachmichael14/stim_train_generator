import heapq
from enum import Enum
import time

import pandas as pd

from analog_streaming.daq import DAQ

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
        
        self.schedule_events([(self.channel, self.frequency, self.amplitude, 1/self.frequency)])

    def set_mode(self, mode: StimLoopMode):
        self.loop_mode = mode

    def stop(self):
        self.running = False
        self.daq.zero_all()
