"""
File: sensorConfirmationManager.py
Purpose: SensorConfirmationDialog is a helper class that displays detected sensors to the user, allowing them to confirm the sensor configuration. This class is called by the onFileUpload() method of the SensorManager class provided by sensorManager.py.

While this dialog doesn't allow the user to make any changes to the setup (changes currently must be performed by editing the sensor map .csv file), that may be a desirable feature in the future.
"""
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

class SensorVisualizationWidget(QWidget):
    def __init__(self, sensors):
        super().__init__()
        
        # Widget is scrollable in the event of many detected sensors
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_widget)

        self.sensor_layout = QVBoxLayout(self.scroll_widget)
        self.sensor_layout.setSizeConstraint(QVBoxLayout.SetMinAndMaxSize)


        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.scroll_area)
        self.setLayout(self.main_layout)
        
    def update_sensors(self, sensors):
        self.clear_previous_content()
        
        if not sensors:
            self.sensor_layout.addWidget(QLabel(f"No sensor map has been uploaded."))
            return

        analog_sensor_quantity = len(sensors.get("analog", []))
        digital_sensor_quantity = len(sensors.get("digital", []))
        
        self.sensor_layout.addWidget(QLabel(f"Detected {analog_sensor_quantity} analog sensors and {digital_sensor_quantity} digital sensors."))

        # Pretty-print detected sensors
        for sensor_type, sensor_list in sensors.items():
            self.pretty_print_sensor_data(sensor_type, sensor_list)

        self.update_minimum_width()
        
    def pretty_print_sensor_data(self, sensor_type, sensor_list):
        capitalized_sensor_type = sensor_type.capitalize()

        if sensor_list:  # Ensure >0 sensors of sensor_type
            self.sensor_layout.addWidget(QLabel(f"\n{capitalized_sensor_type} sensors:"))
            for sensor in sensor_list:
                sensor_label = QLabel(f"Sensor {sensor['channel']}: \n\tID: {sensor['id']} \n\tChannel: {sensor['channel']} \n\tMuscle: {sensor['muscle']}")
                self.sensor_layout.addWidget(sensor_label)
        else:
            self.sensor_layout.addWidget(QLabel(f"\nNo {sensor_type} sensors detected."))

    def update_minimum_width(self):
        maximum_width = 0
        for i in range(self.sensor_layout.count()):
            widget = self.sensor_layout.itemAt(i).widget()
            maximum_width = max(maximum_width, widget.sizeHint().width())
        minimum_width = maximum_width + self.scroll_area.verticalScrollBar().width()
        self.scroll_area.setMinimumWidth(minimum_width)

    @Slot(str)
    def display_error_message(self, error_message):
        """
        This message displays an error message to the user.
        The specific error message is emitted by config_maanger.py's validate_sensor_map method.
        """
        self.clear_previous_content()

        # Display the error message
        error_label = QLabel(error_message)
        self.sensor_layout.addWidget(error_label)

    def clear_previous_content(self):
        """Clear previous content from the sensor layout."""
        for i in reversed(range(self.sensor_layout.count())):
            self.sensor_layout.itemAt(i).widget().setParent(None)
