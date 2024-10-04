from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QSlider


class DoubleSlider(QSlider):
    signal_value_changed = Signal(float)

    def __init__(self,
                 orientation: Qt.Orientation = Qt.Vertical,
                 decimal_places: int = 2, 
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self._step = 1
        self._scalar = 10 ** decimal_places
        self.valueChanged.connect(self._emit_value_changed)

    def _emit_value_changed(self):
        """Emits the scaled value as a float when the slider value changes."""
        self.signal_value_changed.emit(self.value())

    def value(self) -> float:
        """Returns the current slider value as a float."""
        return self._int_to_float_value(super().value())
    
    def _int_to_float_value(self, value: int) -> float:
        """Unscales an integer value from QSlider back to a float."""
        return value / self._scalar

    def _float_to_int_value(self, value: float) -> int:
        """Scales a floating-point value to an integer for QSlider."""
        return int(value * self._scalar)

    def setMinimum(self, value: float):
        """Sets the minimum value of the slider as a float.
        Overrides base class's setMinimum method.
        """
        super().setMinimum(self._float_to_int_value(value))

    def setMaximum(self, value: float):
        """Sets the maximum value of the slider as a float.
        Overrides base class's setMaximum method.
        """
        super().setMaximum(self._float_to_int_value(value))

    def setSingleStep(self, value: float):
        """Sets the single step size of the slider as a float.
        Overrides base class's setSingleStep method.
        """
        self._step = value
        super().setSingleStep(self._float_to_int_value(value))

    def singleStep(self) -> float:
        """Returns the single step size as a float.
        Overrides base class's singleStep method.
        """
        return self._int_to_float_value(super().singleStep())

    def setValue(self, value: float):
        """Sets the current slider value as a float.
        Overrides base class's setValue method.
        """
        super().setValue(self._float_to_int_value(value))

    def mouseMoveEvent(self, event):
        """Overrides the mouse move event to adjust value to the nearest step."""
        super().mouseMoveEvent(event)
        # Calculate the nearest step value to snap the slider to
        raw_value = self._int_to_float_value(super().value())
        step_value = round(raw_value / self._step) * self._step
        self.setValue(step_value)
