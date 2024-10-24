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

        slope = self._calculate_slope(params.start_value, params.end_value, params.duration)
        timepoints, values = self._generate_points(params, slope)
        timepoints, values = self._ensure_final_point(timepoints, values, params)

        return list(zip(timepoints.tolist(), values.tolist()))

    def _validate_inputs(self,
                         duration: float,
                         start_value: float,
                         end_value: float) -> RampParameters:
        """
        Validates the input parameters for the ramp.

        It's possible to ensure duration is non-zero, positive integer
        in this method, but it might make sense for zero to be a flag to
        indicate continuous stim, for example. As such, the check occurs
        elsewhere.

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
                         slope: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generates time and value points based on ramp parameters and slope.

        Parameters:
            params (RampParameters): The ramp parameters
            slope (float): The slope of the ramp

        Returns:
            Tuple[np.ndarray, np.ndarray]: Arrays of time points and
            corresponding values
        """
        timepoints = []
        values = []
        current_time = 0.0

        while current_time < params.duration:
            current_value = params.start_value + slope * current_time
            timepoints.append(current_time)
            values.append(current_value)

            period = 1.0 / current_value
            current_time += period

            if period < self.precision:
                break

        return np.array(timepoints), np.array(values)
    
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
            timepoints = np.append(timepoints, params.duration)
            values = np.append(values, params.end_value)
        return timepoints, values
    
    def _calculate_slope(self,
                         x_delta: float,
                         y1: float,
                         y2: float) -> float:
        """
        Calculates the slope of the ramp based on the start and end values.

        Parameters:
            start_value (float): The starting value of the ramp
            end_value (float): The ending value of the ramp
            duration (float): The duration of the ramp

        Returns:
            float: The calculated slope
        """
        return (y2 - y1) / x_delta
