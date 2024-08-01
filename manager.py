import heapq
import math
import numpy as np
import json
from typing import Dict, List
from PySide6 import QtCore

from data_classes import StimTrainEvent, Channel
from daq import DAQ

class StimTrainManager:
    def __init__(self):
        self.channels: List[Channel] = []
        # self.timeline = self.create_timeline()
        # self.daq = DAQ()

    def add_channel(self, channel: Channel):
        self.channels.append(channel)

    def execute(self):
        for channel in channels:
            for event in channel.events:
                
                print(event)
            # print(F"channel {channel}")
    
    # def create_timeline(self):
    #     timeline = []
    #     for channel in self.channels:
    #         for event in channel.events:
    #             heapq.heappush(timeline, (event.start_time, 'start', channel.id, event))
    #             heapq.heappush(timeline, (event.end_time, 'end', channel.id, event))
    #     return timeline

    # def execute(self):
    #     active_events = {}
    #     current_time = 0.0
    #     max_time = max(event[0] for event in self.timeline)

    #     while self.timeline and current_time <= max_time:
    #         time_point, event_type, channel_id, event = heapq.heappop(self.timeline)

    #         if time_point > current_time:
    #             self.execute_active_events(active_events, current_time, time_point)
    #             current_time = time_point

    #         if event_type == 'start':
    #             active_events[channel_id] = event
    #         elif event_type == 'end':
    #             active_events.pop(channel_id, None)

    #     if active_events:
    #         self.execute_active_events(active_events, current_time, max_time + 1)

    # def execute_active_events(self, active_events, start_time, end_time):
    #     current_time = float(start_time)
    #     while current_time < float(end_time):
    #         for channel_id, event in sorted(active_events.items()):
    #             if current_time >= float(end_time):
    #                 break
    #             self.stimulate_channel(channel_id, event, current_time)
    #         current_time += 1.0  # Move time forward by 1ms
    #         # This would really only work if the above operations only took 1ms. 

    #         if current_time - start_time > 1000000:  # Safety check: break if loop runs for too long
    #             print("Safety break triggered")
    #             break

    # def stimulate_channel(self, channel_id, event, current_time):
    #     if event.start_time <= current_time < event.end_time:
    #         time_since_start = current_time - event.start_time
    #         pulse_interval = 1000 / event.frequency  # Convert frequency to ms
    #         if math.isclose(time_since_start % pulse_interval, 0, abs_tol=0.5):  # Allow 0.5ms tolerance
    #             # print(f"Time: {current_time:.2f}ms - Stimulating channel {channel_id} with amplitude {event.amplitude:.2f}")
    #             self.daq.send_pulse_on_channel(self.daq.switcher_channels, event.amplitude, channel=channel_id)
    #         else:
    #             pass
    #             # print(f"Time: {current_time:.2f}ms - Channel {channel_id} active but not pulsing")
    #     else:
    #         pass
    #         # print(f"Time: {current_time:.2f}ms - Channel {channel_id} inactive")
    

if __name__ == "__main__":
    manager = StimTrainManager()
    channels = [
    Channel(1, [
        StimTrainEvent(start_time=0, end_time=100, amplitude=4.0, frequency=60.0),   # 100ms burst of 60Hz pulses
        StimTrainEvent(start_time=150, end_time=250, amplitude=4.0, frequency=30.0), # 100ms burst of 30Hz pulses
        StimTrainEvent(start_time=300, end_time=400, amplitude=4.0, frequency=20.0), # 100ms burst of 20Hz pulses
    ]),
    Channel(8, [
        StimTrainEvent(start_time=50, end_time=150, amplitude=3.0, frequency=70.0),  # 100ms burst of 70Hz pulses
        StimTrainEvent(start_time=200, end_time=300, amplitude=3.0, frequency=25.0), # 100ms burst of 25Hz pulses
    ]),
    Channel(4, [
        StimTrainEvent(start_time=75, end_time=175, amplitude=5.0, frequency=35.0),  # 100ms burst of 35Hz pulses
        StimTrainEvent(start_time=225, end_time=325, amplitude=5.0, frequency=45.0), # 100ms burst of 45Hz pulses
    ]),
    Channel(3, [
        StimTrainEvent(start_time=100, end_time=200, amplitude=2.5, frequency=55.0), # 100ms burst of 55Hz pulses
        StimTrainEvent(start_time=250, end_time=350, amplitude=2.5, frequency=65.0), # 100ms burst of 65Hz pulses
    ]),
    Channel(5, [
        StimTrainEvent(start_time=25, end_time=125, amplitude=6.0, frequency=40.0),  # 100ms burst of 40Hz pulses
        StimTrainEvent(start_time=175, end_time=275, amplitude=6.0, frequency=50.0), # 100ms burst of 50Hz pulses
        StimTrainEvent(start_time=325, end_time=425, 
        amplitude=6.0, frequency=20.0), # 100ms burst of 20Hz pulses
    ]),
]
    
    for channel in channels:
        manager.add_channel(channel)

    manager.execute()



