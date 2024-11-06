import numpy as np
from typing import List, Tuple

from analog_streaming.core.data_classes import RampValues

class RampCalculator:
    """Class to calculate ramp values over a specified duration."""

    def __init__(self, precision: float = 1e-10):
        self.precision = precision

    def generate_all_frequency_ramps(self,
                                     current_frequency: float,
                                     ramp_parameters: dict):
        max_intermediates = self.generate_single_frequency_ramp(
            ramp_parameters["to_max_duration"],
            current_frequency,
            ramp_parameters["ramp_max"])
        rest_intermediates = self.generate_single_frequency_ramp(
            ramp_parameters["to_rest_duration"],
            current_frequency,
            ramp_parameters["ramp_rest"])
        min_intermediates = self.generate_single_frequency_ramp(
            ramp_parameters["to_min_duration"],
            current_frequency,
            ramp_parameters["ramp_min"])

        return RampValues(
            current_to_max = max_intermediates,
            current_to_rest = rest_intermediates,
            current_to_min = min_intermediates)

    def generate_single_frequency_ramp(self,
                                       duration: float,
                                       start_frequency: float,
                                       end_frequency: float) -> List[float]:
        """
        Generates intermediate points for a ramp.

        Parameters:
            duration (float): Duration of the ramp
            start_value (float): Starting value of the ramp
            end_value (float): Ending value of the ramp

        Returns:
            List[float]: A list of ramp values at each timepoint
        """
        # No duration, continue with current frequency
        if duration == 0:
            return [start_frequency]
        
        results = []
        f_ramp_results = self._calculate_timepoints(0,
                                                    duration,
                                                    start_frequency,
                                                    end_frequency)
        
        results.extend(point[1] for point in f_ramp_results)
        return results

    def _calculate_timepoints(self,
                              start_time: float,
                              end_time: float,
                              start_frequency: float,
                              end_frequency: float) -> List[Tuple[float, float]]:
        results = []
        ramp_function = self._get_linear_function(start_time,
                                                  end_time,
                                                  start_frequency,
                                                  end_frequency)
    
        current_frequency = max(start_frequency, end_frequency)
        next_timepoint = start_time
    
        while next_timepoint <= end_time:
            current_frequency = ramp_function(next_timepoint)
            results.append((next_timepoint, current_frequency))
            
            if current_frequency <= 0:
                break
                
            period = 1 / current_frequency
            next_timepoint += period
    
        results_array = np.array(results)
        if len(results) > 0:
            results_array = self._handle_last_timepoint(results_array,
                                                        end_time, 
                                                        start_frequency,
                                                        end_frequency)
        
        return results_array.tolist()

    def _handle_last_timepoint(self,
                               results: np.ndarray,
                               end_time: float,
                               start_frequency: float,
                               end_frequency: float) -> np.ndarray:
        if len(results) == 0:
            return results
            
        time_remaining = end_time - results[-1][0]
        if time_remaining <= self.precision:
            return results
            
        frequency_floor = min(start_frequency, end_frequency)
        frequency_ceiling = max(start_frequency, end_frequency)
        
        frequency_to_add = 1 / time_remaining if time_remaining > 0 else float('inf')
        
        if frequency_to_add > frequency_ceiling:
            if len(results) <= 1:
                return results
            results = results[:-1]
            return self._handle_last_timepoint(results, end_time, start_frequency, end_frequency)
            
        if frequency_to_add < frequency_floor:
            print(frequency_floor)
            print(frequency_to_add)
            print(time_remaining)
            print(f"Ramp Calculator says: 'Frequency to add is less than frequency floor. That's worth investigating...'")
            return results            
        insert_index = np.searchsorted(results[:, 1], frequency_to_add)
        if insert_index >= len(results):
            insert_index = len(results) - 1
            
        new_row_time = results[insert_index][0] + (1 / frequency_to_add)
        new_row = np.array([[new_row_time, frequency_to_add]])
        
        results = np.insert(results, insert_index + 1, new_row, axis=0)
        
        if len(results) > 0:
            results[-1][1] = end_frequency
            
        return results

    def _get_linear_function(self, x1: float, x2: float, y1: float, y2: float):
        slope = (y2 - y1) / (x2 - x1)
        intercept = y1 - slope * x1
        return lambda x: slope * x + intercept
    
    def generate_all_amplitude_ramps(self,
                                     current_amplitude: float,
                                     amplitude_ramp_parameters: dict,
                                     current_frequency: float):
        max_quantity = amplitude_ramp_parameters["to_max_duration"] / (1 / current_frequency)
        rest_quantity = amplitude_ramp_parameters["to_rest_duration"] / (1 / current_frequency)
        min_quantity = amplitude_ramp_parameters["to_min_duration"] / (1 / current_frequency)
          
        max_intermediates = self.generate_single_amplitude_ramp(
            current_amplitude,
            amplitude_ramp_parameters["ramp_max"],
            max_quantity,
            current_frequency)
        rest_intermediates = self.generate_single_amplitude_ramp(
            current_amplitude,
            amplitude_ramp_parameters["ramp_rest"],
            rest_quantity,
            current_frequency)
        min_intermediates = self.generate_single_amplitude_ramp(
            current_amplitude,
            amplitude_ramp_parameters["ramp_min"],
            min_quantity,
            current_frequency)

        return RampValues(
            current_to_max = max_intermediates,
            current_to_rest = rest_intermediates,
            current_to_min = min_intermediates)

    def generate_single_amplitude_ramp(self,
                                       start_amplitude: float,
                                       end_amplitude: float,
                                       duration: float,
                                       current_frequency: float):
        quantity_of_intermediates = int(duration / (1 / current_frequency))
        return np.linspace(start_amplitude,
                           end_amplitude,
                           quantity_of_intermediates).tolist()


    # Two situations:
        # -Frequency is ramping, in which case amplitudes just need to be paired with each frequency pulse, so the number of amplitude intermediates is equal to the number of frequency intermediates

        # - Frequency is not ramping, in which case the number of amplitude intermediates must be equal to the number of frequency pulses that occur in the given amplitude ramp duration (number of amplitudes = duration / (1 / frequency))