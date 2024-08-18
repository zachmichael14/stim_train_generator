import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from matplotlib.patches import Rectangle

# Import the StimDataManager and StimEvent classes
from stim_data_manager import StimDataManager, StimEvent

class BarGraphPlotter(FigureCanvas):
    def __init__(self, stim_data_manager):
        self.fig, self.ax = plt.subplots()
        super().__init__(self.fig)
        self.stim_data_manager = stim_data_manager
        self.selected_patch = None

        # Render the initial plot
        self.render_plot()

        # Connect event listeners
        self.mpl_connect('button_press_event', self.on_click)
        self.mpl_connect('button_release_event', self.on_release)
        self.mpl_connect('motion_notify_event', self.on_drag)
        self.mpl_connect('pick_event', self.on_pick)

    def render_plot(self):
        self.ax.clear()
        self.ax.set_xlabel('Time (ms)')
        self.ax.set_ylabel('Channels')

        # Get unique channels and sort them
        channels = sorted(set(event.channel for event in self.stim_data_manager.get_sorted_events()))
        channel_mapping = {channel: idx for idx, channel in enumerate(channels)}
        max_time = self.stim_data_manager.get_time_range()[1]

        for event in self.stim_data_manager.get_sorted_events():
            mapped_channel = channel_mapping[event.channel]
            rect = Rectangle((event.start_time,
                              mapped_channel - 0.4),
                              event.duration,
                              0.8,
                              edgecolor='black',
                              facecolor='blue' if event.amplitude > 0 else 'red',
                              )
            self.ax.add_patch(rect)

        # Set y-axis with sequential positions and map labels to the actual channel numbers
        self.ax.set_yticks(range(len(channels)))
        self.ax.set_yticklabels(channels)
        self.ax.set_xlim(0, max_time)
        self.ax.set_ylim(-0.5, len(channels) - 0.5)
        self.draw()


    def on_click(self, event):
        if event.inaxes is not self.ax:
            return

        for rect in self.ax.patches:
            contains, _ = rect.contains(event)
            if contains:
                self.selected_patch = rect
                break

    def on_drag(self, event):
        if self.selected_patch and event.inaxes is self.ax:
            dx = event.xdata - self.selected_patch.get_x()
            self.selected_patch.set_width(dx)
            self.draw()

    def on_release(self, event):
        if self.selected_patch:
            # Update the corresponding StimEvent
            self.selected_patch = None
            self.recalculate_events()

    def on_pick(self, event):
        artist = event.artist
        if isinstance(artist, Rectangle):
            # Logic for double-click and opening a dialog to edit the StimEvent
            pass

    def recalculate_events(self):
        # Logic to recalculate the timeline based on new durations
        self.stim_data_manager.recalculate_timeline()
        self.render_plot()

class MainWindow(QMainWindow):
    def __init__(self, stim_data_manager):
        super().__init__()
        self.setWindowTitle('Stim Event Plotter')

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.plotter = BarGraphPlotter(stim_data_manager)
        layout.addWidget(self.plotter)

        self.setGeometry(100, 100, 800, 600)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Initialize StimDataManager and load CSV data
    stim_data_manager = StimDataManager()
    stim_data_manager.load_from_csv('test.csv')

    window = MainWindow(stim_data_manager)
    window.show()

    sys.exit(app.exec())



# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.patches import Rectangle
# from PySide6.QtWidgets import QWidget, QVBoxLayout, QMainWindow
# from PySide6.QtCore import Qt
# import numpy as np
# from stim_data_manager import StimEvent

# class StimTrainPlotter(QMainWindow):
#     def __init__(self, stim_data_manager):
#         super().__init__()
#         self.stim_data_manager = stim_data_manager
#         self.setup_ui()
#         self.setup_plot()
#         self.plot_data()
#         self.show()

#     def setup_ui(self):
#         layout = QVBoxLayout()
#         self.canvas = FigureCanvas(plt.Figure(figsize=(10, 6)))
#         layout.addWidget(self.canvas)
#         self.setLayout(layout)

#     def setup_plot(self):
#         self.fig = self.canvas.figure
#         self.ax = self.fig.add_subplot(111)
#         self.ax.set_xlabel('Time (ms)')
#         self.ax.set_ylabel('Channel')
#         self.fig.tight_layout()

#         self.canvas.mpl_connect('button_press_event', self.on_click)
#         self.canvas.mpl_connect('motion_notify_event', self.on_motion)
#         self.canvas.mpl_connect('button_release_event', self.on_release)

#     def plot_data(self):
#         self.ax.clear()
#         events = self.stim_data_manager.get_sorted_events()
#         channels = sorted(set(event.channel for event in events))
#         channel_map = {ch: i for i, ch in enumerate(channels)}

#         for event in events:
#             y = channel_map[event.channel]
#             color = 'blue' if event.amplitude > 0 or event.frequency > 0 else 'gray'
#             rect = Rectangle((event.start_time, y - 0.4), event.duration, 0.8, 
#                              facecolor=color, edgecolor='black', alpha=0.7)
#             self.ax.add_patch(rect)
#             rect.set_picker(5)  # Enable picking for the rectangle

#         self.ax.set_ylim(-0.5, len(channels) - 0.5)
#         self.ax.set_yticks(range(len(channels)))
#         self.ax.set_yticklabels(channels)
        
#         time_range = self.stim_data_manager.get_time_range()
#         if time_range:
#             self.ax.set_xlim(0, time_range[1])

#         self.fig.canvas.draw()
#         self.fig.canvas.show()

#     def on_click(self, event):
#         if event.button == 1:  # Left click
#             self.drag_start = (event.xdata, event.ydata)
#             self.drag_rect = None
#         elif event.button == 3:  # Right click
#             self.show_context_menu(event)

#     def on_motion(self, event):
#         if event.button == 1 and self.drag_start:
#             if self.drag_rect:
#                 self.drag_rect.remove()
#             x0, y0 = self.drag_start
#             width = event.xdata - x0
#             self.drag_rect = Rectangle((x0, y0 - 0.4), width, 0.8, 
#                                        facecolor='gray', edgecolor='black', alpha=0.5)
#             self.ax.add_patch(self.drag_rect)
#             self.fig.canvas.draw()

#     def on_release(self, event):
#         if event.button == 1 and self.drag_start:
#             x0, y0 = self.drag_start
#             channel = int(round(y0))
#             duration = event.xdata - x0
#             if duration > 0:
#                 new_event = StimEvent(channel, 0, 0, duration, x0)
#                 self.stim_data_manager.add_event(new_event)
#                 self.plot_data()
#             self.drag_start = None
#             if self.drag_rect:
#                 self.drag_rect.remove()
#                 self.drag_rect = None

#     def show_context_menu(self, event):
#         # Implement context menu for adding/deleting events
#         pass

#     def update_plot(self):
#         self.plot_data()
