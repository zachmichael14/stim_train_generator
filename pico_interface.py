import serial
import time
import struct

# Serial communication settings
SERIAL_PORT = 'COM8'  # Update with the actual port
BAUD_RATE = 115200
TIMEOUT = 1  # Timeout for serial operations in seconds

# Command Definitions
CMD_SET_AMPLITUDE = 0x01
CMD_SET_FREQUENCY = 0x02
CMD_SET_CHANNEL = 0x03


class MicrocontrollerInterface:
    def __init__(self, port: str, baud_rate: int):
        self.serial = serial.Serial(port, baud_rate, timeout=TIMEOUT)

    def send_command_set(self, amplitude, frequency, duration, channel):
        command_set = struct.pack('<fIIB', amplitude, frequency, duration, channel)
        self.ser.write(command_set)
        response = self.ser.readline()
        print(f"Microcontroller response: {response.decode().strip()}")
    
    def send_command(self, channel, amplitude, frequency, duration):
        # Convert amplitude to a value between 0 and 1023
        amplitude_value = int(amplitude / 1000 * 1023)
        frequency_value = int(frequency)
        duration_value = int(duration)
        
        # Pack the command with channel, amplitude, frequency, duration
        command_packet = struct.pack('<BHHH', channel, amplitude_value, frequency_value, duration_value)
        
        # Send the packet to the microcontroller
        self.serial.write(command_packet)
        
        # Receive and print response (for verification)
        response = self.receive_response()
        if response:
            print(f"Response: {response}")

    def receive_response(self) -> bytes:
        response = self.serial.read_until(size=2)  # Read until at least 2 bytes (command and success flag)
        if len(response) < 2:
            return b''  # Incomplete response or timeout
        payload_length = response[0] - 2
        payload = self.serial.read(payload_length)
        return response + payload

    def set_amplitude(self, amplitude: float) -> None:
        # Map the amplitude value (0 to 1000 mA) to the 0 to 1023 analog range
        voltage = int(amplitude / 1000 * 1023)  # Assuming 1000 mA maps to 1023
        print(voltage)
        payload = self.int_to_bytes(voltage, 2)
        print(payload)
        self.send_command(CMD_SET_AMPLITUDE, payload)
        response = self.receive_response()
        if response:
            print(f"Amplitude set response: {response}")

    
    @staticmethod
    def int_to_bytes(value: int, length: int) -> bytes:
        """
        Convert an integer to a byte representation with a specified length.
        Assumes that value fits within the specified number of bytes.
    
        :param value: The integer value to convert
        :param length: Number of bytes in the result
        :return: Byte representation of the integer
        """
        return value.to_bytes(length, byteorder='big')
    
    def set_channel(self, channel: int) -> None:
        """
        Set the channel on the microcontroller.

        :param channel: The channel number to set
        """
        payload = bytes([channel])
        self.send_command(CMD_SET_CHANNEL, payload)
        
        response = self.receive_response()
        if response:
            print(f"Channel set response: {response}")

    def set_frequency(self, frequency: int, duration: int) -> None:
        """
        Set the frequency and duration on the microcontroller.

        :param frequency: The frequency to set (needs to fit within the byte length)
        :param duration: The duration to set (needs to fit within the byte length)
        """
        # Convert frequency and duration to bytes
        frequency_bytes = self.int_to_bytes(frequency, 2)  # 2 bytes for frequency
        duration_bytes = self.int_to_bytes(duration, 2)    # 2 bytes for duration
        
        # Construct the payload
        payload = frequency_bytes + duration_bytes
        self.send_command(CMD_SET_FREQUENCY, payload)
        
        # Receive and print the response
        response = self.receive_response()
        if response:
            print(f"Frequency set response: {response}")


        def set_channel(self, channel: int) -> None:
            payload = bytes([channel])
            self.send_command(CMD_SET_CHANNEL, payload)
            response = self.receive_response()
            if response:
                print(f"Channel set response: {response}")

def main():
    mcu = MicrocontrollerInterface(SERIAL_PORT, BAUD_RATE)
    
    while True:
        # mcu.set_channel(2)  # Set channel to 2

        mcu.set_amplitude(25)  # Set amplitude to 3 units

        time.sleep(1)
        mcu.set_amplitude(0)  # Set frequency to 1000 Hz for 200 ms
    time.sleep(1)
    
    mcu.serial.close()

if __name__ == "__main__":
    main()



# import serial
# import struct
# import time
# from daq import DAQ
# """
# Packet structure:

# Start byte (1 byte)
# Command ID (1 byte)
# Parameter flags (1 byte)
# Channel (1 byte, if flag set)
# Amplitude (2 bytes, if flag set)
# Frequency (4 bytes, if flag set)
# Checksum (1 byte)
# End byte (1 byte)

# The parameter flags byte will indicate which parameters are included in the packet:

# Bit 0: Channel
# Bit 1: Amplitude
# Bit 2: Frequency
# """

# class PicoInterface:
#     START_BYTE = 0xAA
#     END_BYTE = 0x55
#     CMD_SET_PARAMS = 0x01

#     def __init__(self, port, baudrate=115200, timeout=1):
#         self.ser = serial.Serial(port, baudrate, timeout=timeout)
#         time.sleep(2)  # Wait for Pico to initialize

#     def _send_command(self, channel=None, amplitude=None, frequency=None):
#         flags = 0
#         data = bytearray([self.START_BYTE, self.CMD_SET_PARAMS, 0])  # 0 is a placeholder for flags

#         if channel is not None:
#             flags |= 1
#             data.extend(struct.pack('B', channel))
#         if amplitude is not None:
#             flags |= 2
#             data.extend(struct.pack('<H', amplitude))
#         if frequency is not None:
#             flags |= 4
#             data.extend(struct.pack('<f', frequency))

#         data[2] = flags  # Update flags in the packet
    
#         # Calculate checksum (simple XOR of all bytes including START_BYTE and excluding END_BYTE)
#         checksum = 0
#         for byte in data:
#             checksum ^= byte
    
#         data.extend([checksum, self.END_BYTE])
    
#         print(f"Sending packet: {' '.join([f'{b:02X}' for b in data])}")
    
#         # Send the packet
#         self.ser.write(data)
    
#         # Wait for acknowledgment
#         ack = self.ser.read(1)
#         print(f"Received acknowledgment: {ack.hex() if ack else 'None'}")
#         if ack != b'\x06':  # ACK byte
#             raise Exception("Command not acknowledged")

#     def set_params(self, channel=None, amplitude=None, frequency=None):
#         self._send_command(channel, amplitude, frequency)

#     def close(self):
#         self.ser.close()

# # In the main part:
# if __name__ == "__main__":
#     pico = PicoInterface('COM7')  # Adjust port as needed
#     daq = DAQ()

#     try:
#         # print("Setting channel only:")
#         # pico.set_params(channel=5)
#         print("Setting amplitude only:")
#         # while True:
#         pico.set_params(amplitude=0)
#         # print("Setting frequency only:")
#         # pico.set_params(frequency=1000.0)
#         # print("Setting all params:")
#         # pico.set_params(amplitude=50, frequency=1000.0)
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         pico.close()