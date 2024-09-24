#!/usr/bin/env python3

import socket
import struct
import numpy as np
import virgo  # Make sure to install astro-virgo library

# Define TCP/IP connection parameters
TCP_IP = '73.117.151.70'  # Replace with your actual IP
TCP_PORT = 1001  # Replace with your actual port
BUFFER_SIZE = 16384  # Buffer size for receiving data

# Define observation parameters for Virgo
obs = {
    'dev_args': '',
    'rf_gain': 30,
    'if_gain': 25,
    'bb_gain': 18,
    'frequency': 1420e6,
    'bandwidth': 2.4e6,
    'channels': 2048,
    't_sample': 1,
    'duration': 60,  # Observation duration in seconds
    'loc': '',
    'ra_dec': '',
    'az_alt': ''
}

class EclypseZ7Source:
    '''Eclypse Z7 Source'''

    def __init__(self, freq, rate, corr):
        self.freq = freq
        self.rate = rate
        self.corr = corr

        # Start receiving and processing data
        self.receive_data()

    def receive_data(self):
        '''Receive data from the data socket and process it.'''
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                print(f"Connecting to {TCP_IP}:{TCP_PORT}...")
                sock.connect((TCP_IP, TCP_PORT))
                print("Connection established!")

                while True:
                    # Receive data from the stream
                    data = sock.recv(BUFFER_SIZE)
                    if not data:
                        print("No data received or connection closed.")
                        break

                    # Debugging: Print the received data in hex format
                    print(f"Received raw data (hex): {data.hex()}")

                    # Unpack data as IQ samples (assuming 16-bit signed integers for I and Q)
                    num_samples = len(data) // 4  # Each sample is 4 bytes (2 bytes I + 2 bytes Q)
                    iq_data = struct.unpack(f'<{2*num_samples}h', data)

                    # Convert to complex numbers: I + jQ
                    complex_data = np.array(iq_data[0::2]) + 1j * np.array(iq_data[1::2])

                    # Debugging: Print the first few IQ samples
                    print(f"First 5 IQ samples: {complex_data[:5]}")

                    # Process the received IQ data using Virgo
                    self.process_observation(complex_data)

            except socket.error as e:
                print(f"Socket error: {e}")
            except KeyboardInterrupt:
                print("Interrupted by user.")

    def process_observation(self, data):
        '''Process the complex samples using Virgo and display results.'''
        # Debugging: Print the number of IQ samples received
        print(f"Number of IQ samples received: {len(data)}")

        # Save the raw IQ data into a temporary file for Virgo (optional)
        temp_obs_file = 'temp_observation.dat'
        with open(temp_obs_file, 'wb') as f:
            f.write(data.astype(np.complex64).tobytes())  # Save as 32-bit complex

        # Perform the observation and analysis using Virgo
        print("Running Virgo observation and plotting...")
        virgo.observe(obs_parameters=obs, obs_file=temp_obs_file)

        # Plot and analyze the data (for hydrogen line at 1420.4057517667 MHz)
        virgo.plot(obs_parameters=obs, n=20, m=35, f_rest=1420.4057517667e6,
                   vlsr=False, meta=False, avg_ylim=(-5, 15), cal_ylim=(-20, 260),
                   obs_file=temp_obs_file, rfi=[(1419.2e6, 1419.3e6), (1420.8e6, 1420.9e6)],
                   dB=True, spectra_csv='spectrum.csv', plot_file='plot.png')

        print("Observation complete, plot saved as plot.png and data exported to spectrum.csv")

if __name__ == "__main__":
    # Replace these parameters with your device-specific configuration
    freq = 1420405000  # Frequency in Hz (example: 1.420405 GHz)
    rate = 768000  # Sample rate
    corr = 0  # Frequency correction in ppm

    # Create an instance of the EclypseZ7Source and start processing data
    eclypse_source = EclypseZ7Source(freq, rate, corr)
