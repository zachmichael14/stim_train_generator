from PySide6.QtWidgets import QDoubleSpinBox
from PySide6.QtCore import Signal, Qt

class DebouncedDoubleSpinBox(QDoubleSpinBox):
    """
    A QDoubleSpinBox that:
    - Only emits valueChanged when Enter is pressed or focus is lost
    - Emits immediately for arrow keys and spin buttons
    - Prevents duplicate emissions
    - Limits the rate of change per step
    """
    
    # Custom signal to replace the default valueChanged
    valueChangedFinished = Signal(float)
    
    def __init__(self, parent=None, max_change_per_step=None):
        super().__init__(parent)
        
        self._last_emitted_value = self.value()
        self._typing_value = self.value()
        self._is_typing = False
        self._max_change_per_step = max_change_per_step
        
        # Connect the original valueChanged to our handler
        self.valueChanged.connect(self._handle_value_changed)
    
    def set_max_change_per_step(self, max_change):
        """Set the maximum allowed change per step"""
        self._max_change_per_step = max_change
    
    def keyPressEvent(self, event):
        key = event.key()
        
        if key in (Qt.Key_Enter, Qt.Key_Return):  # Enter/Return
            self._is_typing = False
            self._emit_if_changed()
        elif key in (Qt.Key_Up, Qt.Key_Down):  # Up/Down arrows
            self._is_typing = False
            # Store current value before change
            old_value = self.value()
            super().keyPressEvent(event)
            # Limit the change if needed
            self._limit_change(old_value)
        else:
            self._is_typing = True
            super().keyPressEvent(event)
    
    def focusOutEvent(self, event):
        if self._is_typing:
            self._is_typing = False
            old_value = self._last_emitted_value
            # Limit the change if needed
            self._limit_change(old_value)
            self._emit_if_changed()
        super().focusOutEvent(event)
    
    def stepBy(self, steps):
        # Handle spin button clicks
        self._is_typing = False
        old_value = self.value()
        super().stepBy(steps)
        # Limit the change if needed
        self._limit_change(old_value)
    
    def _limit_change(self, old_value):
        """Limit the change in value to the maximum allowed step"""
        print("limit change")
        if self._max_change_per_step is not None:
            current_value = self.value()
            change = abs(current_value - old_value)
            print(change)
            
            if change > self._max_change_per_step:
                # Determine direction of change
                direction = 1 if current_value > old_value else -1
                # Limit the change
                new_value = old_value + (direction * self._max_change_per_step)
                # Set the new value without triggering stepBy
                self.setValue(new_value)
    
    def _handle_value_changed(self, value):
        if not self._is_typing:
            self._emit_if_changed()
    
    def _emit_if_changed(self):
        """Emit valueChangedFinished only if the value has actually changed"""
        current_value = self.value()
        if current_value != self._last_emitted_value:
            self._last_emitted_value = current_value
            self.valueChangedFinished.emit(current_value)