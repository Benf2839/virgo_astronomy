import socket
import virgo
import numpy as np
import struct
import time

# Define TCP/IP connection parameters
TCP_IP = '73.117.151.70'
TCP_PORT = 1001
BUFFER_SIZE = 4096  # Adjust the buffer size based on expected data

# Define observation parameters for virgo
obs = {
    'dev_args': '',
    'rf_gain': 30,
    'if_gain': 25,
    'bb_gain': 18,
    'frequency': 1420e6,
    'bandwidth': 2.4e6,
    'channels': 2048,
    't_sample': 1,
    'duration': 60,  # Duration of observation in seconds
    'loc': '',
    'ra_dec': '',
    'az_alt': ''
}

# Connect to the custom TCP/IP data stream
def receive_data():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((TCP_IP, TCP_PORT))
            print(f"Connected to {TCP_IP}:{TCP_PORT}")
            
            data_buffer = b''
            while True:
                # Receive data from the stream
                data = sock.recv(BUFFER_SIZE)
                if not data:
                    print("Connection closed by the server.")
                    break
                data_buffer += data

                # Assume the data is being streamed in a float format and unpack it
                float_data = struct.unpack(f'{len(data_buffer) // 4}f', data_buffer)
                np_data = np.array(float_data)

                # Process the received data using Virgo
                process_observation(np_data)

                # Clear the buffer for the next data batch
                data_buffer = b''

        except socket.error as e:
            print(f"Socket error: {e}")
        except KeyboardInterrupt:
            print("Interrupted by user.")

# Process the received observation data using Virgo
def process_observation(data):
    # Save the raw data into a temporary file (optional)
    temp_obs_file = 'temp_observation.dat'
    with open(temp_obs_file, 'wb') as f:
        f.write(data.tobytes())

    # Perform the observation and analysis using virgo
    virgo.observe(obs_parameters=obs, obs_file=temp_obs_file)

    # Plot and analyze the data (for hydrogen line at 1420.4057517667 MHz)
    virgo.plot(obs_parameters=obs, n=20, m=35, f_rest=1420.4057517667e6,
               vlsr=False, meta=False, avg_ylim=(-5, 15), cal_ylim=(-20, 260),
               obs_file=temp_obs_file, rfi=[(1419.2e6, 1419.3e6), (1420.8e6, 1420.9e6)],
               dB=True, spectra_csv='spectrum.csv', plot_file='plot.png')
    print("Observation complete, plot saved as plot.png and data exported to spectrum.csv")

if __name__ == "__main__":
    # Start the data stream and observation process
    receive_data()
