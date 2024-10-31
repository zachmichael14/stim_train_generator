from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget

class ImportExportWidget(QWidget):
    """
    Widget with buttons for importing and exporting configurations. Emits
    signals when either the import or export action is requested.
    
    Attributes:
        signal_import_requested (Signal): Emitted when the import button is clicked.
        signal_export_requested (Signal): Emitted when the export button is clicked.
    """

    signal_import_requested = Signal()
    signal_export_requested = Signal()
    
    def __init__(self):
        """Initialize the ImportExportWidget and its components."""
        super().__init__()
        self.import_config_button = QPushButton("Import Configuration")
        self.export_config_button = QPushButton("Export Configuration")

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Set up the layout and add import and export buttons."""
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.import_config_button)
        main_layout.addWidget(self.export_config_button)
        self.setLayout(main_layout)

    def _connect_signals(self):
        """Connect button click events to signal emissions."""
        self.import_config_button.clicked.connect(self.signal_import_requested.emit)
        self.export_config_button.clicked.connect(self.signal_export_requested.emit)
