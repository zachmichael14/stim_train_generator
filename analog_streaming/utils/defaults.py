class ConfigDefaults:
    """Default configuration values for the application."""

    DEVICE_MANAGERS = ["Trigno Client", "Analog Client"]
    # IP address of the desktop near the Trigno base station
    HOST_IP = "10.229.96.105" 
    SENSOR_MAP = "No sensor map selected"
    SAVE_DIR = "No save directory selected"


class StimDefaults:
    """Default values for stimulation"""
    GLOBAL_MIN_TO_MAX_RAMP_TIME = 120.0
    GLOBAL_REST_TO_RAMP_TIME = 10.0
    
    class FrequencyDefaults:
        GLOBAL_FREQUENCY = 30.0
        GLOBAL_MAXIMUM = 500
        RAMP_MAX = 60.0
        RAMP_REST = 30.0
        RAMP_MIN = 1.0
        MAX_INCREMENT_SIZE = 50.0
        

    class AmplitudeDefaults:
        GLOBAL_AMPLITUDE = 0.0
        GLOBAL_MAXIMUM = 1000
        RAMP_MAX = 1.0
        RAMP_REST = 0.5
        RAMP_MIN = 0.0
        MAX_INCREMENT_SIZE = 15.0
                                    