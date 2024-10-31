from dataclasses import dataclass
from typing import List

@dataclass
class RampValues:
    current_to_max: List[float]
    current_to_rest: List[float]
    current_to_min: List[float]


@dataclass
class StimEvent:
    channel: int
    frequency: float
    amplitude: float
    period: float
