#!/usr/bin/env python3

import socket
import struct
import numpy as np

class EclypseZ7Source:
    '''Eclypse Z7 Source'''

    rates = {24000: 0, 48000: 1, 96000: 2, 192000: 3, 384000: 4, 768000: 5, 1536000: 6}

    def __init__(self, addr, port, freq, rate, corr):
        self.addr = addr
        self.port = port
        self.ctrl_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the control and data sockets
        self.ctrl_sock.connect((addr, port))
        self.ctrl_sock.send(struct.pack('<I', 0))  # Initialize control connection

        self.data_sock.connect((addr, port))
        self.data_sock.send(struct.pack('<I', 1))  # Initialize data connection

        # Set frequency and rate
        self.set_freq(freq, corr)
        self.set_rate(rate)

        # Start receiving and writing data to a file
        self.write_received_data_to_file()

    def set_freq(self, freq, corr):
        self.ctrl_sock.send(struct.pack('<I', 0 << 28 | int((1.0 + 1e-6 * corr) * freq)))

    def set_rate(self, rate):
        if rate in EclypseZ7Source.rates:
            code = EclypseZ7Source.rates[rate]
            self.ctrl_sock.send(struct.pack('<I', 1 << 28 | code))
        else:
            raise ValueError("Acceptable sample rates are 24k, 48k, 96k, 192k, 384k, 768k, 1536k")

    def write_received_data_to_file(self):
        '''Receive data from the data socket and write to a file.'''
        try:
            with open("received_data.bin", "wb") as bin_file, open("received_data_hex.txt", "w") as hex_file:
                print("Starting data reception...")
                while True:
                    # Receive data from the socket
                    data = self.data_sock.recv(16384)  # Adjust buffer size as needed
                    if data:
                        print(f"Received {len(data)} bytes of data.")
                        bin_file.write(data)  # Write raw binary data to file

                        # Process data into complex IQ format
                        num_samples = len(data) // 8  # Each complex sample is 8 bytes (4 bytes for real + 4 bytes for imaginary)
                        fmt = f'<{num_samples}ff'  # Format string for struct.unpack
                        iq_data = struct.unpack(fmt, data)
                        complex_data = np.array(iq_data).reshape(-1, 2)  # Reshape into pairs of (real, imag)
                        complex_samples = complex_data[:, 0] + 1j * complex_data[:, 1]

                        # Debug output for first few samples
                        print(f"First 5 complex samples: {complex_samples[:5]}")

                        # Write hex representation to hex file
                        hex_view = data.hex()  # Convert the binary data to hexadecimal representation
                        hex_file.write(f"{hex_view}\n")  # Write the hex view to the text file
                    else:
                        print("No more data received.")
                        break
        except Exception as e:
            print(f"Error receiving data: {e}")
        finally:
            print("Closing sockets...")
            self.data_sock.close()
            self.ctrl_sock.close()

if __name__ == "__main__":
    # Replace these parameters with your device-specific configuration
    addr = "192.168.178.64"  # Device IP address
    port = 1001  # Device port number
    freq = 1420405000  # Frequency in Hz (example: 1.420405 GHz)
    rate = 768000  # Sample rate
    corr = 0  # Frequency correction in ppm

    # Create an instance of the EclypseZ7Source and start writing data to a file
    eclypse_source = EclypseZ7Source(addr, port, freq, rate, corr)
