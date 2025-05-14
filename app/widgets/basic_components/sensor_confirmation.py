from typing import Dict, List, Optional
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

class SensorVisualizationWidget(QWidget):
    """
    A widget that displays sensor information in a scrollable layout.
    
    This widget visualizes both analog and digital sensors, displaying their
    channel numbers, IDs, and associated muscle groups. It handles dynamic
    updates and error message display.

    Args:
        sensors (Dict[str, List[Dict[str, str]]]): Initial sensor configuration
    """

    def __init__(self, sensors: Dict[str, List[Dict[str, str]]]) -> None:
        super().__init__()
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_widget)
        
        self.sensor_layout = QVBoxLayout(self.scroll_widget)
        self.sensor_layout.setSizeConstraint(QVBoxLayout.SetMinAndMaxSize)
        
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.scroll_area)
        self.setLayout(self.main_layout)

    def update_sensors(self, sensors: Dict[str, List[Dict[str, str]]]) -> None:
        """
        Updates the widget with new sensor information.

        Args:
            sensors: Dictionary containing lists of analog and digital sensors,
                    where each sensor is represented by a dictionary with
                    'channel', 'id', and 'muscle' keys.
        """
        self.clear_previous_content()
        
        if not sensors:
            self.sensor_layout.addWidget(QLabel("No sensor map has been uploaded."))
            return
            
        analog_sensor_quantity = len(sensors.get("analog", []))
        digital_sensor_quantity = len(sensors.get("digital", []))
        
        self.sensor_layout.addWidget(QLabel(
            f"Detected {analog_sensor_quantity} analog sensors and "
            f"{digital_sensor_quantity} digital sensors."
        ))
        
        for sensor_type, sensor_list in sensors.items():
            self.pretty_print_sensor_data(sensor_type, sensor_list)
        self.update_minimum_width()

    def pretty_print_sensor_data(self,
                                 sensor_type: str,
                                 sensor_list: List[Dict[str, str]]) -> None:
        """
        Displays formatted sensor information in the widget.

        Args:
            sensor_type: Type of sensors ('analog' or 'digital')
            sensor_list: List of sensor dictionaries containing sensor details
        """
        capitalized_sensor_type = sensor_type.capitalize()
        if sensor_list:
            self.sensor_layout.addWidget(QLabel(f"\n{capitalized_sensor_type} sensors:"))
            for sensor in sensor_list:
                sensor_label = QLabel(
                    f"Sensor {sensor['channel']}: \n"
                    f"\tID: {sensor['id']} \n"
                    f"\tChannel: {sensor['channel']} \n"
                    f"\tMuscle: {sensor['muscle']}"
                )
                self.sensor_layout.addWidget(sensor_label)
        else:
            self.sensor_layout.addWidget(QLabel(f"\nNo {sensor_type} sensors detected."))

    def update_minimum_width(self) -> None:
        """
        Updates the scroll area's minimum width based on the widest content
        widget.
        
        Ensures all sensor information is readable without horizontal 
        scrolling.
        """
        maximum_width = max(
            self.sensor_layout.itemAt(i).widget().sizeHint().width()
            for i in range(self.sensor_layout.count())
        )
        minimum_width = maximum_width + self.scroll_area.verticalScrollBar().width()
        self.scroll_area.setMinimumWidth(minimum_width)

    @Slot(str)
    def display_error_message(self, error_message: str) -> None:
        """
        Displays an error message in the widget.
        
        Args:
            error_message: Error message emitted by config_manager.py's 
                         validate_sensor_map method
        """
        self.clear_previous_content()
        error_label = QLabel(error_message)
        self.sensor_layout.addWidget(error_label)

    def clear_previous_content(self) -> None:
        """Removes all widgets from the sensor layout."""
        for i in reversed(range(self.sensor_layout.count())):
            self.sensor_layout.itemAt(i).widget().setParent(None)
