import csv

import numpy as np
from PySide6 import QtWidgets
from PySide6.QtCore import Signal

from widgets import channel_widget, parameter_widgets

class StimTrainWidget(QtWidgets.QWidget):
    # Emit name of stim train csv file after it's been generated
    signal_values_ready = Signal(str)
    
    def __init__(self):
        super().__init__()

        self.amplitude_widget = parameter_widgets.AmplitudeParameterWidget("Amplitude Settings")
        self.frequency_widget = parameter_widgets.StimulationParameterWidget("Frequency Settings")
        self.pulse_duration_widget = parameter_widgets.StimulationParameterWidget("Pulse Duration Settings")
        self.interpulse_interval_widget = parameter_widgets.StimulationParameterWidget("Inter-pulse Interval Settings")
        self.channel_add_widget = channel_widget.ChannelAddWidget()

        self.init_main_layout()
        
    def init_main_layout(self):
        main_layout = QtWidgets.QGridLayout(self)
        self.setLayout(main_layout)

        # First row
        main_layout.addWidget(self.amplitude_widget, 0, 0)
        main_layout.addWidget(self.frequency_widget, 0, 1)

        # Second row
        main_layout.addWidget(self.pulse_duration_widget, 1, 0)
        main_layout.addWidget(self.interpulse_interval_widget, 1, 1)

        # Third row; spans both columns
        main_layout.addWidget(self.channel_add_widget, 3, 0, 1, 2)

        self.add_button = QtWidgets.QPushButton("Add to Channel(s)")
        self.add_button.pressed.connect(self.handle_add_to_channels)
        main_layout.addWidget(self.add_button, 4, 0, 1, 2)

    def handle_add_to_channels(self):
        amplitudes = self.amplitude_widget.input_values
        train_length = len(amplitudes)

        channels = self.channel_add_widget.get_active_channels()

        pulse_durations = self.pad_input_array(self.pulse_duration_widget,
                                               train_length) 
               
        frequencies = self.pad_input_array(self.frequency_widget,
                                           train_length)
        
        intervals = self.pad_input_array(self.interpulse_interval_widget,
                                         train_length)

        filename = "test.csv"
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Channel ID", "Amplitude", "Frequency", "Start Time", "End Time"])

            current_time = 0
            for i, channel_id in enumerate(channels):
                for j in range(train_length):
                    amplitude = amplitudes[j]
                    frequency = frequencies[j]
                    duration = pulse_durations[j]

                    start_time = current_time
                    end_time = start_time + duration

                    writer.writerow([channel_id,
                                     amplitude,
                                     frequency,
                                     start_time,
                                     end_time,
                                     ])
            
                    # Update current_time for the interval event
                    current_time = end_time
                
                    # Calculate start and end times for the interval event
                    interval_start_time = current_time
                    interval_end_time = interval_start_time + intervals[j]


                    writer.writerow([channel_id,
                                     0, # Intervals don't have amplitudes
                                     0, # Intervals don't have frequency
                                     interval_start_time,
                                     interval_end_time,
                                     ])
                                
                    # Update current_time for the next event
                    current_time = interval_end_time

        self.signal_values_ready.emit(filename)
        self.reset_to_default()

    def pad_input_array(self, widget, desired_length):
        values = widget.input_values

        if widget.get_current_mode() == "constant":
            values = np.repeat(values, desired_length)   

        if len(values) != desired_length:
            print("Error: Too many or too few pulse values")
            print(f"Actual length of values list: {values.size}")
            print(f"Expected length of values list: {desired_length}")
            raise Exception
        
        return values

    def reset_to_default(self):
        self.amplitude_widget.reset()
        self.pulse_duration_widget.reset()
        self.interpulse_interval_widget.reset()
        self.channel_add_widget.reset()
        self.frequency_widget.reset()
