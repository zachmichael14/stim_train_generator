import time
from typing import List

import nidaqmx

class DAQ:
    """
    A class supporting a National Instruments Data Acquisition (NI-DAQ/DAQ) device.
    
    This class focuses on allowing the DAQ to control a DS8R stimulator.
    """

    VOLT_TO_AMP_CONVERSION = 10 / 1000 # DS8R's conversion factor
    AMP_OFFSET = 0.015 # Added to amplitude to minimize DS8R's variability

    # Cached for faster lookup
    PICO_LOOKUP = {
        0: [False, False, False, False],
        1: [False, False, False, True],
        2: [False, False, True, False],
        3: [False, False, True, True],
        4: [False, True, False, False],
        5: [False, True, False, True],
        6: [False, True, True, False],
        7: [False, True, True, True],
        8: [True, False, False, False],
        9: [True, False, False, True],
        10: [True, False, True, False],
        11: [True, True, True, True],
    }

   
    def __init__(self,
                 pico_port: int = 1,
                 switcher_port: int = 0,
                 trigger_port: int = 2,
                 amplitude_port: int = 0,
                 ) -> None:
        """
        Initialize the DAQ object with specified ports, where a port corresponds to set of physical pin inputs/outputs on the DAQ rather
        than to a PC's TCP/IP port.

        Ports can have one or more channels, where a channel represents the physical location of a single pin within a port.

        Args:
            pico_port (int): Pico connection port, defaults to 1
            switcher_port (int): Channel switcher port, defaults to 0
            trigger_port (int): Trigger channel port, defaults to 1
            amplitude_port (int): Amplitude control port, defaults to 0
        """
        # Get the name of the first available DAQ device
        # This may be erroneous if >1 device is connected
        # It would be better to get device name in the code the inits
        # the instance using a static method, then pass the name of the 
        # device as an init argument
        self.device_name: str = self.get_devices()[0].name

        self.tasks: List[nidaqmx.Task] = []

        # Used for setting DS8R's amplitude (DAQ's analog output)
        self.amplitude_channel: nidaqmx.Task = self._create_task()
        self.amplitude_channel.ao_channels.add_ao_voltage_chan(f"{self.device_name}/ao{amplitude_port}")

        # For sending trigger singal to DS8R (DAQ's digital output)
        self.trigger_channel: nidaqmx.Task = self._create_task()
        self._add_digital_out_channels(self.trigger_channel, trigger_port, 1)
      
        # For specifying D188 channel (DAQ's digital output)
        self.switcher_channels: nidaqmx.Task = self._create_task()
        self._add_digital_out_channels(self.switcher_channels, switcher_port, 8)

        # For high frequency triggering via the Pico (DAQ's digital output)
        self.pico_channels: nidaqmx.Task = self._create_task()
        self._add_digital_out_channels(self.pico_channels, pico_port, 4)

        # Zero any previously stored values on the DAQ/Pico
        self.zero_all()

    def __del__(self) -> None:
        """
        Destructor to clean up resources when the DAQ object is garbage collected.

        Prevents DaqResourceWarning by closing tasks before their deletion.
        """
        if hasattr(self, "tasks"):
            for task in self.tasks:
                task.close()
        self.tasks = []

    def _create_task(self) -> nidaqmx.Task:
        """
        Create a new NI-DAQ task and add it to the tasks list.
        
        A task is essentially a way to interact with a port on the DAQ.
        The tasks list is used by __del__ for closing tasks before garbage collection.

        Return: 
            nidaqmx.Task: Newly created nidaqmx.Task object
        """
        task = nidaqmx.Task()
        self.tasks.append(task)
        return task

    def _add_digital_out_channels(self,
                                 task: nidaqmx.Task,
                                 port: int,
                                 channel_quantity: int,
                                 ) -> None:
        """
        Add digital output channels to the specified task.
        A channel is individual pin within a port.

        Args:
            task (nidaqmx.Task): The nidaqmx.Task to add channels to
            port (int): The port number to use
            channel_quantity (int): The number of channels to add
            
        """
        for i in range(channel_quantity):
            task.do_channels.add_do_chan(f"{self.device_name}/port{port}/line{i}")        

    def set_amplitude(self, amplitude: float) -> None:
        """
        TODO: Implement conversion factor if DS8R settings change.
        Set the DS8R's amplitude by writing a value to the DAQ analog output pin that corresponds to the DS8R's "Control" input. 
        
        This method alone does not trigger stimulation; it must be called with a nonzero value before calling a trigger method.
        
        This method assumes the DS8R's conversion factor is 10 V = 1000 mA.
        
        Args:
            amplitude: Desired amplitude in mA
        """
    
        if amplitude == 0: 
            # Write true zero (i.e., no offset)
            self.amplitude_channel.write(0) 
        else: 
            # Adding an offset helps counter DS8R variability when
            # using 10V = 1000mA conversion factor
            self.amplitude_channel.write((amplitude * self.VOLT_TO_AMP_CONVERSION) + self.AMP_OFFSET)
 
    def set_channel(self, channel: int) -> None:
        """
        Turn on a specific D188 (channel switcher) channel.
        Passing 0 as an argument turns off all channels.

        This methods writes a HIGH value (i.e., `True`) to the DAQ
        output pin corresponding to the desired D188 channel. The D188 is
        incapable of selecting more than 1 channel simultaneously, however.
        This means that a HIGH value written to >1 pin is rejected by the
        D188, which will instead write LOW values to all pins, turning them
        all off.

        Args:
            channel (int): The channel number to turn on
                - channel == 0 turns off all channels
        """
        # Pins are reversed, hence the backwards iteration
        self.switcher_channels.write([channel == i for i in range(8, 0, -1)])

    def trigger(self) -> None:
        """
        Simplest possible trigger method.
        For stimulation to be delivered, a nonzero amplitude must be set before
        calling this method.

        When the trigger is configured using a software timer, the max
        frequency is ~500 Hz before the timer introduces too much jitter to be
        reliable.
        """
        self.trigger_channel.write(True)
        self.trigger_channel.write(False)

    def set_pulse_with_pico(self, pulses: int) -> None:
        """
        This method contains a 100ms sleep that seems unrelated to frequency.
        It instead seems to serve as a buffer to the sampling rate of the Pico.
        Its effect is that the Pico only sends the trigger signal once.        
        """
        self.pico_channels.write(self.PICO_LOOKUP[pulses])
        time.sleep(0.1)
        self.pico_channels.write(self.PICO_LOOKUP[0])

    def zero_all(self) -> None:
        """Reset all DAQ and Pico outputs to zero."""
        self.set_amplitude(0)
        self.set_channel(0)
        self.set_pulse_with_pico(0)

    @staticmethod
    def get_devices() -> List[nidaqmx.system.device.Device]:
        """
        Get a list of available NI-DAQ devices on the system.

        Returns: 
            list (nidaqmx.system.device.Device): List of all of NI-DAQ devices
            found on the system.
        """
        system = nidaqmx.system.System.local()
        
        ## Wait for DAQ to be detected
        if not system.devices:
            print("Cannot find DAQ device(s). Check USB connections.")
            print("Waiting for connection...")
            print("Ctrl + C to quit")

            while not system.devices:
                pass

            print("Device found! Kept you waiting, huh?")
            time.sleep(1) # Add delay to allow time to read new connection
        return system.devices

    @staticmethod
    def print_devices_and_channels() -> None:
        """Print names and channels for each device found on the system."""
        system = nidaqmx.system.System.local()
        for device in system.devices:
            print(f"Device: {device.name}")
            print("All Available Channels:")
            print(f"\tAI Channels: {[chan.name for chan in device.ai_physical_chans]}")
            print(f"\tAO Channels: {[chan.name for chan in device.ao_physical_chans]}")
            print(f"\tDI Channels: {[chan.name for chan in device.di_lines]}")
            print(f"\tDO Channels: {[chan.name for chan in device.do_lines]}")
            print(f"\tCI Channels: {[chan.name for chan in device.ci_physical_chans]}")
            print(f"\tCO Channels: {[chan.name for chan in device.co_physical_chans]}")
