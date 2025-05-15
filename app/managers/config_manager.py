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
