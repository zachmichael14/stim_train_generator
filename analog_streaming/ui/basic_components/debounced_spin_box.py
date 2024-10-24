from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QDoubleSpinBox

class DebouncedDoubleSpinBox(QDoubleSpinBox):
    """
    A QDoubleSpinBox that implements debounced value changes:
    - Only emits valueChanged when Enter is pressed or focus is lost.
    - Emits immediately for arrow keys and spin buttons.
    - Limits the rate of change per step if specified.
    """
    # The superclass's valueChanged signal is emitted instantly upon key press.
    # Since this class aims to delay the update until editing is finished,
    # this signal is emitted instead.
    signal_value_changed = Signal(float)
    
    def __init__(self, max_increase: float = None) -> None:
        """
        Initializes the DebouncedDoubleSpinBox.

        Args:
            max_change: The maximum allowed increase from current value.
        """
        super().__init__()
        self._max_increase: float = max_increase
        # Previous value is stored to enforce step limitations, if any
        self._previous_value: float = self.value()
        self._is_typing: bool = False
        
        self.signal_value_changed.connect(self._handle_value_changed)

    def keyPressEvent(self, event) -> None:
        """
        Handles key press events.

        Emits valueChanged on Enter key and limits changes on arrow key presses.
        Overrides superclass's keyPressEvent method.
        
        Args:
            event: The key press event.
        """
        key = event.key()
        if key in (Qt.Key_Enter, Qt.Key_Return):
            self._is_typing = False
            self._limit_change(self._previous_value)
            self._emit_if_changed()

        if key in (Qt.Key_Up, Qt.Key_Down):
            self._is_typing = False
            old_value = self.value()
            super().keyPressEvent(event)
            self._limit_change(old_value)
            self._emit_if_changed()
        else:
            # Typing is in progess
            self._is_typing = True
            super().keyPressEvent(event)       
    
    def focusOutEvent(self, event) -> None:
        """
        Handles focus out events.

        Emits valueChanged if typing is detected and limits the value change.
        Overrides superclass's focusOutEvent method.

        Args:
            event: The focus out event.
        """
        if self._is_typing:
            self._is_typing = False
            self._limit_change(self._previous_value)  # Limit value change if needed
            self._emit_if_changed()  # Emit signal if value has changed
        super().focusOutEvent(event)  # Call the base class method
    
    def stepBy(self, steps: int) -> None:
        """
        Handles step events from the spin buttons.

        Limits the change in value according to the specified step.
        Overrides superclass's stepBy method.

        Args:
            steps: The number of steps to change the value.
        """
        self._is_typing = False  # Indicate typing is not in progress
        old_value = self.value()  # Store the old value
        super().stepBy(steps)  # Call the base class method
        self._limit_change(old_value)  # Limit the change if needed
    
    def _limit_change(self, old_value: float) -> None:
        """
        Limits the change in value to the maximum allowed step.

        Args:
            old_value: The value before the change.
        """
        if self._max_increase is not None:            
            change = self.value() - old_value 
            if change > self._max_increase:
                new_value = old_value + self._max_increase
                print(f"Can't increase more than {self._max_increase} limit.")
                print(f"Setting value to {new_value}.")
                self.setValue(new_value)
    
    def _handle_value_changed(self, value: float) -> None:
        """
        Handles the value changed signal.

        Emits valueChanged only if not in typing mode.

        Args:
            value: The new value.
        """
        if not self._is_typing:
            self._emit_if_changed()  # Emit the signal if applicable
    
    def _emit_if_changed(self) -> None:
        """
        Emits valueChanged only if the value has actually changed.
        """
        current_value = self.value()  # Get the current value
        if current_value != self._previous_value:  # Check if the value has changed
            self._previous_value = current_value  # Update the previous value
            # Emit the default signal from QDoubleSpinBox
            self.signal_value_changed.emit(current_value)  # Emit the base class signal
