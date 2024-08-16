import serial
import time
from typing import List
from dataclasses import dataclass
import csv


class MicrocontrollerInterface:
    # Serial communication settings
    SERIAL_PORT = 'COM7'  # Update with the actual port
    BAUD_RATE = 115200
    TIMEOUT = 1  # Timeout for serial operations in seconds

    # Command Definitions
    CMD_SET_AMPLITUDE = 0x01
    CMD_SET_FREQUENCY = 0x02
    CMD_SET_CHANNEL = 0x03
    CMD_START_EXECUTION = 0x04

    def __init__(self, port: str = SERIAL_PORT, baud_rate: int = BAUD_RATE):
        self.serial = serial.Serial(port, baud_rate, timeout=self.TIMEOUT)

    def send_command(self, command: int, payload: bytes) -> None:
        packet = bytes([len(payload) + 1, command]) + payload  # Changed from +2 to +1
        self.serial.write(packet)
        time.sleep(0.01)

    def receive_response(self) -> bytes:
        response = self.serial.read(2)  # Read 2 bytes (command and success flag)
        if len(response) < 2:
            return b''  # Incomplete response or timeout
        payload_length = response[0] - 2
        payload = self.serial.read(payload_length)
        return response + payload

    def set_amplitude(self, amplitude: float) -> None:
        value = int(amplitude)  # Assuming amplitude is already in the 0-1000 range
        payload = self.int_to_bytes(value, 2)
        self.send_command(self.CMD_SET_AMPLITUDE, payload)
        response = self.receive_response()
        if response:
            print(f"Amplitude set response: {response}")

    @staticmethod
    def int_to_bytes(value: int, length: int) -> bytes:
        return value.to_bytes(length, byteorder='big')

    def set_channel(self, channel: int) -> None:
        payload = bytes([channel])
        self.send_command(self.CMD_SET_CHANNEL, payload)
        response = self.receive_response()
        if response:
            print(f"Channel set response: {response}")

    def set_frequency(self, frequency: int, duration: int) -> None:
        frequency_bytes = self.int_to_bytes(frequency, 4)  # 4 bytes for frequency
        duration_bytes = self.int_to_bytes(duration, 4)    # 4 bytes for duration
        payload = frequency_bytes + duration_bytes
        self.send_command(self.CMD_SET_FREQUENCY, payload)
        response = self.receive_response()
        if response:
            print(f"Frequency set response: {response}")

    def start_execution(self):
        self.send_command(self.CMD_START_EXECUTION, b'')
        response = self.receive_response()
        if response:
            print(f"Start execution response: {response}")

class StimExecutor:
    def __init__(self, data_manager: StimDataManager, interface: MicrocontrollerInterface):
        self.data_manager = data_manager
        self.interface = interface

    def send_batch_commands(self):
        events = self.data_manager.get_sorted_events()
        for event in events:
            print(f"Sending event: Channel {event.channel}, Amplitude {event.amplitude}, Frequency {event.frequency}, Duration {event.duration} ms")
            
            self.interface.set_channel(event.channel)
            input("Press Enter after observing channel set...")
            
            self.interface.set_amplitude(event.amplitude)
            input("Press Enter after observing amplitude set...")
            
            self.interface.set_frequency(int(event.frequency), int(event.duration))
            
            # Convert milliseconds to seconds for the sleep duration
            sleep_duration = event.duration / 1000.0
            print(f"Waiting for {sleep_duration:.2f} seconds...")
            time.sleep(sleep_duration)
            
            input("Press Enter after observing the burst...")
    
        print("Starting execution")
        self.interface.start_execution()

if __name__ == "__main__":
    data_manager = StimDataManager()
    data_manager.load_from_csv("test_files/input/daq_test_input.csv")

    interface = MicrocontrollerInterface()
    executor = StimExecutor(data_manager, interface)
    executor.send_batch_commands()
