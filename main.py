
import csv
from datetime import datetime
import enum
import heapq
from os import path
from pathlib import Path
import sys
import threading
import time
from typing import List, Tuple

import numpy as np
import pandas as pd
from PySide6 import QtWidgets
from PySide6.QtCore import QObject, Signal, Slot

from daq import DAQ

class StimMode(enum.Enum):
    STOP_AT_END = 1
    LOOP_LAST = 2
    LOOP_ALL = 3


class StimWorker:
    def __init__(self, log_file):
        self.daq = DAQ()
        self.paused = False
        self.events = []  # Store scheduled events
        self.pause_start_time = 0
        self.total_pause_duration = 0
        self.running = False
        self.lock = threading.Lock()
        self.pause_condition = threading.Condition(self.lock)
        self.start_time = None
        self.mode = StimMode.STOP_AT_END
        self.original_data = None
        self.last_actual_time = None
        self.next_event_time = None
        self.log_file = log_file
        self._initialize_csv()

    def _initialize_csv(self):
        """Initializes the CSV file with headers."""
        with open(self.log_file, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Expected Time",
                             "Actual Time",
                             "Amplitude",
                             "Expected Frequency",
                             "Actual Frequency",
                             "Period Expected",
                             "Period Actual",
                             ])

    def _log_event(self,
                   expected_time,
                   actual_time,
                   amplitude,
                   frequency,
                   freq_from_actual_period,
                   period_expected,
                   period_actual,
                   ):
        """Logs the expected and actual event times along with additional data."""
        with open(self.log_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([expected_time,
                             actual_time,
                             amplitude,
                             frequency,
                             freq_from_actual_period,
                             period_expected,
                             period_actual,
                             ])

    def _time(self):
        if self.start_time is None:
            return 0
        return time.perf_counter() - self.start_time - self.total_pause_duration

    def _stimulate(self, frequency, amplitude, expected_time):
        actual_time = self._time()
        self.daq.trigger()

        # Calculate the expected period
        period_expected = 1 / frequency

        # Calculate the actual period using the last actual time
        if self.last_actual_time is not None:
            period_actual = actual_time - self.last_actual_time
        else:
            period_actual = period_expected  # For the first stimulation

        # Calculate the frequency based on the actual period
        freq_from_actual_period = 1 / period_actual if period_actual > 0 else frequency

        # Update last actual time for the next pulse
        self.last_actual_time = actual_time

        # Log the event with all necessary details
        self._log_event(expected_time,
                        actual_time,
                        amplitude,
                        frequency,
                        freq_from_actual_period,
                        period_expected,
                        period_actual,
                        )

    def run(self):
        self.running = True
        self.start_time = time.perf_counter()
        while self.running:
            if self.paused:
                with self.lock:
                    self.pause_condition.wait()
                continue

            if not self.events:
                self._handle_end_of_events()
                if not self.events:  # If still no events after handling
                    break
            
            next_event_time, frequency, amplitude = self.events[0]

            # if next_event_time == 0:
            #     # self._stimulate(frequency, amplitude, next_event_time)
            #     heapq.heappop(self.events)
            # else:

            current_time = self._time()

            wait_time = next_event_time - current_time

            # if wait_time + current_time > next_event_time:
            #     print(f"Cannot stim at {frequency} becuase its period will execeed expected timepoint {current_time:.3f} + {1 / frequency:.3f} ({wait_time + current_time:.3f}) > {next_event_time}.")
            #     print("Skipping...")
            #     continue

            if wait_time <= 0:
                self._stimulate(frequency, amplitude, next_event_time)
                heapq.heappop(self.events)
            else:
                self._precise_sleep(wait_time)
        print("~~~ Run Complete ~~~")

    def _precise_sleep(self, duration):
        # self.time
        end_time = time.perf_counter() + duration
        while time.perf_counter() < end_time:
            remaining = end_time - time.perf_counter()
            if remaining > 0.001:
                time.sleep(0.0009)  # Sleep in small increments
            else:
                # Busy-wait for the last sub-millisecond
                pass

    def schedule_events(self, data):
        with self.lock:
            self.original_data = data.copy()
            self.events = []
            for index, row in data.iterrows():
                timepoint, frequency, amplitude = row
                heapq.heappush(self.events, (timepoint, frequency, amplitude))
            if self.events:
                self.next_event_time = self.events[0][0]
   
    def set_mode(self, mode: StimMode):
        self.mode = mode

    def _handle_end_of_events(self):
        if self.mode == StimMode.STOP_AT_END:
            self.running = False
        elif self.mode == StimMode.LOOP_LAST:
            last_stim = self.original_data.iloc[-1]
            self._schedule_single_event(last_stim)
        elif self.mode == StimMode.LOOP_ALL:
            self._reschedule_all_events()

    def _schedule_single_event(self, stim_data):
        current_time = self._time()
        timepoint, frequency, amplitude = stim_data
        new_timepoint = current_time + (1 / frequency)
        heapq.heappush(self.events, (new_timepoint, frequency, amplitude))

    def _reschedule_all_events(self):
        current_time = self._time()
        for index, row in self.original_data.iterrows():
            timepoint, frequency, amplitude = row
            new_timepoint = current_time + timepoint
            heapq.heappush(self.events, (new_timepoint, frequency, amplitude))

    def pause(self):
        with self.lock:
            if not self.paused and self.running:
                self.paused = True
                self.pause_start_time = time.perf_counter()

    def resume(self):
        with self.lock:
            if self.paused:
                self.paused = False
                self.total_pause_duration += time.perf_counter() - self.pause_start_time
                self.pause_condition.notify_all()

    def stop(self):
        with self.lock:
            self.running = False
            self.paused = False
            self.events.clear()
            self.total_pause_duration = 0
            self.start_time = None
            self.pause_condition.notify_all()

    def is_finished(self):
        return not self.running or (not self.paused and len(self.events) == 0)


class ContinuousStimManager(QObject):
    signal_stim_finished = Signal(bool)

    def __init__(self, daq):
        super().__init__()
        self.daq = daq
        self.worker = None
        self.stim_thread = None
        self.data = None
        self.log_file = None

    @Slot(str)
    def stim_mode_callback(self, mode: str):
        if self.worker:
            if mode.casefold() == "loop":
                self.worker.set_mode(StimMode.LOOP_ALL)
            elif mode.casefold() == "final":
                self.worker.set_mode(StimMode.LOOP_LAST)
            else:
                self.worker.set_mode(StimMode.STOP_AT_END)

    # @Slot(bool)
    def stim_callback(self, start_stim):
        if self.data is None or self.data.empty:
            print("Stim incorrectly configured")
            return

        if start_stim:
            self._begin_stim_thread()
        else:
            if self.worker:
                self.worker.pause()

    @Slot(bool)
    def interrupt_stim_callback(self, interrupt_bool):
        if interrupt_bool:
            self._stop_stim_thread()
        else:
            if self.worker:
                self.worker.resume()

    def run_csv(self, file_name):
        input_data = pd.read_csv(file_name)
        self.data = input_data
        self.data = self._generate_intermediates(input_data)
        output_file_name = Path(file_name).stem
        output_csv = f"benchmarks\\ramped_timepoints\\{output_file_name}_ramped.csv"

        self.log_file = f"benchmarks\\results\\stim_log_{output_file_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"

        self.data.to_csv(output_csv, index=False)

        self.worker = StimWorker(self.log_file)
        self.worker.schedule_events(self.data)
        self.stim_thread = threading.Thread(target=self._stim_worker)
        self.stim_thread.start()
        self.stim_thread.join()

    @Slot(str)
    def upload_stims_callback(self, file_name):
        input_data = pd.read_csv(file_name)
        self.data = self._generate_intermediates(input_data)
        output_file_name = Path(file_name).stem
        output_csv = f"{output_file_name}_ramped.csv"

        self.log_file = f"stim_log_{output_file_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"
        self.data.to_csv(output_csv, index=False)
        if self.worker:
            self.worker.schedule_events(self.data)

    def _begin_stim_thread(self):
        if self.stim_thread is None or not self.stim_thread.is_alive():
            self.worker = StimWorker(self.log_file)
            self.worker.schedule_events(self.data)
            self.stim_thread = threading.Thread(target=self._stim_worker, daemon=True)
            self.stim_thread.start()
        else:
            if self.worker:
                self.worker.resume()

    def _stim_worker(self):
        self.worker.run()
        self.signal_stim_finished.emit(True)

    def _stop_stim_thread(self):
        if self.stim_thread and self.stim_thread.is_alive():
            self.worker.stop()
            self.stim_thread.join()
            self.stim_thread = None
        print("Stim stopped and thread joined.")

    ###################################
    ### AMPLITUDE/FREQUENCY RAMPING ###
    ###################################  
    def _generate_intermediates(self, data_frame):
        results = [(value for value in data_frame.iloc[0])]

        for i in range(len(data_frame) - 1):
            start_time = data_frame.iloc[i]["timepoint"]
            end_time = data_frame.iloc[i + 1]["timepoint"]

            start_freq = data_frame.iloc[i]["frequency"]
            end_freq = data_frame.iloc[i + 1]["frequency"]

            start_amplitude = data_frame.iloc[i]["amplitude"]
            end_amplitude = data_frame.iloc[i + 1]["amplitude"]

            amplitude_function = self._get_linear_function(start_time,
                                                           end_time,
                                                           start_amplitude,
                                                           end_amplitude)
            
            f_ramp_results = self._calculate_timepoints(start_time,
                                                        end_time,
                                                        start_freq,
                                                        end_freq)

            for result in f_ramp_results:
                timepoint = result[0]
                results.append((timepoint, result[1], amplitude_function(timepoint)))

            # elif start_amplitude != end_amplitude:
            #     print("Handle the situation where frequency doesn"t ramp but amplitude does.")
            # else:
            #     # results.append([end_time, end_freq, end_amplitude])

                # No ramp required (start_freq == end_freq)
                # amplitudes = []
                # for result in f_ramp_results:
                    # timepoint = result[0]
                    # amplitudes.append(line_function(timepoint))

        results = pd.DataFrame(results,
                               columns=["timepoint", "frequency", "amplitude"])
        return results    
    
    def _calculate_timepoints(self, start_time, end_time, start_frequency, end_frequency):
        results = pd.DataFrame(columns=["time", "frequency"])        

        ramp_function = self._get_linear_function(
                start_time,
                end_time,
                start_frequency,
                end_frequency)
        
        current_frequency = start_frequency
        next_timepoint = start_time + (1 / current_frequency)

        while next_timepoint <= end_time:
            next_frequency = ramp_function(next_timepoint)
            
            new_row = pd.DataFrame({"time": [next_timepoint], "frequency": [next_frequency]})
            results = pd.concat([results, new_row], ignore_index=True)
            
            current_frequency = next_frequency
            period = 1 / current_frequency
            next_timepoint += period
                
        results = self._handle_last_timepoint(results, end_time, start_frequency, end_frequency)
        
        # Convert results to a list of tuples for further processing
        result_tuples = [tuple(x) for x in results.to_records(index=False)]

        if result_tuples[-1][0] + 1/result_tuples[-1][1] == end_time:
            result_tuples.append((end_time, end_frequency))

        return result_tuples
    
    def _handle_last_timepoint(self, results, end_time, start_frequency, end_frequency):
        time_remaining = end_time - results.iloc[-1]["time"]
        frequency_floor = min(start_frequency, end_frequency)
        frequency_ceiling = max(start_frequency, end_frequency)
    
        frequency_to_add = 1 / time_remaining

        # Early return when frequency doesn"t fit in range
        if frequency_to_add > frequency_ceiling:
            print(f"{frequency_to_add} Hz is above frequency ceiling ({frequency_ceiling} Hz).")
            return results        
        elif frequency_to_add < frequency_floor:
            print(f"{frequency_to_add} Hz is below frequency floor ({frequency_floor} Hz).")
            return results
        
        # Insert frequency in proper place to maintain ramp order
        # searchsorted() requires ascending order
        insert_index = results["frequency"].searchsorted(frequency_to_add,
                                                         sorter=np.argsort(results["frequency"]),
                                                         )
        
        replaced_frequency = results.loc[insert_index, "frequency"].copy()

        results.loc[insert_index, "frequency"] = frequency_to_add

        # Add back in the replaced frequency
        new_row = pd.DataFrame({"time": [None], "frequency": [replaced_frequency]}, index=[insert_index + 1])

        results = pd.concat([results.loc[:insert_index], new_row, results.iloc[insert_index + 1:]]).reset_index(drop=True)

        results = self.recalculate_time(results)

        # Ensure the requested end_frequency is included
        if results.loc[len(results) - 1, "frequency"] != end_frequency:
            results.loc[len(results) - 1, "frequency"] = end_frequency
        
        return results
    
    def recalculate_time(self, df):
        """"""
        for i in range(1, len(df)):
            df.loc[i, "time"] = df.loc[i-1, "time"] + (1 / df.loc[i-1, "frequency"])

        return df

    def _get_linear_function(self,
                                x1: float,
                                x2: float,
                                y1: float,
                                y2:float
                                ):
        slope = (y2 - y1) / (x2 - x1)
        intercept = y1 - slope * x1
        return lambda x: slope * x + intercept
    

class TestWidget(QtWidgets.QWidget):
    signal_stim_button_pressed = Signal(bool)
    signal_interrupt_button_pressed = Signal(bool)
    signal_stims_uploaded = Signal(str)

    signal_stim_mode = Signal(str)

    def __init__(self):
        super().__init__()
        main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(main_layout)

        self.upload_button = QtWidgets.QPushButton("Upload Stims")
        self.upload_button.clicked.connect(self.upload_stim_callback)
        main_layout.addWidget(self.upload_button)

        self.stim_button = QtWidgets.QPushButton("Start Stim")
        self.stim_button.clicked.connect(self.stim_button_callback)
        main_layout.addWidget(self.stim_button)

        self.interrupt_button = QtWidgets.QPushButton("Kill Stim")
        self.interrupt_button.clicked.connect(self.interrupt_stim_callback)
        main_layout.addWidget(self.interrupt_button)


        self.radio_stop_at_end = QtWidgets.QRadioButton("Stop at End")
        self.radio_stop_at_end.toggled.connect(self.stop_at_end_callback)

        self.radio_continue_final_stim = QtWidgets.QRadioButton("Continue Final Stim")
        self.radio_continue_final_stim.toggled.connect(self.continue_final_callback)

        self.radio_loop = QtWidgets.QRadioButton("Loop")
        self.radio_loop.toggled.connect(self.loop_callback)

        # Create a button group and add radio buttons to it
        self.button_group = QtWidgets.QButtonGroup(self)
        self.button_group.addButton(self.radio_stop_at_end)
        self.button_group.addButton(self.radio_continue_final_stim)
        self.button_group.addButton(self.radio_loop)

        # Add radio buttons to layout
        main_layout.addWidget(self.radio_stop_at_end)
        main_layout.addWidget(self.radio_continue_final_stim)
        main_layout.addWidget(self.radio_loop)

        # Set default selection (optional)
        self.radio_stop_at_end.setChecked(True)

    #################
    ### CALLBACKS ###
    #################
    @Slot()  
    def continue_final_callback(self):
        if self.radio_continue_final_stim.isChecked():
            self.signal_stim_mode.emit("final")

    @Slot()
    def stop_at_end_callback(self):
        if self.radio_stop_at_end.isChecked():
            self.signal_stim_mode.emit("stop")

    @Slot()
    def loop_callback(self):
        if self.radio_loop.isChecked():
            self.signal_stim_mode.emit("loop")

    @Slot()
    def upload_stim_callback(self):
        # getOpenFileName also returns a filter, which is not needed
        stim_file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 
                                                   caption="Select Stim File")
        
        # The above returns paths separated with "/" (for Unix-like OSs).
        # Replace all "/" with path separator of current OS.
        # If current OS is Unix-like, the replacement will be redundant.
        if not stim_file_path:
            return
        
        stim_file_path = stim_file_path.replace("/", path.sep)
        self.signal_stims_uploaded.emit(stim_file_path)

    @Slot()
    def stim_button_callback(self):
        button_state = self.stim_button.text().casefold()

        # Start stim
        if "start" in button_state:
            self.signal_stim_button_pressed.emit(True)
            self.stim_button.setText("Pause Stim")

        # Pause stim
        elif "pause" in button_state:
            self.signal_stim_button_pressed.emit(False)
            # Set to opposite option
            self.stim_button.setText("Start Stim")

    @Slot()
    def interrupt_stim_callback(self):        
        self.signal_interrupt_button_pressed.emit(True)
    
    @Slot()
    def stim_finished_callback(self):
        self.stim_button.setText("Start Stim") 

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    daq = DAQ()
    widget = TestWidget()
    manager = ContinuousStimManager(None)

    widget.signal_stim_button_pressed.connect(manager.stim_callback)
    widget.signal_interrupt_button_pressed.connect(manager.interrupt_stim_callback)
    widget.signal_stims_uploaded.connect(manager.upload_stims_callback)
    widget.signal_stim_mode.connect(manager.stim_mode_callback)

    manager.signal_stim_finished.connect(widget.stim_finished_callback)

  
    window.setCentralWidget(widget)
    window.setWindowTitle("Stim Train Generator")
    window.show()

    # file = Path("C:\\Users\\Lab\\zach\\stim_train_generator\\60hz_5_interval_const_amp_short_ramped.csv")

    # dir_path = Path("C:\\Users\\Lab\\zach\\stim_train_generator\\benchmarks\\tests")

    
    # if not dir_path.is_dir():
    #     raise NotADirectoryError(f"{dir_path} is not a valid directory.")
    
    # # Iterate through files in the directory
    # for i in range(1):
    #     print(f"~~~ Pass #{i} ~~~")
    #     for file in dir_path.iterdir():
    #         print(f"File: {file}")
    #         if file.is_file():  # Ensures it"s a file, not a directory
    #             manager.run_csv(file)
    #         print("~~~ Done with file ~~~ \n")
    # print("~~~ Fin ~~~")

    # for file in dir_path.iterdir():
    #     print(f"File: {file}")
    #     if file.is_file():  # Ensures it"s a file, not a directory
    #     manager.run_csv(file)

    # while True:
    #     manager.run_csv(file)
    #     print("~~~ Done with file ~~~ \n")
    # print("~~~ Fin ~~~")
    
    sys.exit(app.exec())

