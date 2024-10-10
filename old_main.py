
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

class StimLoopMode(enum.Enum):
    """Loop mode determines how a stim train should loop.

    Options:
        - NO_LOOP - Stim will cease when the end of the train is reached.
        - LOOP_LAST - Train's last stim will loop until manually stopped.
        - LOOP_ALL - Train will start from the beginning when end is reached.
    """
    NO_LOOP = 1
    LOOP_LAST = 2
    LOOP_ALL = 3


class StimWorker:
    def __init__(self) -> None:
        self.daq = None

        self.uploaded_stims = None
        self.scheduled_stim_events = []

        # self.thread_lock = threading.Lock()
        # self.pause_condition = threading.Condition(self.thread_lock)
        # self.stim_is_paused = False
        # self.thread_is_running = False
        
        self.loop_mode = StimLoopMode.NO_LOOP

    def run(self) -> None:
        # self.thread_is_running = True

        # Execution delay represents the time it takes for the code to execute
        # from the end of one period to just before sleeping for the next
        # period. It's subtracted from the sleep time just before sleeping to 
        # account for execution time.
        execution_delay_start_time = time.perf_counter()

        # Additionally, subtracting a small offset from the sleep time seems to
        # stabilize higher frequencies
        timer_offset = 0.00001

        while self.thread_is_running:
            if self.stim_is_paused:
                with self.thread_lock:
                    self.pause_condition.wait()
                continue

            if not self.scheduled_stim_events:
                self._handle_end_of_events()
                # No events to reschedule after handling
                if not self.scheduled_stim_events:  
                    break

            _, _, amplitude, expected_period = self.scheduled_stim_events[0]

            self.daq.set_amplitude(amplitude)
            self.daq.trigger()

            self._precise_sleep(expected_period - (time.perf_counter() - execution_delay_start_time) - timer_offset)
            
            heapq.heappop(self.scheduled_stim_events)
            execution_delay_start_time = time.perf_counter()
        print("~~~ Run Complete ~~~")

    def _precise_sleep(self, duration: float) -> None:
        end_time = time.perf_counter() + duration
        while time.perf_counter() < end_time:
            remaining = end_time - time.perf_counter()
            if remaining > 0.001:
                time.sleep(0.0005)
            else: # Busy-wait for the last sub-millisecond
                pass

    def _handle_end_of_events(self) -> None:
        if self.loop_mode == StimLoopMode.NO_LOOP:
            self.thread_is_running = False
            #TODO: Change settings here to allow for pressing stim again after finishing
        elif self.loop_mode == StimLoopMode.LOOP_LAST:
            last_stim = self.uploaded_stims.iloc[-1]
            self._schedule_single_event(last_stim)
        elif self.loop_mode == StimLoopMode.LOOP_ALL:
            self._schedule_all_events()

    def _schedule_all_events(self) -> None:
        for _, row in self.uploaded_stims.iterrows():
            self._schedule_single_event(row)

    def _schedule_single_event(self, stim_data: pd.Series):
        timepoint, frequency, amplitude, delay = stim_data
        heapq.heappush(self.scheduled_stim_events, (timepoint, frequency, amplitude, delay))

    def schedule_events(self, data: pd.DataFrame) -> None:
        with self.thread_lock:
            self.uploaded_stims = data.copy()
            self.scheduled_stim_events = []
            self._schedule_all_events()

        if self.daq is None:
            self.daq = DAQ()

    def set_mode(self, mode: StimLoopMode):
        self.loop_mode = mode    

    def pause(self):
        with self.thread_lock:
            if not self.stim_is_paused and self.thread_is_running:
                self.stim_is_paused = True

    def resume(self):
        with self.thread_lock:
            if self.stim_is_paused:
                self.stim_is_paused = False
                self.pause_condition.notify_all()

    def stop(self):
        with self.thread_lock:
            self.thread_is_running = False
            self.stim_is_paused = False
            self.scheduled_stim_events.clear()
            self.pause_condition.notify_all()


