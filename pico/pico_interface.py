import serial
import struct
import time
from typing import Type

class PicoInterface:
    """
    TODO: Implement method to find port
    TODO: Don't exclude end byte from checksum

    Packet structure:
        - Start byte (1 byte): Indicates start of packet
        - Command ID (1 byte): What is the Pico told to do
        - Parameter flags (1 byte): What parameters are being set, if any
            - Channel (1 byte): turn on channel if bit 0 of parameter flags is set
            - Amplitude (2 bytes): set amplitude if bit 1 of parameter flags is set
            - Frequency (4 bytes): set frequency if bit 2 of parameter flags is set
        - Checksum (1 byte): Sum of packet bits, excluding itself and end byte
        - End byte (1 byte): Indicates end of packet
    """
    START_BYTE = 0xAA
    END_BYTE = 0x55
    CMD_SET_PARAMS = 0x01

    def __init__(self, port, baudrate=115200, timeout=1):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)  # Wait for Pico to initialize

    def set_params(self, channel=None, amplitude=None, frequency=None):
        data = self._build_packet(channel, amplitude, frequency)
        self._send_command(data)

    def _send_command(self, data: Type[bytearray]) -> None:
        """
        Send command packet to Pico.
        """   
        print(f"Sending packet: {' '.join([f'{b:02X}' for b in data])}")
    
        # Send the packet
        self.ser.write(data)
    
        # Wait for acknowledgment
        ack = self.ser.read(1)
        print(f"Received acknowledgment: {ack.hex() if ack else 'None'}")
        if ack != b'\x06':  # ACK byte
            raise Exception("Command not acknowledged")

    def _build_packet(self,
                      channel: int = None,
                      amplitude: float = None,
                      frequency: float = None,
                      ) -> Type[bytearray]:
        """
        Currently, the Pico doesn't handle amplitude appropriately in part
        because the +3.3V output capability falls short of the DS8R's expected
        +10V input range. As such, the amplitude output of the Pico needs to
        be amplified.

        While it's possible for the DAQ to amplify that signal, the Pico's
        output isn't very smooth/stable without an additional filter.
        """
        flags = 0
        data = bytearray([self.START_BYTE, self.CMD_SET_PARAMS, flags])

        if channel is not None:
            flags |= 1
            data.extend(struct.pack('B', channel))
        if amplitude is not None:
            flags |= 2
            data.extend(struct.pack('<H', amplitude))
        if frequency is not None:
            flags |= 4
            data.extend(struct.pack('<f', frequency))
        data[2] = flags  # Update flags in the packet
    
        checksum = self._generate_checksum(data)
        data.extend([checksum, self.END_BYTE])
        return data
    
    def _generate_checksum(self, data: Type[bytearray]) -> int:
        """
        Calculate simple XOR of all bytes.
        """
        checksum = 0
        for byte in data:
            checksum ^= byte
        return checksum   

    def close(self):
        self.ser.close()
