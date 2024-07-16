import numpy as np
from numpy import linspace
import json
from PySide6 import QtCore

class StimTrain(QtCore.QObject):
    json_updated = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self.trains = {}
        self.amplitudes: np.array = None
        self.frequencies: np.array = None
        self.pulse_durations: np.array = None
        self.inter_pulse_intervals: np.array = None
        self.repetitions_per_amplitude: int = 1  # There will always be at least 1 amplitude

    def generate_repeats(self, value, number_of_repeats):
        """Return a numpy array of a value repeated a number of times."""
        return np.repeat(value, number_of_repeats)
    
    def generate_ramp_values(self, start: float, stop: float, points: int):
        """Return a numpy array of linearly spaced values."""
        return linspace(start, stop, points)
    
    def handle_repetition_changed(self, repetitions: int):
        self.repetitions_per_amplitude = repetitions
        self.update_amplitudes()
        self.update_pulse_durations()
        self.update_inter_pulse_intervals()
        self.update_frequencies()

    def handle_amplitude_change(self, values: dict):
        if values["mode"] == "constant":
            amplitude = float(values["values"]["constant"])
            self.amplitudes = self.generate_repeats(amplitude, self.repetitions_per_amplitude)
        elif values["mode"] == "ramp":
            start = float(values["values"]["start"])
            stop = float(values["values"]["stop"])
            points = int(values["values"]["points"])
            self.amplitudes = self.generate_ramp_values(start, stop, points)
        

    def handle_pulse_duration_change(self, values):
        if values["mode"] == "constant":
            pulse_duration = float(values["values"]["constant"])
            self.pulse_durations = self.generate_repeats(pulse_duration, len(self.amplitudes))
        elif values["mode"] == "ramp":
            start = float(values["values"]["start"])
            stop = float(values["values"]["stop"])
            points = int(values["values"]["points"])
            self.pulse_durations = self.generate_ramp_values(start, stop, points)

    def handle_break_change(self, values):
        if values["mode"] == "constant":
            interval = float(values["values"]["constant"])
            if len(self.amplitudes) == 1:
                self.inter_pulse_intervals = self.generate_repeats(interval, len(self.amplitudes))
            else:
                self.inter_pulse_intervals = self.generate_repeats(interval, len(self.amplitudes) - 1)
        elif values["mode"] == "ramp":
            start = float(values["values"]["start"])
            stop = float(values["values"]["stop"])
            points = int(values["values"]["points"])
            self.inter_pulse_intervals = self.generate_ramp_values(start, stop, points)
    
    def handle_frequency_changed(self, frequency: float):
        self.frequencies = self.generate_repeats(frequency, len(self.amplitudes))

    def update_amplitudes(self):
        if self.amplitudes is not None:
            self.amplitudes = self.generate_repeats(self.amplitudes,
                                                    self.repetitions_per_amplitude)

    def update_pulse_durations(self):
        if self.pulse_durations is not None:
            self.pulse_durations = self.generate_repeats(self.pulse_durations,
                                                         len(self.amplitudes))

    def update_inter_pulse_intervals(self):
        if self.inter_pulse_intervals is not None:
            self.inter_pulse_intervals = self.generate_repeats(self.inter_pulse_intervals,
                                                               len(self.amplitudes) - 1)
            

    def update_frequencies(self):
        if self.frequencies is not None:
            self.frequencies = self.generate_repeats(self.frequencies, len(self.amplitudes))

        
class StimTrainManager(QtCore.QObject):
    json_updated = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
