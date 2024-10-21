import threading

from PySide6.QtCore import QObject, Signal
from ..workers.stim_worker import StimWorker

class ContinuousStimManager(QObject):
    parameters_updated = Signal()

    def __init__(self):
        super().__init__()
        self.channel = None
        self.amplitude = 0.0
        self.frequency = 30.0
        self.worker = StimWorker()
        self.are_updates_live = False
        self._running = False
        self._lock = threading.Lock()
        self._thread = None
        self._parameters_changed = False

    def start(self):
        print("Starting Thread")
        self._running = True
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        print("Stopping Thread")
        self._running = False
        self.worker.stop()
        if self._thread and self._thread.is_alive():
            self._thread.join()
        self._thread = None
        print("Thread stopped and joined.")

    def set_parameters(self,
                       channel: int = None,
                       frequency: float = None,
                       amplitude: float = None,
                       are_updates_live: bool = None,
                       ):
        with self._lock:
            if channel is not None:
                self.channel = channel
            if frequency is not None:
                self.frequency = frequency
            if amplitude is not None:
                self.amplitude = amplitude
            if are_updates_live is not None:
                self.are_updates_live = are_updates_live

            # Setting this to True assumes params are different from previous.
            # While this method shouldn't be called unless params are actually
            # changing, this assumption could be erroneous.
            self._parameters_changed = True

        if self.are_updates_live:
            self.apply_changes()

    def apply_changes(self):
        with self._lock:
            self.worker.set_parameters(self.channel,
                                       self.frequency,
                                       self.amplitude)
            # self.parameters_updated.emit()

    def _run(self):
        while self._running:
            if not self.are_updates_live and self._parameters_changed:
                self.apply_changes()
                self._parameters_changed = False

            self.worker.run()
