#!/usr/bin/env python3

import socket
import struct
import numpy as np
import Virgo  # Make sure to install astro-virgo library

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

        # Start receiving and processing data
        self.process_received_data()

    def set_freq(self, freq, corr):
        self.ctrl_sock.send(struct.pack('<I', 0 << 28 | int((1.0 + 1e-6 * corr) * freq)))

    def set_rate(self, rate):
        if rate in EclypseZ7Source.rates:
            code = EclypseZ7Source.rates[rate]
            self.ctrl_sock.send(struct.pack('<I', 1 << 28 | code))
        else:
            raise ValueError("Acceptable sample rates are 24k, 48k, 96k, 192k, 384k, 768k, 1536k")

    def process_received_data(self):
        '''Receive data from the data socket and process it.'''
        try:
            print("Starting data reception...")
            while True:
                # Receive data from the socket
                data = self.data_sock.recv(16384)  # Adjust buffer size as needed
                if data:
                    print(f"Received {len(data)} bytes of data.")

                    # Process data into complex IQ format
                    num_samples = len(data) // 8  # Each complex sample is 8 bytes (4 bytes for real + 4 bytes for imaginary)
                    fmt = f'<{num_samples}ff'  # Format string for struct.unpack
                    iq_data = struct.unpack(fmt, data)
                    complex_data = np.array(iq_data).reshape(-1, 2)  # Reshape into pairs of (real, imag)
                    complex_samples = complex_data[:, 0] + 1j * complex_data[:, 1]

                    # Process the complex samples using the Virgo library
                    self.process_observation(complex_samples)
                else:
                    print("No more data received.")
                    break
        except Exception as e:
            print(f"Error receiving data: {e}")
        finally:
            print("Closing sockets...")
            self.data_sock.close()
            self.ctrl_sock.close()

    def process_observation(self, complex_samples):
        '''Process the complex samples using Virgo and display results.'''
        try:
            virgo = Virgo()  # Create an instance of the Virgo class
            result = virgo.process_observation(complex_samples)  # Process the data
            print(f"Processed Data Result: {result}")  # Display the result
        except Exception as e:
            print(f"Error processing observation: {e}")

if __name__ == "__main__":
    # Replace these parameters with your device-specific configuration
    addr = "192.168.178.64"  # Device IP address
    port = 1001  # Device port number
    freq = 1420405000  # Frequency in Hz (example: 1.420405 GHz)
    rate = 768000  # Sample rate
    corr = 0  # Frequency correction in ppm

    # Create an instance of the EclypseZ7Source and start processing data
    eclypse_source = EclypseZ7Source(addr, port, freq, rate, corr)
