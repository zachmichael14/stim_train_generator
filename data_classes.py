from dataclasses import dataclass
from typing import List

@dataclass
class StimTrainEvent:
    amplitude: float
    start_time: float
    end_time: float
    frequency: float


@dataclass
class Channel:
    id: int
    events: List[StimTrainEvent]
