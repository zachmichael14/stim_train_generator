import sys

from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QInputDialog, QPushButton, QDialog, QToolBar, QMenu)
from PySide6.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton

from plot_edit_dialog import IntervalEditDialog, PulseEditDialog


class StimTrainPlotter(QMainWindow):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.original_x_limit = None
        self.canvas_width = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Stim Train Plotter")
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.figure, self.axes = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.canvas_width = self.canvas.width()
        layout.addWidget(self.canvas)

        self.setup_toolbar()

        self.plot_data()

        self.setup_canvas_events()

        self.dragging = False
        self.drag_data = None
        self.clicked_bar = None

        self.setup_pan_timer()

    def setup_toolbar(self):
        toolbar = QToolBar(self)
        self.addToolBar(toolbar)

        for direction in ["<", ">"]:
            button = QPushButton(direction, self)
            button.pressed.connect(lambda d=direction: self.start_pan(d))
            button.released.connect(self.stop_pan)
            toolbar.addWidget(button)

    def setup_canvas_events(self):
        self.canvas.mpl_connect("scroll_event", self.on_zoom)
        self.canvas.mpl_connect("button_press_event", self.on_click)
        self.canvas.mpl_connect("button_release_event", self.on_release)
        self.canvas.mpl_connect("motion_notify_event", self.on_motion)

    def setup_pan_timer(self):
        self.pan_timer = QTimer(self)
        self.pan_timer.timeout.connect(self.do_pan)

    def create_context_menu(self, event):
        menu = QMenu(self)

        add_pulse_menu = menu.addMenu("Add Pulse")
        add_pulse_before = add_pulse_menu.addAction("Add Before")
        add_pulse_after = add_pulse_menu.addAction("Add After")

        add_interval_menu = menu.addMenu("Add Interval")
        add_interval_before = add_interval_menu.addAction("Add Before")
        add_interval_after = add_interval_menu.addAction("Add After")

        delete_action = menu.addAction("Delete")

        action = menu.exec(self.canvas.mapToGlobal(event.guiEvent.position().toPoint()))

        if action in (add_pulse_before, add_pulse_after):
            self.add_pulse(event.xdata, event.ydata, before=(action == add_pulse_before))
        elif action in (add_interval_before, add_interval_after):
            self.add_interval(event.xdata, event.ydata, before=(action == add_interval_before))
        elif action == delete_action:
            self.delete_item(event)

    def plot_data(self):
        self.axes.clear()
        
        y_ticks = []
        y_labels = []
        self.bar_data = []
        all_events = []
        max_x_limit = 0
    
        for channel in self.manager.channels:
            y_ticks.append(channel.id)
            y_labels.append(f"Channel {channel.id}")
            
            for event in channel.events:
                all_events.append((event.start_time, "pulse" if event.amplitude > 0 else "inter_pulse_interval", channel.id, event))
                max_x_limit = max(max_x_limit, event.end_time)
    
        all_events.sort()
        pulse_counter = 1
    
        self.axes.set_xlim(0, max_x_limit + 1000)  # Adding some buffer
    
        for start, event_type, channel_id, event in all_events:
            duration = event.end_time - event.start_time
            if event_type == "pulse":
                bar = self.axes.barh(channel_id, duration, left=start, color="blue", edgecolor="black")
                self.bar_data.append((bar, "pulse", channel_id, event, start, duration))
                self.add_pulse_text(channel_id, event, start, duration, pulse_counter)
                pulse_counter += 1
            elif event_type == "inter_pulse_interval":
                bar = self.axes.barh(channel_id, duration, left=start, color="gray", edgecolor="black")
                self.bar_data.append((bar, "inter_pulse_interval", channel_id, event, start, duration))
                self.add_interval_text(channel_id, start, duration)
    
        self.axes.set_yticks(y_ticks)
        self.axes.set_yticklabels(y_labels)
        self.axes.set_xlabel("Time (ms)")
        self.canvas.draw()


    def add_pulse_text(self, channel, event, start, duration, pulse_counter):
        text = f"#{pulse_counter}\n{event.amplitude}mA\n{event.frequency}Hz\n{duration:.1f}ms"
        if self.text_fits(duration, text):
            x_pos = start + duration / 2
            self.axes.text(x_pos, channel, text, ha="center", va="center", color="white", fontsize=8)

    def add_interval_text(self, channel, start, duration):
        text = f"{duration:.1f}ms"
        if self.text_fits(duration, text):
            x_pos = start + duration / 2
            self.axes.text(x_pos, channel, text, ha="center", va="center", color="white", fontsize=8)

    def text_fits(self, duration, text):
        text_width = self.calculate_text_width(text)
        current_x_limit = self.axes.get_xlim()
        box_width = (duration / (current_x_limit[1] - current_x_limit[0])) * self.canvas_width
        return text_width < box_width

    def calculate_text_width(self, text):
        renderer = self.canvas.get_renderer()
        temp_text = self.figure.text(0, 0, text)
        bbox = temp_text.get_window_extent(renderer)
        temp_text.remove()
        return (bbox.width + 20) / self.figure.dpi * 25.4

    def on_click(self, event):
        if event.button is MouseButton.LEFT:
            if event.inaxes != self.axes:
                return

            if event.dblclick:
                self.handle_double_click(event)
            else:
                self.handle_single_click(event)
        
        else:
            self.create_context_menu(event)

    def handle_double_click(self, event):
        for bar, bar_type, channel, index, start, duration in self.bar_data:
            contains, _ = bar[0].contains(event)
            if contains:
                if bar_type == "pulse":
                    self.edit_pulse_values(bar, channel, index)
                elif bar_type == "inter_pulse_interval":
                    self.edit_inter_pulse_interval_duration(bar, channel, index)
                break

    def handle_single_click(self, event):
        self.dragging = False
        self.drag_data = None

        for bar, bar_type, channel, index, start, duration in self.bar_data:
            contains, _ = bar[0].contains(event)
            if contains:
                self.dragging = True
                self.drag_data = (bar, bar_type, channel, index, start, duration, event.xdata)
                self.clicked_bar = bar
                break

    def on_motion(self, event):
        if not self.dragging or self.drag_data is None or event.xdata is None:
            return

        bar, bar_type, channel, index, start, duration, start_x = self.drag_data
        delta_x = event.xdata - start_x

        new_duration = max(1, round(duration + delta_x))

        if bar_type == "pulse":
            self.data[channel]["pulse_durations"][index] = new_duration
        elif bar_type == "inter_pulse_interval":
            self.data[channel]["inter_pulse_intervals"][index] = new_duration

        self.plot_data()

    def on_release(self, event):
        self.dragging = False
        self.drag_data = None

    def start_pan(self, direction):
        self.pan_direction = direction
        self.pan_timer.start(50)

    def stop_pan(self):
        self.pan_timer.stop()
        self.pan_direction = None

    def on_zoom(self, event):
        base_scale = 1.2
        current_x_limit = self.axes.get_xlim()
        x_data = event.xdata

        if event.button == "up":
            scale_factor = 1 / base_scale
        elif event.button == "down":
            scale_factor = base_scale
        else:
            scale_factor = 1

        new_width = (current_x_limit[1] - current_x_limit[0]) * scale_factor
        relative_x = (current_x_limit[1] - x_data) / (current_x_limit[1] - current_x_limit[0])

        new_x_min = max(0, x_data - new_width * (1 - relative_x))
        new_x_max = x_data + new_width * relative_x

        max_x_limit = self.calculate_max_x_limit()

        new_x_min = max(0, min(new_x_min, max_x_limit - new_width))
        new_x_max = min(max_x_limit, new_x_max)

        self.axes.set_xlim([new_x_min, new_x_max])
        self.original_x_limit = self.axes.get_xlim()

        self.plot_data()

    def calculate_max_x_limit(self):
        max_last_value = 0

        for _, _, channel, _, start, duration in self.bar_data:
            if duration > 0:
                end_time = start + duration
                if end_time > max_last_value:
                    max_last_value = end_time

        return max_last_value + 1000

    def do_pan(self):
        if self.pan_direction is None:
            return

        current_x_limit = self.axes.get_xlim()
        pan_step = 50
        new_x_min, new_x_max = current_x_limit
        if self.pan_direction == "<":
            new_x_min = max(0, current_x_limit[0] - pan_step)
            new_x_max = max(new_x_min + (current_x_limit[1] - current_x_limit[0]), current_x_limit[1] - pan_step)
        elif self.pan_direction == ">":
            new_x_min = max(0, current_x_limit[0] + pan_step)
            new_x_max = current_x_limit[1] + pan_step

        self.axes.set_xlim([new_x_min, new_x_max])
        self.original_x_limit = self.axes.get_xlim()

        self.plot_data()

    def edit_pulse_values(self, bar, channel, event):
        dialog = PulseEditDialog(event.amplitude, event.frequency, event.end_time - event.start_time, self)
        if dialog.exec() == QDialog.Accepted:
            new_amplitude, new_frequency, new_duration = dialog.get_values()
            self.manager.update_event(channel, event, new_amplitude, new_frequency, new_duration)
            self.plot_data()

    def edit_inter_pulse_interval_duration(self, bar, channel, event):
        current_duration = event.start_time - bar[4]  # bar[4] is the start time of the interval
        dialog = IntervalEditDialog(current_duration, self)
        if dialog.exec() == QDialog.Accepted:
            new_duration = dialog.get_value()
            self.manager.update_interval(channel, event, new_duration)
            self.plot_data()
       
    def add_pulse(self, xdata, ydata, before):
        channel = round(ydata)
        amplitude, ok = QInputDialog.getDouble(self, "Amplitude", "Enter amplitude (mA):")
        if ok:
            frequency, ok = QInputDialog.getDouble(self, "Frequency", "Enter frequency (Hz):")
            if ok:
                duration, ok = QInputDialog.getDouble(self, "Duration", "Enter duration (ms):")
                if ok:
                    self.manager.add_pulse(channel, amplitude, frequency, duration, xdata, before)
                    self.plot_data()

    def add_interval(self, x, y, before=False):
        channel = int(round(y))
        dialog = IntervalEditDialog()
        if dialog.exec() == QDialog.Accepted:
            duration = dialog.get_values()
            self.manager.add_interval(channel, duration, x, before)
            self.plot_data()

    def find_insert_index(self, channel, x):
        total_time = 0
        for i in range(len(self.data[channel]['amplitudes'])):
            pulse_duration = self.data[channel]['pulse_durations'][i]
            if total_time + pulse_duration > x:
                return i
            total_time += pulse_duration
            if i < len(self.data[channel]['inter_pulse_intervals']):
                interval_duration = self.data[channel]['inter_pulse_intervals'][i]
                if total_time + interval_duration > x:
                    return i + 1
                total_time += interval_duration
        return len(self.data[channel]['amplitudes'])
    
    def undo(self):
        if self.undo_stack:
            command = self.undo_stack.pop()
            command.undo()
            self.redo_stack.append(command)

    def redo(self):
        if self.redo_stack:
            command = self.redo_stack.pop()
            command.execute()
            self.undo_stack.append(command)

    def delete_item(self, event):
        for bar, bar_type, channel, event_obj, start, duration in self.bar_data:
            for rect in bar:
                if rect.contains(event)[0]:
                    if bar_type == "pulse":
                        self.manager.delete_pulse(channel, event_obj)
                    elif bar_type == "inter_pulse_interval":
                        self.manager.delete_interval(channel, event_obj)
                    self.plot_data()
                    break
            
    def delete_item(self, event):
        for bar, bar_type, channel, index, start, duration in self.bar_data:
            for rect in bar:
                if rect.contains(event)[0]:
                    if bar_type == "pulse":
                        command = DeletePulseCommand(self, channel, index)
                        self.undo_stack.append(command)
                        command.execute()
                        self.redo_stack.clear()

    def delete_pulse(self, channel, index):
        # Remove the pulse
        del self.data[channel]['amplitudes'][index]
        del self.data[channel]['frequencies'][index]
        del self.data[channel]['pulse_durations'][index]

        # Check if deleting this pulse results in two sequential intervals
        if 0 < index < len(self.data[channel]['inter_pulse_intervals']):
            interval1 = self.data[channel]['inter_pulse_intervals'][index - 1]
            interval2 = self.data[channel]['inter_pulse_intervals'][index]
            combined_interval = interval1 + interval2
            self.data[channel]['inter_pulse_intervals'][index - 1] = combined_interval
            del self.data[channel]['inter_pulse_intervals'][index]

    def delete_interval(self, channel, index):
        # Remove the interval
        del self.data[channel]['inter_pulse_intervals'][index]
    
        # Check if deleting this interval results in two sequential pulses
        if index < len(self.data[channel]['amplitudes']) - 1:
            pulse1 = {
                'amplitude': self.data[channel]['amplitudes'][index],
                'frequency': self.data[channel]['frequencies'][index],
                'duration': self.data[channel]['pulse_durations'][index]
            }
            pulse2 = {
                'amplitude': self.data[channel]['amplitudes'][index + 1],
                'frequency': self.data[channel]['frequencies'][index + 1],
                'duration': self.data[channel]['pulse_durations'][index + 1]
            }
    
            if pulse1['amplitude'] == pulse2['amplitude'] and pulse1['frequency'] == pulse2['frequency']:
                # Combine the pulses
                combined_duration = pulse1['duration'] + pulse2['duration']
                self.data[channel]['pulse_durations'][index] = combined_duration
                del self.data[channel]['amplitudes'][index + 1]
                del self.data[channel]['frequencies'][index + 1]
                del self.data[channel]['pulse_durations'][index + 1]
            else:
                # Just delete the second pulse
                del self.data[channel]['amplitudes'][index + 1]
                del self.data[channel]['frequencies'][index + 1]
                del self.data[channel]['pulse_durations'][index + 1]

# if __name__ == "__main__":
#     data = {
#         1: {"amplitudes": [0.5, 1.0, 0.8],
#             "frequencies": [5, 10, 8],
#             "pulse_durations": [100, 150, 120],
#             "inter_pulse_intervals": [50, 60, 70]},
#         2: {"amplitudes": [0.6, 1.1, 0.9],
#             "frequencies": [6, 11, 9],
#             "pulse_durations": [110, 160, 130],
#             "inter_pulse_intervals": [55, 65, 75]},
#     }

#     app = QApplication(sys.argv)
#     window = StimTrainPlotter(data)
#     window.show()
#     sys.exit(app.exec())
