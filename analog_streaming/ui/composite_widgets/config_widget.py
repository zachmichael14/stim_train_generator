from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFormLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
)

from analog_streaming.ui.basic_components.import_export import ImportExportWidget
from analog_streaming.utils.config_defaults import ConfigDefaults


class ConfigWidget(QWidget):
    """Widget that provides UI for setting experimental configuration."""

    signal_import_requested = Signal()
    signal_export_requested = Signal()
    signal_host_ip_checkbox_toggled = Signal(bool)
    signal_select_save_dir_requested = Signal() 
    signal_sensor_map_requested = Signal()

    def __init__(self) -> None:
        """Initialize the ConfigWidget and its components."""
        super().__init__()
        self.import_export_buttons = ImportExportWidget()
        self.subject_id = QLineEdit()
        self.device_manager = QComboBox()

        self.host_ip = QLineEdit()
        self.host_ip_checkbox = QCheckBox("Use Trigno from this machine?")

        self.sensor_map_label = QLabel()
        self.sensor_map_button = QPushButton("Select Sensor Map")

        self.save_dir_label = QLabel()
        self.save_dir_button = QPushButton("Select Save Directory")

        self._init_ui()
        self._set_field_defaults()
        self._connect_signals()

    def _init_ui(self) -> None:
        """Arrange UI components into columns and rows."""
        form_layout = QFormLayout()
        form_layout.addRow(self.import_export_buttons)
        form_layout.addRow("Subject ID:", self.subject_id)
        form_layout.addRow("Device Manager:", self.device_manager)
        form_layout.addRow("Host IP Address:", self.host_ip)
        form_layout.addRow(self.host_ip_checkbox)
        form_layout.addRow(self.sensor_map_label)
        form_layout.addRow(self.sensor_map_button)
        form_layout.addRow(self.save_dir_label)
        form_layout.addRow(self.save_dir_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        self.setLayout(main_layout)

    def _set_field_defaults(self) -> None:
        """Set default values for the input fields."""
        self.device_manager.addItems(ConfigDefaults.DEVICE_MANAGERS)
        self.host_ip.setText(ConfigDefaults.HOST_IP)
        self.save_dir_label.setText(ConfigDefaults.SAVE_DIR)
        self.sensor_map_button.setText(ConfigDefaults.SENSOR_MAP)

    def _connect_signals(self) -> None:
        """Connect event signals to their respective methods."""
        self.import_export_buttons.signal_import_requested.connect(self._import_config_requested)
        self.import_export_buttons.signal_export_requested.connect(self._export_config_requested)
        self.host_ip_checkbox.toggled.connect(self._handle_host_ip_checkbox)
        self.sensor_map_button.clicked.connect(self._select_sensor_map_requested)
        self.save_dir_button.clicked.connect(self._select_save_dir_requested) 

    @Slot()
    def _import_config_requested(self) -> None:
        """Emit signal to request configuration import."""
        self.signal_import_requested.emit()

    @Slot()
    def _export_config_requested(self) -> None:
        """Emit signal to request configuration export."""
        self.signal_export_requested.emit()

    @Slot(bool)
    def _handle_host_ip_checkbox(self, checked: bool) -> None:
        """Emit signal when the host IP checkbox is toggled."""
        self.signal_host_ip_checkbox_toggled.emit(checked)

    @Slot()
    def _select_save_dir_requested(self) -> None:
        """Emit signal to request selection of save directory."""
        self.signal_select_save_dir_requested.emit()

    @Slot()
    def _select_sensor_map_requested(self) -> None:
        """Emit signal to request selection of sensor map."""
        self.signal_sensor_map_requested.emit()

    @property
    def save_dir(self) -> str | None:
        """
        Retrieve the save directory.
        
        Returns None if the save directory is set to the default label.
        """
        save_dir = self.save_dir_label.text()
        if save_dir == ConfigDefaults.SAVE_DIR:
            return None
        return save_dir

    @save_dir.setter
    def save_dir(self, save_dir: str) -> None:
        """Update the text of the save directory label."""
        self.save_dir_label.setText(save_dir)

    def set_host_ip(self, ip: str) -> None:
        """Set the text of the host IP field."""
        self.host_ip.setText(ip)

    def set_host_ip_read_only(self, is_read_only: bool) -> None:
        """Set the host IP field to read-only if specified."""
        self.host_ip.setReadOnly(is_read_only)

    @property
    def sensor_map(self) -> str | None:
        """
        Retrieve the sensor map.
        
        Returns None if the sensor map is set to the default label.
        """
        sensor_map = self.sensor_map_label.text()
        if sensor_map == ConfigDefaults.SENSOR_MAP:
            return None
        return sensor_map

    @sensor_map.setter
    def sensor_map(self, sensor_map: str) -> None:
        """Update the text of the sensor map label."""
        self.sensor_map_label.setText(sensor_map)

    def populate_fields_with_imported_config(self,
                                             configuration: dict) -> None:
        """Populate UI fields with imported configuration data."""
        self.subject_id.setText(configuration["subject_id"])
        self.device_manager.setCurrentText(configuration["device_manager"])
        self.host_ip.setText(configuration["host_ip"])
        self.sensor_map_label.setText(configuration["sensor_map"])
        self.save_dir_label.setText(configuration["save_dir"])

    def get_configuration(self) -> dict[str, str]:
        """Return user-entered configuration values as a dictionary."""
        data = {
            "subject_id": self.subject_id.text(),
            "device_manager": self.device_manager.currentText(),
            "host_ip": self.host_ip.text(),
            "sensor_map": self.sensor_map,
            "save_dir": self.save_dir
        }
        return data
