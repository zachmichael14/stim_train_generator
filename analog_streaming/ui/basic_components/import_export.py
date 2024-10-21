from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton

class ImportExportWidget(QWidget):
    signal_import_requested = Signal()
    signal_export_requested = Signal()
    
    def __init__(self):
        super().__init__()
        self.import_config_button = QPushButton("Import Configuration")
        self.export_config_button = QPushButton("Export Configuration")

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.import_config_button)
        main_layout.addWidget(self.export_config_button)
        self.setLayout(main_layout)

    def _connect_signals(self):
        self.import_config_button.clicked.connect(self._handle_import_requested)
        self.export_config_button.clicked.connect(self._handle_export_requested)

    def _handle_import_requested(self):
        self.signal_import_requested.emit()

    def _handle_export_requested(self):
        self.signal_export_requested.emit()
