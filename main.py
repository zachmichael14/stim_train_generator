import sys
from PySide6 import QtWidgets

import manager
import plotter
from widgets import stim_train_widget

# TODO: Adding a new train to a channel causes it to replace the previou train.
# Appending is probably the desired behavior.

# TODO: Interleave pulses. Possibly include a start latency or a way to determine order. This will probably be a DAQ function in control_window.py
# Control_window will also no longer need create_stim_trian since that si 
# handled by the stim manager now. It'll need access to the stim manager

## TODO: Validat base widget values with QtGui.QValidator

## TODO: get rid of value attribute in base widgets? do base widget need value attrs or cna values just be grabbed form the QLineEidt boxes. 


"""




"""

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()

    train_manager = manager.StimTrainManager()
    train_widget = stim_train_widget.StimTrainWidget(train_manager)
    train_plotter = plotter.StimTrainPlotter(train_manager)

    window.setCentralWidget(train_widget)
    window.setWindowTitle("Stim Train Generator")
    window.show()

    sys.exit(app.exec())
