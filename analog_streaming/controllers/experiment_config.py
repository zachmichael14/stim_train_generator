from os import path
import sys

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QHBoxLayout, QMainWindow, QWidget, QApplication, QFileDialog, QMessageBox
)

from analog_streaming.core.defaults import ConfigDefaults
from analog_streaming.managers.config_manager import ConfigManager
from analog_streaming.ui.basic_components.sensor_confirmation import SensorVisualizationWidget
from analog_streaming.ui.composite_widgets.config_widget import ConfigWidget

class ExperimentConfigWindow(QMainWindow):
    """Manages interactions between config widget and config manager."""

    def __init__(self, config_manager) -> None:
        """Initialize ConfigWindow and its components."""
        super().__init__()
        self.config_manager = config_manager
        self.config_widget = ConfigWidget()
        self.sensor_widget = SensorVisualizationWidget({})

        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
        """Arrange component widgets side-by-side."""
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.config_widget)
        main_layout.addWidget(self.sensor_widget)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def _connect_signals(self) -> None:
        """Connect widget event signals to corresponding slot methods."""
        self.config_widget.signal_import_requested.connect(self._handle_config_import)
        self.config_widget.signal_export_requested.connect(self._handle_config_export)
        self.config_widget.signal_host_ip_checkbox_toggled.connect(self._handle_host_ip_toggle)
        self.config_widget.signal_sensor_map_requested.connect(self._handle_sensor_map_selection)
        self.config_widget.signal_select_save_dir_requested.connect(self._handle_save_dir_selection)

    @Slot()
    def _handle_config_import(self) -> None:
        """
        Import configuration from a file and populate widget fields.
        
        A file dialog is opened to select a JSON configuration file.
        If the file is valid, the configuration is applied, and the widget
        fields are populated with the imported values.

        Displays a warning and returns None if the file is invalid.
        """
        file_path, _ = QFileDialog.getOpenFileName(self.config_widget,
                                                   "Select Configuration File",
                                                   "",
                                                   "JSON Files (*.json)")
        if not file_path:
            QMessageBox.warning(self,
                                "Invalid Config Import",
                                "It appears the config file is invalid.")
            return None

        config_data = self.config_manager.read_config_from_file(file_path)
        self.config_manager.set_configuration(config_data)
        self.config_widget.populate_fields_with_imported_config(config_data)

        if config_data["host_ip"] == self.config_manager.get_current_machine_ip():
            self.config_widget.host_ip_checkbox.setChecked(True)
            self.config_widget.set_host_ip_read_only(True)
        else:
            self.config_widget.host_ip_checkbox.setChecked(False)
            self.config_widget.set_host_ip_read_only(False)

        # TODO: Handle bilateral sensors and sensor dict

    @Slot()
    def _handle_config_export(self) -> None:
        """Export to a file the configuration data entered by the user."""
        configuration = self.config_widget.get_configuration()

        if any(value is None for value in configuration.values()):
            QMessageBox.warning(self,
                                "Invalid Configuration",
                                "It appears some values haven't been set.")
            return None
        self.config_manager.set_configuration(configuration, export=True)

    @Slot()
    def _handle_host_ip_toggle(self, checked: bool) -> None:
        """
        Update IP-related fields based on the checkbox state.
        
        When checked, the host IP is set to the current machine's IP and
        editing is disabled. 
        When unchecked, the host IP is reset to the default and editing is
        enabled.
        """
        if checked:
            current_ip = self.config_manager.get_current_machine_ip()
            self.config_widget.set_host_ip(current_ip)
            self.config_widget.set_host_ip_read_only(True)
        else:
            self.config_widget.set_host_ip(ConfigDefaults.HOST_IP)
            self.config_widget.set_host_ip_read_only(False)

    @Slot()
    def _handle_save_dir_selection(self) -> None:
        """Open a dialog for selecting the save directory."""
        save_dir = QFileDialog.getExistingDirectory(None,
                                                    "Select Save Directory", "")
        if not save_dir:
            QMessageBox.warning(self,
                                "Invalid Save Directory",
                                "It appears no save directory has been selected.")
            return None

        normalized_save_dir = save_dir.replace("/", path.sep)
        self.config_widget.save_dir = normalized_save_dir

    @Slot()
    def _handle_sensor_map_selection(self) -> None:
        """Open a dialog for selecting a sensor map file in CSV format."""
        sensor_map, _ = QFileDialog.getOpenFileName(self.config_widget,
                                                    "Select Sensor Map",
                                                    "",
                                                    "CSV Files (*.csv)")
        if not sensor_map:
            QMessageBox.warning(self,
                                "Invalid Sensor Map",
                                "It appears no sensor map has been selected.")
            return None
        self.config_widget.sensor_map = sensor_map

if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = ConfigManager()
    window = ConfigWindow(manager)
    window.setWindowTitle("Analog Streaming Configuration")
    window.show()

    sys.exit(app.exec())