#     from dataclasses import dataclass
# from typing import List
# import heapq
# import math

# from daq import DAQ

# from data_classes import Channel, StimTrainEvent

# class StimulationExecutor:
#     def __init__(self, channels: List[Channel]):
#         self.channels = channels
#         self.timeline = self.create_timeline()
#         # self.daq = DAQ()

#     def create_timeline(self):
#         timeline = []
#         for channel in self.channels:
#             for event in channel.events:
#                 heapq.heappush(timeline, (event.start_time, 'start', channel.id, event))
#                 heapq.heappush(timeline, (event.end_time, 'end', channel.id, event))
#         return timeline

#     def execute(self):
#         active_events = {}
#         current_time = 0.0
#         max_time = max(event[0] for event in self.timeline)

#         while self.timeline and current_time <= max_time:
#             time_point, event_type, channel_id, event = heapq.heappop(self.timeline)

#             if time_point > current_time:
#                 self.execute_active_events(active_events, current_time, time_point)
#                 current_time = time_point

#             if event_type == 'start':
#                 active_events[channel_id] = event
#             elif event_type == 'end':
#                 active_events.pop(channel_id, None)

#         if active_events:
#             self.execute_active_events(active_events, current_time, max_time + 1)

#     def execute_active_events(self, active_events, start_time, end_time):
#         current_time = float(start_time)
#         while current_time < float(end_time):
#             for channel_id, event in sorted(active_events.items()):
#                 if current_time >= float(end_time):
#                     break
#                 self.stimulate_channel(channel_id, event, current_time)
#             current_time += 1.0  # Move time forward by 1ms
#             if current_time - start_time > 1000000:  # Safety check: break if loop runs for too long
#                 print("Safety break triggered")
#                 break

#     def stimulate_channel(self, channel_id, event, current_time):
#         if event.start_time <= current_time < event.end_time:
#             time_since_start = current_time - event.start_time
#             pulse_interval = 1000 / event.frequency  # Convert frequency to ms
#             if math.isclose(time_since_start % pulse_interval, 0, abs_tol=0.5):  # Allow 0.5ms tolerance
#                 # print(f"Time: {current_time:.2f}ms - Stimulating channel {channel_id} with amplitude {event.amplitude:.2f}")
#                 self.daq.send_pulse_on_channel(self.daq.switcher_channels, event.amplitude, channel=channel_id)
#             else:
#                 pass
#                 # print(f"Time: {current_time:.2f}ms - Channel {channel_id} active but not pulsing")
#         else:
#             pass
#             # print(f"Time: {current_time:.2f}ms - Channel {channel_id} inactive")

# # Example usage
# channels = [
#     Channel(1, [
#         StimTrainEvent(start_time=0, end_time=100, amplitude=4.0, frequency=60.0),   # 100ms burst of 60Hz pulses
#         StimTrainEvent(start_time=150, end_time=250, amplitude=4.0, frequency=30.0), # 100ms burst of 30Hz pulses
#         StimTrainEvent(start_time=300, end_time=400, amplitude=4.0, frequency=20.0), # 100ms burst of 20Hz pulses
#     ]),
#     Channel(8, [
#         StimTrainEvent(start_time=50, end_time=150, amplitude=3.0, frequency=70.0),  # 100ms burst of 70Hz pulses
#         StimTrainEvent(start_time=200, end_time=300, amplitude=3.0, frequency=25.0), # 100ms burst of 25Hz pulses
#     ]),
#     Channel(4, [
#         StimTrainEvent(start_time=75, end_time=175, amplitude=5.0, frequency=35.0),  # 100ms burst of 35Hz pulses
#         StimTrainEvent(start_time=225, end_time=325, amplitude=5.0, frequency=45.0), # 100ms burst of 45Hz pulses
#     ]),
#     Channel(3, [
#         StimTrainEvent(start_time=100, end_time=200, amplitude=2.5, frequency=55.0), # 100ms burst of 55Hz pulses
#         StimTrainEvent(start_time=250, end_time=350, amplitude=2.5, frequency=65.0), # 100ms burst of 65Hz pulses
#     ]),
#     Channel(5, [
#         StimTrainEvent(start_time=25, end_time=125, amplitude=6.0, frequency=40.0),  # 100ms burst of 40Hz pulses
#         StimTrainEvent(start_time=175, end_time=275, amplitude=6.0, frequency=50.0), # 100ms burst of 50Hz pulses
#         StimTrainEvent(start_time=325, end_time=425, amplitude=6.0, frequency=20.0), # 100ms burst of 20Hz pulses
#     ]),
# ]


# if __name__ == "__main__":
#     executor = StimulationExecutor(channels)
#     executor.execute()