#####################################
## PLOTTER ONLY TEST:
# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)

#     file = "test.csv"
#     manager = stim_data_manager.StimDataManager()
#     manager.load_from_csv("test.csv")

#     tp = plotter.StimTrainPlotter(manager)
#     tp.show()
#     # tp.load_data(file)

#     sys.exit(app.exec())

#####################################


#####################################
### PICO TEST ###
# if __name__ == "__main__":
#     from pico.pico_interface import PicoInterface

#     pico = PicoInterface("COM8")  # Adjust port as needed

#     try:
#         print("Setting channel only:")
#         pico.set_params(channel=0)
#         print("Setting amplitude only:")
#         pico.set_params(amplitude=0)
#         print("Setting frequency only:")
#         pico.set_params(frequency=1000.0)
#         print("Setting all params:")
#         pico.set_params(amplitude=50, frequency=1000.0)
    # except Exception as e:
    #     print(f"Error: {e}")
    # finally:
    #     pico.close()
#####################################



# def _calculate_timepoints_backward(self, end_time, start_time, end_frequency, start_frequency):
#         results = []
#         # results = [(end_time, end_frequency)]
#         time_remaining = end_time - start_time

#         if time_remaining < 0.0001: # 0.1 ms
#             return
        
#         linear_function = self._get_linear_function(start_time,
#                                                     end_time,
#                                                     start_frequency,
#                                                     end_frequency)
#         current_time = end_time
#         current_frequency = end_frequency

