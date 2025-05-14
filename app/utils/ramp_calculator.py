import numpy as np
from typing import List, Tuple

from app.core.data_classes import RampValues

class RampCalculator:
    """Class to calculate ramp values over a specified duration."""
    def generate_all_frequency_ramps(self,
                                     current_frequency: float,
                                     ramp_parameters: dict) -> RampValues:
        max_intermediates = self.generate_single_frequency_ramp(
            current_frequency,
            ramp_parameters["ramp_max"],
            ramp_parameters["to_max_duration"])
        rest_intermediates = self.generate_single_frequency_ramp(
            current_frequency,
            ramp_parameters["ramp_rest"],
            ramp_parameters["to_rest_duration"])
        min_intermediates = self.generate_single_frequency_ramp(
            current_frequency,
            ramp_parameters["ramp_min"],
            ramp_parameters["to_min_duration"])

        return RampValues(
            max = max_intermediates,
            rest = rest_intermediates,
            min = min_intermediates)

    def generate_single_frequency_ramp(self,
                                       start_frequency: float,
                                       end_frequency: float,
                                       duration: float) -> List[float]:
        """
        Generates intermediate points for a ramp, adjusting the last frequency to fit the duration.
        Parameters:
            duration (float): Duration of the ramp
            start_frequency (float): Starting frequency of the ramp
            end_frequency (float): Ending frequency of the ramp
        Returns:
            List[float]: A list of ramp frequencies at each timepoint
        """
        if duration == 0:
            return [end_frequency]

        results = []
        current_frequency = start_frequency
        current_time = 0
        period = 1 / current_frequency

        while current_time + period <= duration:
            results.append(current_frequency)
            current_time += period
            current_frequency = start_frequency + (end_frequency - start_frequency) * (current_time / duration)
            period = 1 / current_frequency

        if current_time < duration:
            remaining_time = duration - current_time
            last_frequency = 1 / remaining_time  # Calculate frequency that fits the remaining time
            if min(start_frequency, end_frequency) < last_frequency < max(start_frequency, end_frequency):
                results.append(last_frequency)
        results.append(end_frequency)

        return sorted(results, reverse=(end_frequency < start_frequency))
    
    def generate_all_amplitude_ramps(self,
                                     current_amplitude: float,
                                     amplitude_ramp_parameters: dict,
                                     current_frequency: float):          
        max_intermediates = self.generate_single_amplitude_ramp(
            current_amplitude,
            amplitude_ramp_parameters["ramp_max"],
             amplitude_ramp_parameters["to_max_duration"],
            current_frequency)
        rest_intermediates = self.generate_single_amplitude_ramp(
            current_amplitude,
            amplitude_ramp_parameters["ramp_rest"],
             amplitude_ramp_parameters["to_rest_duration"],
            current_frequency)
        min_intermediates = self.generate_single_amplitude_ramp(
            current_amplitude,
            amplitude_ramp_parameters["ramp_min"],
            amplitude_ramp_parameters["to_min_duration"],
            current_frequency)

        return RampValues(
            max = max_intermediates,
            rest = rest_intermediates,
            min = min_intermediates)

    def generate_single_amplitude_ramp(self,
                                       start_amplitude: float,
                                       end_amplitude: float,
                                       duration: float,
                                       current_frequency: float):
        quantity_of_intermediates = int(duration / (1 / current_frequency))

        if quantity_of_intermediates == 1:
            return [end_amplitude]
    
        elif quantity_of_intermediates == 2:
            print([((start_amplitude + end_amplitude) / 2), end_amplitude])
            return [((start_amplitude + end_amplitude) / 2), end_amplitude]


        return np.linspace(start_amplitude,
                           end_amplitude,
                           quantity_of_intermediates).tolist()


    # Two situations:
        # -Frequency is ramping, in which case amplitudes just need to be paired with each frequency pulse, so the number of amplitude intermediates is equal to the number of frequency intermediates

        # - Frequency is not ramping, in which case the number of amplitude intermediates must be equal to the number of frequency pulses that occur in the given amplitude ramp duration (number of amplitudes = duration / (1 / frequency))