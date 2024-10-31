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
            print(f"Ramp Calculator says: 'Frequency to add is less than frequency floor. That's worth investigating...'")
            return results
            
        insert_index = np.searchsorted(results[:, 1], frequency_to_add)
        if insert_index >= len(results):
            insert_index = len(results) - 1
            
        new_row_time = results[insert_index][0] + (1 / frequency_to_add)
        new_row = np.array([[new_row_time, frequency_to_add]])
        
        results = np.insert(results, insert_index + 1, new_row, axis=0)
        results = self._recalculate_time(results)
        
        if len(results) > 0:
            results[-1][1] = end_frequency
            
        return results

    def _recalculate_time(self, arr: np.ndarray) -> np.ndarray:
        if len(arr) <= 1:
            return arr
            
        for i in range(1, len(arr)):
            arr[i][0] = arr[i - 1][0] + (1 / arr[i - 1][1])
        return arr

    def _get_linear_function(self, x1: float, x2: float, y1: float, y2: float):
        if abs(x2 - x1) < self.precision:
            return lambda x: y2
        slope = (y2 - y1) / (x2 - x1)
        intercept = y1 - slope * x1
        return lambda x: slope * x + intercept