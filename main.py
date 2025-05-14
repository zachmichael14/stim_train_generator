from pathlib import Path
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QStyleFactory

from app.controllers.continuous_stimulation import ContinuousStimController
from app.managers.continuous_manager import ContinuousStimManager

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create("Fusion"))
    
    continuous_stim_manager = ContinuousStimManager()
    main_window = ContinuousStimController(continuous_stim_manager)
    main_window.setWindowTitle("Seáñez Lab Continuous Stimulation Generator")

    icon_path = Path("assets/sl_icon.png").resolve() # Get the absolute path
    app_icon = QIcon()
    app_icon.addFile(str(icon_path))
    main_window.setWindowIcon(app_icon)

    main_window.show()

    sys.exit(app.exec())
    