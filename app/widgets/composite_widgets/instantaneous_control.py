from enum import Enum
from typing import Optional

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QFormLayout, QGroupBox, QLabel, QPushButton, QToolButton, QVBoxLayout,
    QWidget
)

from app.widgets.basic_components.slide_toggle import SlideToggle
from app.widgets.basic_components.debounced_spin_box import DebouncedDoubleSpinBox

class PauseButtonStates(Enum):
    PAUSE = "Freeze Ramp"
    RESUME = "Resume Ramping"

class InstantaneousControlWidget(QWidget):
    """
    A widget for controlling instantaneous stimulation parameters.
    
    Provides controls for turning stimulation on/off, pausing threads, 
    and managing live updates.
    
    Signals:
    - signal_on_off_changed: Emitted when stimulation is toggled
    - signal_pause_toggled: Emitted when thread pause state changes
    - signal_update_mode_changed: Emitted when update mode changes
    """

    signal_on_off_changed = Signal(bool)
    signal_pause_toggled = Signal(bool)
    signal_update_mode_changed = Signal(bool)
    signal_update_button_clicked = Signal(float)
    signal_reset_button_clicked = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the instantaneous control widget.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
       
        self.onoff_button = SlideToggle()
        self.is_paused = False
        self.pause_button = QPushButton(PauseButtonStates.PAUSE.value)
        self.reset_button = QPushButton("Quit Ramp")
        # Reset button is only available after pausing
        self.reset_button.setEnabled(False)

        self.live_update_toggle = SlideToggle()
        self.send_update_button = QPushButton("Send Update(s)")
        self.ramp_duration_spinbox = DebouncedDoubleSpinBox()

        self._setup_ui()
        self._set_widget_settings()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Set up the user interface layout and components."""
        form_layout = QFormLayout()

        form_layout.addRow("Stimulation:",
                           self.onoff_button)
        form_layout.addRow(self.pause_button)
        form_layout.addRow(self.reset_button)

        # Blank rows for spacing
        form_layout.addRow(QLabel(""))  
        form_layout.addRow(QLabel(""))  

        form_layout.addRow("Live Update:",
                           self.live_update_toggle)
        form_layout.addRow("Update Ramp Duration (s):",
                           self.ramp_duration_spinbox)
        form_layout.addRow(self.send_update_button)
        
        group_box = QGroupBox("Stimulation Control")
        group_box.setLayout(form_layout)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(group_box)
        self.setLayout(main_layout)

    def _set_widget_settings(self) -> None:
        """Configure initial settings for widget components."""
        self.pause_button.setText(PauseButtonStates.PAUSE.value)

        # Match button size policy with send update button (tool buttons are 
        # smaller than push buttons by default)
        self.pause_button.setSizePolicy(self.send_update_button.sizePolicy())
        self.pause_button.setCheckable(True)
        self.pause_button.setEnabled(False)

    def _connect_signals(self) -> None:
        """Connect internal signals and to respective events."""
        self.onoff_button.signal_toggled.connect(self._handle_on_off_toggle)
        self.live_update_toggle.signal_toggled.connect(self._handle_update_mode_changed)
        self.send_update_button.clicked.connect(self._handle_update_button_clicked)
        self.pause_button.clicked.connect(self._handle_pause_button_clicked)
        self.reset_button.clicked.connect(self._handle_reset_button_clicked)

    @Slot()
    def _handle_reset_button_clicked(self):
        self.signal_reset_button_clicked.emit()
        self._handle_pause_button_clicked(False)

    @Slot(bool)
    def _handle_on_off_toggle(self, is_on: bool) -> None:
        """
        Handle stimulation on/off toggle event.

        Args:
            is_on (bool): Current state of stimulation (on/off)
        """
        self.signal_on_off_changed.emit(is_on)
        self.pause_button.setEnabled(is_on)
        self.pause_button.setText(PauseButtonStates.PAUSE.value)
        self.is_paused = False
        self.reset_button.setEnabled(False)
   
    @Slot(bool)
    def _handle_pause_button_clicked(self, is_paused) -> None:
        """
        Handle thread pause button click event.

        Args:
            is_paused (bool): Current pause state
        """
        self.is_paused = not self.is_paused
        self.signal_pause_toggled.emit(self.is_paused)
        self.pause_button.setText(
            PauseButtonStates.RESUME.value if self.is_paused else PauseButtonStates.PAUSE.value
        )
        self._toggle_reset_button_visibility(self.is_paused)

    def _toggle_reset_button_visibility(self, is_paused: bool):
        if is_paused:
            self.reset_button.setEnabled(True)
        else:
            self.reset_button.setEnabled(False)

    @Slot()
    def _handle_update_button_clicked(self) -> None:
        """
        Handle send update button click event.
        
        Emits update mode change signals to toggle the state.
        """
        self.signal_update_button_clicked.emit(self.ramp_duration_spinbox.value())
        
    @Slot(bool)
    def _handle_update_mode_changed(self, are_updates_live: bool) -> None:
        """
        Handle update mode change event.

        Args:
            are_updates_live (bool): Current live update state
        """
        self.signal_update_mode_changed.emit(are_updates_live)
        
        self.send_update_button.setEnabled(not are_updates_live)
        self.send_update_button.setText(
            "Updates Are Live" if are_updates_live else "Send Updates"
        )

    def is_on(self) -> bool:
        return self.onoff_button.is_checked()
    