from collections import deque
from datetime import datetime
import json
from os import path, makedirs
import socket

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox

class ConfigManager(QObject):
    """
    Manage configuration data for a session.
    
    Responsible for experimental session data including sensors/devices and subject info.
    """

    # The _instance flag is managed by __new__() to prevent setting duplicate/conflicting configuration by ensuring only a single instance of this class can be instantiated
    _instance = None 

    sensor_map_error_signal = Signal(str)

    @classmethod
    def get_instance(cls) -> "ConfigManager":
        """Retrieve or create the singleton instance of ConfigManager."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __new__(cls) -> "ConfigManager":
        """Ensure only one instance of ConfigManager is created."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize the ConfigManager instance with default values."""
        super().__init__()
        if not self._initialized:
            self._initialized = True
            
            self.subject_id: str | None = None
            self.sensors_are_bilateral: bool = False

            self.queue: deque = deque()
            self.pass_queue: deque = deque()
            self.detect_queue: deque = deque()

            self.sensor_map: str | None = None
            self.host_ip: str | None = None
            self.sensors: dict = {}
            self.device_manager: str | None = None
            self.save_dir: str | None = None

    def read_config_from_file(self, file_path: str) -> dict | None:
        """
        Load configuration data from a JSON file.

        Args:
            file_path (str): The path to the configuration file.

        Returns:
            dict: Configuration data loaded from the file.
        """
        try:
            with open(file_path, 'r') as json_file:
                configuration = json.load(json_file)
                return configuration
            
        except (json.JSONDecodeError, KeyError) as e:
            QMessageBox.critical(self, "Config Manager Error", f"Failed to read configuration: {e}")
            return None

    def write_config_to_file(self) -> None:
        """Write the current configuration data to a JSON file."""
        config_file = self._get_config_path()

        with open(config_file, "w") as file:
            config_data = self.get_configuration()
            config_data["creation_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            json.dump(config_data, file)

    def _get_config_path(self) -> str:
        """
        Construct and return the configuration file path.

        Returns:
            str: Path to the configuration file.
        """
        config_dir_path = f"{self.save_dir}{path.sep}{self.subject_id}"

        if not path.exists(config_dir_path):
            makedirs(config_dir_path, exist_ok=True)

        return f"{config_dir_path}{path.sep}config.json"
    
    def get_configuration(self) -> dict[str, str]:
        """
        Retrieve the current configuration as a dictionary.

        Returns:
            dict: Current configuration values.
        """
        config = {
            "subject_id": self.subject_id,
            "device_manager": self.device_manager,
            "host_ip": self.host_ip,
            "sensor_map": self.sensor_map,
            "save_dir": self.save_dir,
        }
        return config

    def set_configuration(self,
                          configuration: dict,
                          export: bool = False) -> None:
        """
        Set configuration values and optionally export them.

        Args:
            configuration (dict): Configuration data.
            export (bool, optional): Export configuration to a file if True.
        """
        for key, value in configuration.items():
            setattr(self, key, value)
        if export:
            self.write_config_to_file()

    def get_current_machine_ip(self) -> str:
        """
        Retrieve the current machine's IP address.

        Returns:
            str: Current machine's IP address.
        """
        return socket.gethostbyname(socket.gethostname())


    
    # def categorize_sensors(self):
    #     """
    #     Create a dictionary with keys "analog" and "digital" where values are lists of analog and digital sensors, respectively. Analog sensor IDs are assumed to start with "QTM" and all other sensors (e.g., Trigno) are considered digital. 
    #     """
    #     sensors = self.read_sensor_map_file()
    #     categorized_sensors = {"analog": [], "digital": []}

    #     # Determine whether sensor placement is unilateral or bilateral
    #     has_left = False
    #     has_right = False

    #     for sensor in sensors:
    #         # Use first two characters to avoid detecting rectus femoris muscle
    #         if not has_right and sensor["muscle"][:2].casefold() in ("ri",
    #                                                                  "r "):
    #             has_right = True
    #         elif not has_left and sensor["muscle"][:2].casefold() in ("le",
    #                                                                   "l "):
    #             has_left = True

    #         if sensor["id"].startswith("QTM"):
    #             categorized_sensors["analog"].append(sensor)
    #         else:
    #             categorized_sensors["digital"].append(sensor)

    #     self.sensors_are_bilateral = has_left and has_right
    #     return categorized_sensors
    
    # def read_sensor_map_file(self):
    #     """
    #     Read sensor map file and return a list of sensors containing ID, channel, and muscle data.
    #     """
    #     try:            
    #         with open(self.sensor_map_path, "r") as file:
    #             csvReader = csv.DictReader(file, fieldnames=["id",
    #                                                          "channel",
    #                                                          "muscle"])
    #             sensors = [sensor for sensor in csvReader]
    #     except FileNotFoundError:
    #         print("Config Manager: Sensor map not found.")
    #     return sensors
    
    # def validate_sensor_map(self, file_path):
    #     """
    #     Validate the user-uploaded sensor map file by checking:
    #         - File is valid CSV
    #         - File is not contains valid sensor(s) in the specified format
    #         - No other errors occur
    #     If an error occurs, send an error message to the sensor confirmation widget.
    #     """
    #     # File is not valid CSV
    #     if not self.is_valid_csv_file(file_path):
    #         message = "Config Manager Error - Sensor map file must be a valid CSV"
    #         self.sensor_map_error_signal.emit(message)
    #         return False
        
    #     # File is valid CSV, attempt to read sensor data
    #     try:
    #         # No sensors were detected
    #         if not self.sensor_map_has_sensors(file_path):
    #             message = "Config Manager Error - No sensors could be read from the file"
    #             self.sensor_map_error_signal.emit(message)
    #             return False
            
    #         # Sensors were detected
    #         return True
        
    #     # Some other error
    #     except Exception as e:
    #         message = f"Config Manager Error - Trouble reading sensor map file: {str(e)}"
    #         self.sensor_map_error_signal.emit(message)
    #         return False
        
    # def is_valid_csv_file(self, file_path):
    #     """
    #     Return True if file_path ends in .csv, False otherwise.
    #     """
    #     _, file_extension = os.path.splitext(file_path)
    #     return file_extension.lower() == ".csv"
    
    # def sensor_map_has_sensors(self, file_path):
    #     """
    #     Ensure sensors in the sensor map file are in the specified format and contain sensor data with the following information: 
    #         - ID
    #         - Channel
    #         - Muscle
    #     Return False if sensor information not in the proper format or the file is empty.
    #     """
    #     try:            
    #         with open(file_path, "r") as file:
    #             csvReader = csv.DictReader(file, fieldnames=["id", 
    #                                                          "channel",
    #                                                          "muscle"])
    #             sensors = [sensor for sensor in csvReader]
    #             if sensors:
    #                 return True
        
    #     except FileNotFoundError:
    #         message = f"Config Manager Error - File {file_path} not found"
    #         self.sensor_map_error_signal.emit(message)
    #         return False

    # def update_config(self, data_dict):
    #     """
    #     Sets the values of ConfigManger attributes to the user-provided values in data_dict, if those values are valid.
    #     Return True if update was successful.
    #     """
    #     if self.validate_config(data_dict):
    #         for key, value in data_dict.items():
    #             setattr(self, key, value)
    #         return True

    #     print("Config Manager Error - Configuration is invalid.")
    #     return False
    
    # def validate_config(self, data_dict):
    #     """
    #     Call validation methods on data_dict (which contains user-entered values).
    #     Returns True if valid, False otherwise.
    #     """
    #     if self.validate_attributes(data_dict) and self.validate_sensors():
    #         return True
    #     return False
    
    # def validate_attributes(self, data_dict):
    #     """
    #     Return True if user-provided values in data_dict are non-empty strings and ConfigManager class contains the attribute to which the data will be set.
    #     """
    #     for key, value in data_dict.items():
    #         if not hasattr(self, key):
    #             print(f"Attribute '{key}' does not exist in Config Manager.")
    #             return False
            
    #         if value is None or (isinstance(value, str) and value.strip() == ""):
    #             print(f"Key '{key}' has invalid value '{value}'.")
    #             return False
    #     return True
    
    # def validate_sensors(self):
    #     """
    #     Return True if sensors is a dictionary and has been set as a ConfigManager attributes.
    #     """
    #     if self.sensors and isinstance(self.sensors, dict):
    #         return True
        
    #     print(f"Attribute 'sensors' must be a non-empty dict where keys are 'analog' and 'digital' and values are non-empty lists of sensors.")
    #     return False

    
    
    # # def get_data_dict(self):
    # #     """
    # #     Return dictionary containing class attrbiutes and their values.
    # #     Exclude double and single underscore attributes. The main purpose is to get the user-entered values of class attributes to pass as configuration details to various widgets.
    # #     """
    # #     data_dict = {}
    # #     for key, value in self.__dict__.items():
    # #         if not key.startswith("__") and not key.startswith("_"):
    # #             data_dict[key] = value
    # #     return data_dict
    
    # # def set_save_dir(self, selected_dir):
    # #     self.save_dir = Path(selected_dir)
    
    # def total_sensor_count(self):
    #     """
    #     Return the total number of analog and digital sensors from the sensor attribute.
    #     """
    #     analog_count = len(self.sensors.get("analog", []))
    #     digital_count = len(self.sensors.get("digital", []))
    #     return analog_count + digital_count
