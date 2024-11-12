class ConfigDefaults:
    """Default configuration values for the application."""

    DEVICE_MANAGERS = ["Trigno Client", "Analog Client"]
    # IP address of the desktop near the Trigno base station
    HOST_IP = "10.229.96.105" 
    SENSOR_MAP = "No sensor map selected"
    SAVE_DIR = "No save directory selected"


class FrequencyDefaults:
    """Default frequency parameters for continuous stimulation."""

    defaults = {
            "global_value": 30.0,
            "global_maximum": 500.0,
            "ramp_max": 60.0,
            "ramp_rest": 30.0,
            "ramp_min": 1.0,
            "max_increase": 50.0,
            "to_max_duration": 120.0,
            "to_rest_duration": 10.0,
            "to_min_duration": 1.0,
    }


class AmplitudeDefaults:
    """Default amplitude parameters for continuous stimulation."""

    defaults = {
            "global_value": 0.0,
            "global_maximum": 1000.0,
            "ramp_max": 15,
            "ramp_rest": 7.5,
            "ramp_min": 0.0,
            "max_increase": 15.0,
            "to_max_duration": 120.0,
            "to_rest_duration": 10.0,
            "to_min_duration": 1.0,
    }
