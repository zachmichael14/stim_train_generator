import time
from typing import Type

from stim_data_manager import StimDataManager
from pico.pico_interface import PicoInterface
from daq import DAQ

class StimExecutor:
    def __init__(self,
                 daq: Type[DAQ],
                 data_manager: Type[StimDataManager],
                #  interface: Type[PicoInterface],
                 ):
        self.daq = daq
        self.data_manager = data_manager
        # self.interface = interface

    def daq_execution(self):
        print("Executing via DAQ")
        for event in self.data_manager.events:
            print(event)

            # Event is break, just wait for duration
            if event.frequency == 0 or event.amplitude == 0:
                self.daq.set_amplitude(0)
                burst_start = time.perf_counter()
                while (time.perf_counter() - burst_start) * 1000 < event.duration:
                    pass

                ### Print break duration values
                # print(f"Actual: {(time.perf_counter() - burst_start) * 1000}", f"Expected: {event.duration}")
            else:  
                self.daq.set_channel(event.channel)
                self.daq.set_amplitude(event.amplitude)

                period = 1 / event.frequency
                duration = event.duration / 1000

                burst_start = time.perf_counter()
                while (time.perf_counter() - burst_start) < duration: 
                    pulse_start = time.perf_counter()
                    self.daq.trigger()

                    # The second condition below cuts off the burst if its
                    # period exceeds the duration of its burst. 

                    # For example, a frequency of 1Hz has a wait time of
                    # 1000ms. If a 1 Hz burst is called for 100 ms, the second
                    # condition will end the burst prematurely (i.e., at
                    # 100ms) to conform to the duration, frequency be damned.

                    while time.perf_counter() - pulse_start < period and time.perf_counter() - burst_start < duration:
                        pass

                 ### Print pulse duration values
                # print(f"Actual: {(time.perf_counter() - burst_start) * 1000}", f"Expected: {event.duration}")
            

    def send_batch_commands(self):
        events = self.data_manager.get_sorted_events()
        for event in events:
            print(f"Sending event: Channel {event.channel}, Amplitude {event.amplitude}, Frequency {event.frequency}, Duration {event.duration} ms")
            
            self.interface.set_channel(event.channel)
            input("Press Enter after observing channel set...")
            
            self.interface.set_amplitude(event.amplitude)
            input("Press Enter after observing amplitude set...")
            
            self.interface.set_frequency(int(event.frequency), int(event.duration))
            
            # Convert milliseconds to seconds for the sleep duration
            sleep_duration = event.duration / 1000.0
            print(f"Waiting for {sleep_duration:.2f} seconds...")
            time.sleep(sleep_duration)
            
            input("Press Enter after observing the burst...")
    
        print("Starting execution")
        self.interface.start_execution()

