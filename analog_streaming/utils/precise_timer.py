import time

class PreciseTimer:
    @staticmethod
    def sleep(duration: float) -> None:
        end_time = time.perf_counter() + duration
        while time.perf_counter() < end_time:
            remaining = end_time - time.perf_counter()
            if remaining > 0.001:
                time.sleep(0.0005)
