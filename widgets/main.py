import sys
from PySide6 import QtWidgets

from widgets import interval_widgets, custom_widgets, stim_train_manager, plotter_widget

# TODO: Adding a new train to a channel causes it to replace the previou train.
# Appending is probably the desired behavior.

# TODO: Interleave pulses. Possibly include a start latency or a way to determine order. This will probably be a DAQ function in control_window.py
# Control_window will also no longer need create_stim_trian since that si 
# handled by the stim manager now. It'll need access to the stim manager
# 

# TODO: The manager (or the StimTrain class itself, depending on repsonsibility) will need access to 

# def stim_at_frequency(self, frequency, amplitude, pulse_pins=1):
#     #DAQ function
#     period = (1.0 / frequency)
#     half_period = period / 2

#     self.setAmplitude(amplitude)
#     self.setPulse(pulse_pins)
#     time.sleep(half_period)
#     self.setAmplitude(0)
#     self.setPulse(0)
#     time.sleep(half_period)


class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # self.manager = stim_train_manager.StimTrainManager()
        self.train = stim_train_manager.StimTrain()
        self.init_ui()
        
    def init_ui(self):
        main_layout = QtWidgets.QGridLayout(self)

        self.amplitude_widget = interval_widgets.AmplitudeIntervalWidget()
        self.pulse_length_widget = interval_widgets.PulseLengthIntervalWidget()
        self.interpulse_interval = interval_widgets.InterPulseIntervalWidget()
        self.frequency_widget = interval_widgets.FrequencyWidget()

        main_layout.addWidget(self.amplitude_widget, 0, 0)
        main_layout.addWidget(self.interpulse_interval, 0, 1)

        main_layout.addWidget(self.pulse_length_widget, 1, 0)
        main_layout.addWidget(self.frequency_widget, 1, 1)

    
        self.channel_add_widget = custom_widgets.ChannelAddWidget()
        self.channel_add_widget.channels_selected.connect(self.handle_add_button)

        main_layout.addWidget(self.channel_add_widget, 3, 0, 1, 2)
        self.setLayout(main_layout)

    def handle_add_button(self, channels):
        print(self.amplitude_widget.get_values())
        for channel in channels:
            self.train.trains[channel] = {
                "amplitudes": self.train.amplitudes,
                "frequencies": self.train.frequencies,
                "pulse_durations": self.train.pulse_durations,
                "inter_pulse_intervals": self.train.inter_pulse_intervals
            }
        

        self.reset_to_default()
        plotter = plotter_widget.StimTrainPlotter(self.train.trains)
        plotter.show()

    def reset_to_default(self):
        self.amplitude_widget.reset()
        self.pulse_length_widget.reset()
        self.interpulse_interval.reset()
        self.train_length_widget.reset()
        self.misc_settings_widget.reset()
        self.channel_add_widget.reset()

    def pretty_print_result(self, result):
        for channel, details in result.items():
            print(f"Channel {channel}:")
            print("  Amplitudes: ", end="")
            print(", ".join(f"{amp:.2f}" for amp in details["amplitudes"]))
        
            print(f"  Frequency: {details["frequencies"]} Hz")
        
            print("  Pulse Durations: ", end="")
            print(", ".join(f"{pd:.2f}" for pd in details["pulse_durations"]))
        
            print("  inter_pulse_intervals: ", end="")
            print(", ".join(f"{bd:.2f}" for bd in details["inter_pulse_intervals"]))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()

    w = MainWidget()
    window.setCentralWidget(w)
    window.setWindowTitle("Stim Train Generator")
    window.show()

    sys.exit(app.exec())