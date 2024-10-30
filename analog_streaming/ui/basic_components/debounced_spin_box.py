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
    
    def __init__(self,
                 max_increase: float = None,
                 max_value: float = 1000.0) -> None:
        """
        Initializes the DebouncedDoubleSpinBox.

        Args:
            max_change: The maximum allowed increase from current value
            max_value: The maximum value that can be entered
        """
        super().__init__()

        # Previous value is stored to enforce step limitations, if any
        self._previous_value: float = None
        
        self._max_increase: float = max_increase

        # Keep track of whether user is typing to avoid premature emission
        self._is_typing: bool = False
        self.setMaximum(max_value) 
        
        self.signal_value_changed.connect(self._handle_value_changed)

    def keyPressEvent(self, event) -> None:
        """
        Handles key press events.

        Emits signal on Enter key or focus change, limiting value if necessary.
        If the user is typing, wait to emit signal until typing is finished.
        Overrides superclass's keyPressEvent method.
        
        Args:
            event: The key press event.
        """
        key = event.key()
        # TODO: Is calling super() for keypress event prohibited for enter/return?
        # If not, why not just call super() at end/beginning

        # User pressed enter, editing is finished
        if key in (Qt.Key_Enter, Qt.Key_Return):
            self._is_typing = False
            self._limit_change()
            self._emit_if_changed()

        # User incremented with up/down keyboard keys
        if key in (Qt.Key_Up, Qt.Key_Down):
            self._is_typing = False
            super().keyPressEvent(event)
            self._limit_change()
            self._emit_if_changed()
    
        # User is currently entering values manually
        else:
            self._is_typing = True
            super().keyPressEvent(event)

    def focusInEvent(self, event) -> None:
        """
        Handle focus in event.

        Retain current value as previous value in case of change.
        Overrides superclass's focusInEvent method.
        """
        self._previous_value = self.value()
        super().focusInEvent(event)


    def focusOutEvent(self, event) -> None:
        """
        Handles focus out events.

        Emits signal if user switches focus after editing. This method handles
        situations where the user changes value but clicks away instead of
        pressing enter.
        Overrides superclass's focusOutEvent method.

        Args:
            event: The focus out event.
        """
        if self._is_typing:
            self._is_typing = False
            self._limit_change()
            self._emit_if_changed()
        super().focusOutEvent(event)
    
    def stepBy(self, steps: int) -> None:
        """
        Handles step events from the spin buttons.

        Limits the change in value according to the specified step.
        Overrides superclass's stepBy method.

        Args:
            steps: The number of steps to change the value.
        """
        # TODO: Is resetting is_typing necessary here?
        self._is_typing = False
        super().stepBy(steps)
        self._limit_change()
    
    def _limit_change(self) -> None:
        """
        Limit the change in value to the maximum allowed increment.

        This method assumed decreases in value are safer/more tolerable than
        increases, so it only limits increases.
        
        """
        if self._max_increase is not None:
            change = self.value() - self._previous_value
            if change > self._max_increase:
                # Set to maximum allowed increment
                new_value = self._previous_value + self._max_increase
                print(f"Limited to +{self._max_increase} increases; setting to {new_value}.")
                self.setValue(new_value)
    
    @Slot()
    def _handle_value_changed(self) -> None:
        """
        Handles the value changed signal.

        Emits signal only if user is not currently typing.
        """
        #TODO: Refactor these event/signal handlers
        if not self._is_typing:
            self._emit_if_changed()
    
    def _emit_if_changed(self) -> None:
        """Emits signal only if the value has actually changed."""
        current_value = self.value()
        if current_value != self._previous_value:
            self._previous_value = current_value
            self.signal_value_changed.emit(current_value)