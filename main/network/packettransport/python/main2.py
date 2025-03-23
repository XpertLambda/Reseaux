from CythonCommunicator import *
from global_vars import *
import select
import sys
import os
import time
import threading

def main():
    # Set stdin to non-blocking mode (on Unix-like systems)
    import fcntl
    fl = fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL)
    fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, fl | os.O_NONBLOCK)
    
    comm = CythonCommunicator(python_port=PYTHON_PORT, c_port=C_PORT)
    print("[+] Starting communication loop (Press Ctrl+C to exit)")
    print("[+] Statistics will be printed each second")
    
    # Variables to track packet counts
    sent_packets = 0
    received_packets = 0
    last_stats_time = time.time()
    
    # Counter for packet generation
    counter = 1
    
    try:
        while True:
            current_time = time.time()
            
            # Send packets as fast as possible
            message = f"{counter} ooooooooooooooo" + ("X" * 10000)
            comm.send_packet(message)
            sent_packets += 1
            counter += 1
            
            # Check for incoming messages (non-blocking)
            if comm.receive_packet() != None:
                received_packets += 1
            
            # Check for user input (non-blocking)
            try:
                if select.select([sys.stdin], [], [], 0)[0]:
                    try:
                        input_data = sys.stdin.readline()
                        if input_data and input_data.strip():
                            # User can still input messages manually
                            comm.send_packet(input_data.strip())
                            sent_packets += 1
                    except (IOError, TypeError):
                        pass
            except (IOError, TypeError):
                pass
            
            # Print statistics every second
            if current_time - last_stats_time >= 1.0:
                print(f"[STATS] Sent: {sent_packets} packets/sec | Received: {received_packets} packets/sec")
                # Reset counters
                sent_packets = 0
                received_packets = 0
                last_stats_time = current_time
            
            # Small delay to prevent CPU from being maxed out
            time.sleep(0.02)  # Very small delay to allow more packets to be sent
            
    except KeyboardInterrupt:
        print("\n[+] Exiting...")
    finally:
        comm.cleanup()

if __name__ == "__main__":
    main()
