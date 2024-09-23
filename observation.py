import socket
import virgo  # Assuming virgo is properly installed from the GitHub repo

# Define the IP address and port for the TCP connection
TCP_IP = '73.117.151.70'
TCP_PORT = 1001
BUFFER_SIZE = 4096  # Adjust as needed based on expected data size

def main():
    # Create a TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            # Connect to the remote device broadcasting data
            sock.connect((TCP_IP, TCP_PORT))
            print(f"Connected to {TCP_IP}:{TCP_PORT}")

            # Continuously receive data from the stream
            data_buffer = b''  # Buffer to store incoming data
            while True:
                # Receive data from the socket
                data = sock.recv(BUFFER_SIZE)
                if not data:
                    print("Connection closed by the server.")
                    break

                # Append the received data to the buffer
                data_buffer += data

                # Process the received data using the Virgo package
                # Assuming the virgo package has a method to parse or process the data
                try:
                    # This part will depend on how the virgo package works
                    # For example, it might have a method like virgo.process_observation
                    observation = virgo.process_observation(data_buffer)
                    
                    # If observation is successfully processed, do something with it
                    print(f"Processed Observation: {observation}")

                    # Clear the buffer once processed
                    data_buffer = b''

                except Exception as e:
                    print(f"Error processing data: {e}")
                    continue

        except socket.error as e:
            print(f"Socket error: {e}")
        except KeyboardInterrupt:
            print("Terminating the connection.")

if __name__ == "__main__":
    main()