#         while current_time > start_time:

#             current_period = (1 / current_frequency)

#             previous_timepoint = (current_time - current_period)

            # if current_period > (end_time - start_time) or previous_timepoint <= start_time:
                # previous_timepoint < start_time:
                # print(f"Warning: Period of {current_frequency} Hz ({current_period:.3f} s) at timepoint {current_time} exceeds desired ramp time of {end_time - start_time:.3f} s. This will produce erroneous stimulation.")
                # print(f"Actual frequency will be approximately {1 / (end_time - start_time):.3f} Hz.")
                # break
            
        #     previous_frequency = linear_function(previous_timepoint)
        #     results.append((previous_timepoint, previous_frequency))

        #     current_time = previous_timepoint
        #     current_frequency = previous_frequency

        # print(results)
        # return results[::-1]
    
    # def _calculate_timepoints_forward(self, end_time, start_time, end_frequency, start_frequency):
    #     results = pd.DataFrame(columns=["time", "frequency"])

    #     current_time = start_time
    #     current_frequency = start_frequency

    #     linear_function = self._get_linear_function(
    #             start_time,
    #             end_time,
    #             start_frequency,
    #             end_frequency)

    #     while current_time < end_time:
    #         period = 1 / current_frequency
    #         next_timepoint = current_time + period

    #         next_frequency = linear_function(next_timepoint)
            
    #         if next_timepoint <= end_time:
    #             new_row = pd.DataFrame({"time": [next_timepoint], "frequency": [next_frequency]})
    #             results = pd.concat([results, new_row], ignore_index=True)
    #             current_time = next_timepoint
    #             current_frequency = next_frequency
    #         else:
    #             ideal_period = end_time - current_time
    #             frequencies = [1 / ideal_period]

    #             #search-sorted requires ascending order (use negative index)
    #             insert_index = results["frequency"].searchsorted(frequencies[0], sorter=np.argsort(results["frequency"]))

    #             insert_index = len(results) - insert_index

    #             freqs = results.iloc[insert_index:]["frequency"].to_list()

    #             for frequency in freqs:
    #                 frequencies.append(frequency)


    #             for i in range(insert_index, len(results)):
    #                 results.loc[i, "frequency"] = frequencies[i - insert_index]

    #             # Adjust timepoints based on updated frequencies
    #             for i in range(insert_index + 1, len(results)):
    #                 period = 1 / results.loc[i - 1, "frequency"]
    #                 results.loc[i, "time"] = results.loc[i - 1, "time"] + period
    #             break 

    #     # Convert results to a list of tuples for further processing
    #     result_tuples = [tuple(x) for x in results.to_records(index=False)]

    #     if result_tuples[-1][0] + 1/result_tuples[-1][1] == end_time:
    #         result_tuples.append((end_time, end_frequency))

    #     return result_tuples
    # def _get_x_function(self,
    #                             x1: float,
    #                             x2: float,
    #                             y1: float,
    #                             y2:float
    #                             ):
    #     slope = (y2 - y1) / (x2 - x1)
    #     intercept = y1 - slope * x1
    #     return lambda x: (x - intercept) / slope


        # def _calculate_timepoints_no_ramp(self, end_time, start_time, frequency):
        # results = []
        # period = 1 / frequency
        # current_time = start_time
        
        # while current_time + period < end_time:
        #     timepoint = current_time + period
        #     results.append((timepoint, frequency))
        #     current_time = timepoint
        # return results