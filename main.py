import sys

from PySide6.QtWidgets import QApplication, QStyleFactory

from analog_streaming.controllers.continuous_stimulation import ContinuousStimWidget
from analog_streaming.managers.continuous_manager import ContinuousStimManager

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create("Fusion"))

    continuous_stim_manager = ContinuousStimManager()
    main_window = ContinuousStimWidget(continuous_stim_manager)

    main_window.show()

    sys.exit(app.exec())
    