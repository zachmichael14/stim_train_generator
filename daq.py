import time
from typing import List, Optional

import nidaqmx
import numpy as np

class DAQ:
    """
    A class supporting National Instruments Data Acquisition (NI-DAQ) device operations.
    """

    def __init__(self,
                 pico_port: int = 1,
                 switcher_port: int = 0,
                 trigger_port: int = 1,
                 amplitude_port: int = 0):
        """
        Initialize the DAQ object with specified ports.

        Args:
            pico_port (int): Pico connection port, defaults to 1
            switcher_port (int): Channel switcher port, defaults to 0
            trigger_port (int): Trigger channel port, defaults to 1
            amplitude_port (int): Amplitude control port, defaults to 0
        """

        # Store all created tasks for cleanup
        self.tasks: List[nidaqmx.Task] = []

        # Get the name of the first available DAQ device
        # This may be erroneous if >1 device is connected
        self.device_name: str = self.get_devices()[0].name

        # Initialize amplitude channel (analog output)
        self.amplitude_channel: nidaqmx.Task = self.create_task()
        self.amplitude_channel.ao_channels.add_ao_voltage_chan(f"{self.device_name}/ao{amplitude_port}")

        # Initialize trigger channel (analog output)
        # Note: Not used when DAQ is connected to Pico (Pico controls triggering)
        self.trigger_channel: nidaqmx.Task = self.create_task()
        self.trigger_channel.ao_channels.add_ao_voltage_chan(f"{self.device_name}/ao{trigger_port}")

        # Initialize channel switcher (digital output)
        self.switcher_channels: nidaqmx.Task = self.create_task()
        self.add_digital_out_channels(self.switcher_channels, port=switcher_port, channel_quantity=8)

        # Initialize Pico channels (digital output)
        self.pico_channels: nidaqmx.Task = self.create_task()
        self.add_digital_out_channels(self.pico_channels, port=pico_port, channel_quantity=4)

        # Zero any previously stored values on the DAQ/Pico
        self.zero_all()

    def __del__(self):
        """
        Destructor to clean up resources when the DAQ object is garbage collected.
        """
        if hasattr(self, "tasks"):
            self.zero_all()  # Reset all outputs to safe state
            for task in self.tasks:
                task.close()
        self.tasks = []

    def create_task(self) -> nidaqmx.Task:
        """
        Create a new NI-DAQ task and add it to the tasks list.

        :return: Newly created nidaqmx.Task object
        """
        task = nidaqmx.Task()
        self.tasks.append(task)
        return task

    def add_digital_out_channels(self,
                                 task: nidaqmx.Task,
                                 port: int,
                                 channel_quantity: int):
        """
        Add digital output channels to the specified task.

        Args:
            task (nidaqmx.Task): The nidaqmx.Task to add channels to
            port (int): The port number to use
            channel_quantity (int): The number of channels to add
        """
        for i in range(channel_quantity):
            task.do_channels.add_do_chan(f"{self.device_name}/port{port}/line{i}")        

    def set_amplitude(self, amplitude: float):
        """
        Set the amplitude of the output signal.

        Args:
            amplitude: Desired amplitude in mA
        """
        # TODO: Implement conversion factor if DS8R settings change
        # Convert mA to V (assuming 100mA = 1V)
        self.amplitude_channel.write(amplitude / 100) 

    def set_switcher_channel(self, channel: int = 0, on: bool = True):
        """
        Turn on or off a specific switcher channel.
        Default channel value (0) turns all channels off as a failsafe.

        Args:
            channel (int): The channel number to toggle (0 turns off all channels)
            on (bool): True to turn the channel on, False to turn it off
        """
        switcher = self.switcher_channels

        # Each pin requires a value to be written to it
        # The channel switcher has up to 8 pins
        number_of_pins = len(switcher.channels.channel_names)

        # Default all channels to OFF (as a failsafe)
        pin_values = np.zeros(number_of_pins)

        if channel != 0:
            # Negative indexing used because pins are reversed
            # from their physical pin
            pin_values[-channel] = 1 if on else 0

        output = np.array(pin_values, dtype=bool).tolist()
        switcher.write(output)

    def send_pico_pulse(self, pulses: int, wait_time):
        # Lookup table for the binary pin out
        pulse_table = {0:[0,0,0,0],
                    1:[0,0,0,1],
                    2:[0,0,1,0],
                    3:[0,0,1,1],
                    4:[0,1,0,0],
                    5:[0,1,0,1],
                    6:[0,1,1,0],
                    7:[0,1,1,1],
                    8:[1,0,0,0],
                    9:[1,0,0,1],
                    10:[1,0,1,0],
                    11:[1,1,1,1]
                    }
        
        pin_binary = pulse_table[pulses]
        pin_binary_bool = [bool(x) for x in pin_binary]

        self.pico_channels.write(pin_binary_bool)

        time.sleep(wait_time)

        self.pico_channels.write([False,False,False,False])
    
    def send_pulse_on_channel(self,
                              amplitude: float,
                              wait_time: float = 0.1,
                              hf_pulse: int = 1,
                              channel: Optional[int] = None):
        """
        Send a pulse on the specified channel with given amplitude.

        Args:
            amplitude (float): Pulse amplitude in mA
            hf_pulse (int): Pico pulse
            channel: Channel number (optional)
        """
        print(f"Sending {amplitude} mA pulse")

        self.set_amplitude(amplitude)

        if channel is not None:
            self.set_switcher_channel(channel)
        
        self.send_pico_pulse(hf_pulse, wait_time)

        self.set_amplitude(0)
        self.send_pico_pulse(0)

    def zero_all(self):
        """
        Reset all outputs to zero.
        """
        self.set_amplitude(0)
        self.set_switcher_channel(0)
        self.send_pico_pulse(0)

    @staticmethod
    def get_devices() -> List[nidaqmx.system.device.Device]:
        """
        Get a list of available NI-DAQ devices on the system.

        :return: List of NI-DAQ devices
        """
        system = nidaqmx.system.System.local()
        return system.devices