class ContinuousStimManager(QObject):
    signal_stim_finished = Signal(bool)

    def __init__(self):
        super().__init__()
        self.worker = StimWorker()
        self.stim_thread = None
        self.data = None

    @Slot(str)
    def upload_stims_callback(self, file_name: str) -> None:
        input_data = pd.read_csv(file_name)
        self.data = self._generate_intermediates(input_data)
        self._create_stim_file(file_name)
        self.worker.schedule_events(self.data)

    def _create_stim_file(self, input_file_name: str) -> None:
        output_file_name = Path(input_file_name).stem
        output_csv_name = f"{output_file_name}_ramped.csv"
        self.data.to_csv(output_csv_name, index=False)

    @Slot(str)
    def stim_mode_callback(self, mode: StimLoopMode) -> None:
        if self.worker:
            self.worker.set_mode(mode)

    @Slot(bool)
    def stim_callback(self, start_stim_bool: bool) -> None:
        if self.data is None or self.data.empty:
            print("Stim file hasn't been uploaded or is empty.")
            print("Check stim file and try again.")
            return

        if start_stim_bool:
            self._begin_stim_thread()
        else:
            self.worker.pause()

    def _begin_stim_thread(self) -> None:
        if self.stim_thread is None or not self.stim_thread.is_alive():
            self.stim_thread = threading.Thread(target=self._stim_worker,
                                                daemon=True,
                                                )
            self.stim_thread.start()
        else:
            self.worker.resume()

    def _stim_worker(self) -> None:
        self.worker.run()
        self.signal_stim_finished.emit(True)

    @Slot(bool)
    def interrupt_stim_callback(self, interrupt_bool: bool) -> None:
        if interrupt_bool:
            self._stop_stim_thread()
        else:
            self.worker.resume()

    def _stop_stim_thread(self) -> None:
        if self.stim_thread and self.stim_thread.is_alive():
            self.worker.stop()
            self.stim_thread.join()
            self.stim_thread = None
        print("Stim stopped and thread joined.")

    ###################################
    ### AMPLITUDE/FREQUENCY RAMPING ###
    ###################################  
    def _generate_intermediates(self, data_frame):
        # Add first row first since loop below is for calculating next row
        timepoint, frequency, amplitude = data_frame.iloc[0]
        results = [(timepoint, frequency, amplitude, 1/frequency)]
        
        # Calculate values for next row
        for i in range(len(data_frame) - 1):
            start_time = data_frame.iloc[i, 0]
            end_time = data_frame.iloc[i + 1, 0]

            start_freq = data_frame.iloc[i, 1]
            end_freq = data_frame.iloc[i + 1, 1]

            start_amplitude = data_frame.iloc[i, 2]
            end_amplitude = data_frame.iloc[i + 1, 2]

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
                results.append((timepoint, result[1], amplitude_function(timepoint), 1/result[1]))

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
                               columns=["time", "frequency", "amplitude", "delay"])
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
            results = results.dropna(axis=1, how='all')
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
        time_remaining = end_time - results.loc[len(results) - 1, "time"]

        if time_remaining <= 0:
            return results


        # Frequency may be within +-0.1% of ceiling and floor
        frequency_floor = min(start_frequency, end_frequency)
        frequency_floor = frequency_floor - (frequency_floor * 0.001)

        frequency_ceiling = max(start_frequency, end_frequency)
        frequency_ceiling = frequency_ceiling + (frequency_ceiling * 0.001)

    
        frequency_to_add = 1 / time_remaining
        frequency_to_add = np.round(frequency_to_add, 6)
        last_index = len(results)

        # Early return when frequency doesn"t fit in range
        if frequency_to_add > frequency_ceiling:
            time_remaining = end_time - results.loc[len(results) - 2, "time"]
            frequency_to_add = 1 / time_remaining
            # Leaving in the last stim would mean it the new frequency will
            # exceed desired time, so we need to omit it
            last_index = len(results) - 1
        elif frequency_to_add < frequency_floor:
            print(f"{frequency_to_add} Hz is below frequency floor ({frequency_floor} Hz).")
    
        
        # Insert frequency in proper place to maintain ramp order
        # searchsorted() requires ascending order
        insert_index = results["frequency"].searchsorted(frequency_to_add,
                                                         sorter=np.argsort(results["frequency"]),
                                                         )
        
        replaced_frequency = results.loc[insert_index, "frequency"].copy()

        results.loc[insert_index, "frequency"] = frequency_to_add

        # Add back in the replaced frequency
        new_row = pd.DataFrame({"time": [None], "frequency": [replaced_frequency]}, index=[insert_index + 1])

        new_row = new_row.dropna(axis=1, how='all')

        results = pd.concat([results.loc[:insert_index], new_row, results.iloc[insert_index + 1:last_index]]).reset_index(drop=True)

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

    signal_stim_mode = Signal(StimLoopMode)

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
            self.signal_stim_mode.emit(StimLoopMode.LOOP_LAST)

    @Slot()
    def stop_at_end_callback(self):
        if self.radio_stop_at_end.isChecked():
            self.signal_stim_mode.emit(StimLoopMode.NO_LOOP)

    @Slot()
    def loop_callback(self):
        if self.radio_loop.isChecked():
            self.signal_stim_mode.emit(StimLoopMode.LOOP_ALL)

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
    manager = ContinuousStimManager()

    widget.signal_stim_button_pressed.connect(manager.stim_callback)
    widget.signal_interrupt_button_pressed.connect(manager.interrupt_stim_callback)
    widget.signal_stims_uploaded.connect(manager.upload_stims_callback)
    widget.signal_stim_mode.connect(manager.stim_mode_callback)

    manager.signal_stim_finished.connect(widget.stim_finished_callback)

    window.setCentralWidget(widget)
    window.setWindowTitle("Stim Train Generator")
    window.show()
    sys.exit(app.exec())