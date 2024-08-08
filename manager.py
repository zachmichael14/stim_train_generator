from dataclasses import dataclass
from typing import List
import csv
from operator import attrgetter

@dataclass
class StimEvent:
    channel: int
    amplitude: float
    frequency: float
    duration: float
    start_time: float

    @property
    def end_time(self):
        return self.start_time + self.duration


class StimDataManager:
    def __init__(self):
        self.events: List[StimEvent] = []

    def load_from_csv(self, file_path: str):
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            # next(reader)  # Skip header
            current_time = 0
            for row in reader:
                channel = int(row[0])
                amplitude, frequency, duration = map(float, row[1:])
                
                event = StimEvent(
                    channel=channel,
                    amplitude=amplitude,
                    frequency=frequency,
                    duration=duration,
                    start_time=current_time
                )
                self.events.append(event)
                current_time += duration

    def add_event(self, event: StimEvent):
        self.events.append(event)
        self.sort_events()

    def remove_event(self, event: StimEvent):
        self.events.remove(event)
        self.recalculate_timeline()

    def modify_event(self, old_event: StimEvent, new_event: StimEvent):
        index = self.events.index(old_event)
        self.events[index] = new_event
        self.recalculate_timeline()

    def sort_events(self):
        self.events.sort(key=attrgetter('start_time'))

    def recalculate_timeline(self):
        self.sort_events()
        current_time = 0
        for event in self.events:
            event.start_time = current_time
            current_time += event.duration

    def get_sorted_events(self) -> List[StimEvent]:
        return self.events

    def get_events_for_channel(self, channel: int) -> List[StimEvent]:
        return [event for event in self.events if event.channel == channel]

    def get_time_range(self):
        if not self.events:
            return None, None
        start = min(event.start_time for event in self.events)
        end = max(event.end_time for event in self.events)
        return start, end
