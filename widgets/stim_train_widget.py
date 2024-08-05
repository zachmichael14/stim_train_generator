import numpy as np

from PySide6 import QtWidgets

import manager
import plotter
from data_classes import Channel, StimTrainEvent
from widgets import channel_widget, parameter_widgets

class StimTrainWidget(QtWidgets.QWidget):
    def __init__(self, manager: manager.StimTrainManager):
        super().__init__()
        self.events = []
        self.manager = manager

        self.amplitude_widget = parameter_widgets.AmplitudeParameterWidget("Amplitude Settings")
        self.frequency_widget = parameter_widgets.StimulationParameterWidget("Frequency Settings")
        self.pulse_duration_widget = parameter_widgets.StimulationParameterWidget("Pulse Duration Settings")
        self.interpulse_interval_widget = parameter_widgets.StimulationParameterWidget("Inter-pulse Interval Settings")
        self.channel_add_widget = channel_widget.ChannelAddWidget()

        self.plotter = plotter.StimTrainPlotter(self.manager)

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

        pulse_durations = self.pulse_duration_widget.input_values
        frequencies = self.frequency_widget.input_values
        intervals = self.interpulse_interval_widget.input_values

        # The current issue is tat non amplitude parameters, if they are constant, are shorter arrays than the ampltude array, so indexin doent work

        current_time = 0
        for i, channel_id in enumerate(channels):
            channel = Channel(channel_id, [])

            for j in range(train_length):
                amplitude = amplitudes[j]
                frequency = frequencies[j]
                duration = pulse_durations[j]

                start_time = current_time
                end_time = start_time + duration

                stim_event = StimTrainEvent(
                    amplitude,
                    start_time,
                    end_time,
                    frequency,
                )
                channel.events.append(stim_event)
                self.events.append(stim_event)
            
                # Update current_time for the interval event
                current_time = end_time
                
                # Calculate start and end times for the interval event
                interval_start_time = current_time
                interval_end_time = interval_start_time + intervals[j]
            
                interval_event = StimTrainEvent(
                    0,
                    interval_start_time,
                    interval_end_time,
                    0,
                )
                channel.events.append(interval_event)
                self.events.append(interval_event)
            
                # Update current_time for the next event
                current_time = interval_end_time

            self.manager.add_channel(channel)
            
        self.reset_to_default()
        self.show_plotter()

    def show_plotter(self):
        self.plotter.plot_data()
        self.plotter.show()

    def get_pulse_durations(self, number_of_pulses):
        pulse_durations = self.pulse_duration_widget.get_values()

        if self.pulse_duration_widget.get_current_mode() == "constant":
            pulse_durations = np.repeat(pulse_durations, number_of_pulses)

        if len(pulse_durations) != number_of_pulses:
            print("PulseDurationWidget Error: too many or too few pulse duration values")
            print(f"Actual length of durations list: {len(pulse_durations)}")
            print(f"Expected length of durations list: {number_of_pulses}")
            raise Exception
        
        return pulse_durations

    def get_frequencies(self, number_of_pulses):
        frequencies = self.frequency_widget.get_values()

        if self.frequency_widget.get_current_mode() == "constant":
            frequencies = np.repeat(frequencies, number_of_pulses)

        if len(frequencies) != number_of_pulses:
            print("FrequencyWidget Error: too many or too few frequecy values")
            print(f"Actual length of frequency list: {len(frequencies)}")
            print(f"Expected length of frequency list: {number_of_pulses}")
            raise Exception
        
        return frequencies
    
    def get_inter_pulse_intervals(self, number_of_pulses):
        intervals = self.interpulse_interval_widget.get_values()

        if self.interpulse_interval_widget.get_current_mode() == "constant":
            intervals = np.repeat(intervals, number_of_pulses)

        if len(intervals) != number_of_pulses:
            print("FrequencyWidget Error: too many or too few frequecy values")
            print(f"Actual length of frequency list: {len(intervals)}")
            print(f"Expected length of frequency list: {number_of_pulses}")
            raise Exception
        
        return intervals

    def reset_to_default(self):
        self.amplitude_widget.reset()
        self.pulse_duration_widget.reset()
        self.interpulse_interval_widget.reset()
        self.channel_add_widget.reset()
        self.frequency_widget.reset()
