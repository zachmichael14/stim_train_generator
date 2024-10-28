import numpy as np
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class RampParameters:
    """Data class to store ramp parameters."""
    duration: float
    start_value: float
    end_value: float

class RampCalculator:
    """Class to calculate ramp values over a specified duration."""
    
    def __init__(self, precision: float = 1e-10):
        """
        Initializes the RampCalculator with a given precision.

        Parameters:
            precision (float): The minimum change in value considered
            significant.
        """
        self.precision = precision

    def generate_intermediates(self,
                               duration: float,
                               start_value: float,
                               end_value: float) -> List[Tuple[float, float]]:
        """
        Generates intermediate points for a ramp.

        Parameters:
            duration (float): Duration of the ramp
            start_value (float): Starting value of the ramp
            end_value (float): Ending value of the ramp

        Returns:
            List[Tuple[float, float]]: A list of tuples containing ramp values
            and the timepoints at which they occur
        """
        params = self._validate_inputs(duration, start_value, end_value)

        if params.duration == 0:
            return [(0.0, params.start_value)]

        function = self._get_linear_function(params.duration, params.start_value, params.end_value)
        timepoints, values = self._generate_points(params, function)
        # timepoints, values = self._ensure_final_point(timepoints, values, params)

        return list(zip(timepoints.tolist(), values.tolist()))

    def _validate_inputs(self,
                         duration: float,
                         start_value: float,
                         end_value: float) -> RampParameters:
        """
        Validates the input parameters for the ramp.

        Parameters:
            duration (float): Duration of the ramp
            start_value (float): Starting value of the ramp
            end_value (float): Ending value of the ramp

        Returns:
            RampParameters: An instance of RampParameters with validated
            inputs.

        Raises:
            ValueError: If any input is invalid
        """
        try:
            params = RampParameters(
                duration=float(duration),
                start_value=float(start_value),
                end_value=float(end_value)
            )
        except ValueError:
            raise ValueError("All inputs must be convertible to float")
            
        if params.duration < 0:
            raise ValueError("Duration must be non-negative")
        if params.start_value <= 0 or params.end_value <= 0:
            raise ValueError("Values must be positive")
            
        return params

    def _generate_points(self,
                     params: RampParameters,
                     function) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generates time and value points based on ramp parameters and slope, ensuring
        the final point fits within the specified duration and value range.
    
        Parameters:
            params (RampParameters): The ramp parameters
            function (callable): The ramp function for value calculation
    
        Returns:
            Tuple[np.ndarray, np.ndarray]: Arrays of time points and
            corresponding values
        """
        timepoints = []
        values = []
        current_time = 0.0
        remaining_time = params.duration
        # min_value = min(params.start_value, params.end_value)
        # max_value = max(params.start_value, params.end_value)
    
        while remaining_time > self.precision:
            current_value = function(current_time)
    
            # Ensure the current value fits within the min and max
            # current_value = max(min(current_value, max_value), min_value)
    
            period = 1.0 / current_value  # Dynamic period calculation
    
            if current_time + period > params.duration:
                # Calculate the final point that fits within the remaining time and value range
                timepoints = np.delete(timepoints, -1)
                values = np.delete(values, -1)
            
                time_remaining = params.duration - timepoints[-1]

                inserted_value = 1 / time_remaining

                if not params.start_value < inserted_value < params.end_value:
                    # timepoints = np.delete(timepoints, -1)
                    # values = np.delete(values, -1)
                    print("Continuing")
                    continue
                else:
                    values = np.append(values, inserted_value)


                    inserted_time = (inserted_value - params.start_value) / ((params.end_value - params.start_value) / params.duration)

                    timepoints = np.append(timepoints, inserted_time)
                    
                    print(f"This is inserted value {inserted_value} @ {inserted_time}")

                    # Sort the timepoints and values to maintain order
                    
                    # timepoints, values = self._recalculate_timepoints(timepoints, values, params)
                    sorted_indices = np.argsort(timepoints)
                    timepoints = np.array(timepoints)[sorted_indices]
                    values = np.array(values)[sorted_indices]
                    break
            else:
                timepoints.append(current_time)
                values.append(current_value)
                current_time += period
                remaining_time -= period

        for i in range(len(timepoints)):
            print(timepoints[i], values[i])
    
        # # If the last point is not at the end of the duration, add it
        if timepoints[-1] < params.duration:
     
            timepoints = np.append(timepoints, params.duration)
            values = np.append(values, params.end_value)
    
        return np.array(timepoints), np.array(values)
    
    def _recalculate_timepoints(self, timepoints: List[float], values: List[float], params: RampParameters) -> Tuple[np.ndarray, np.ndarray]:
        """
        Recalculates timepoints to ensure they correspond to the values and maintains order.

        Parameters:
            timepoints (List[float]): The current time points
            values (List[float]): The current values

        Returns:
            Tuple[np.ndarray, np.ndarray]: Updated arrays of time points and values
        """
        recalculated_timepoints = []
        recalculated_values = []
        
        total_time = 0.0
        for i in range(len(values)):
            if i == 0:
                recalculated_timepoints.append(0.0)
                recalculated_values.append(values[i])
            else:
                period = 1 / values[i-1]
                timepoint = timepoints[i-1] + period
                # total_time += timepoint
                recalculated_timepoints.append(timepoint)
                recalculated_values.append(values[i])

        return np.array(recalculated_timepoints), np.array(recalculated_values)


    def _ensure_final_point(self,
                        timepoints: np.ndarray,
                        values: np.ndarray,
                        params: RampParameters) -> Tuple[np.ndarray, np.ndarray]:
        """
        Ensures that the final point of the ramp is included.

        Parameters:
            timepoints (np.ndarray): The generated time points
            values (np.ndarray): The generated values corresponding to the
            time points
            params (RampParameters): The ramp parameters

        Returns:
            Tuple[np.ndarray, np.ndarray]: Updated arrays of time points and
            values
        """
        if timepoints[-1] < params.duration:
            # Calculate the last time point and value to include
            last_time = params.duration
            last_value = self._get_linear_function(params.duration, params.start_value, params.end_value)(last_time)

            # Append the last point to the timepoints and values arrays
            timepoints = np.append(timepoints, last_time)
            values = np.append(values, last_value)

        return timepoints, values
    

    def _get_linear_function(self,
                             duration: float,
                             start_value: float,
                             end_value: float):
        """
        Returns a linear function based on ramp parameters.

        Parameters:
            duration (float): Duration of the ramp
            start_value (float): Starting value of the ramp
            end_value (float): Ending value of the ramp

        Returns:
            callable: A function to calculate ramp values at any time.
        """
        slope = (end_value - start_value) / duration
        intercept = end_value - (slope * duration)
        return lambda x: slope * x + intercept


 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 