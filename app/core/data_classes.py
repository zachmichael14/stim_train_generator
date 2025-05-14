from dataclasses import dataclass
from typing import List

@dataclass
class RampValues:
    max: List[float]
    rest: List[float]
    min: List[float]


@dataclass
class StimEvent:
    channel: int
    frequency: float
    amplitude: float
    period: float
