from PySide6 import QtWidgets

from .type_selector import StimTypeSelector

class StimTrainWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        stim_type_selector = StimTypeSelector()
        
        main_layout.addWidget(stim_type_selector)


        # self.current_subwidget = PulseWidget()

    # def 
