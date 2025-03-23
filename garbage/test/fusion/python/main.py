from CythonCommunicator import *
from global_vars import *
import select
import sys
import os
import time

def main():
    # Set stdin to non-blocking mode (on Unix-like systems)
    import fcntl
    fl = fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL)
    fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, fl | os.O_NONBLOCK)
    
    comm = CythonCommunicator(python_port=PYTHON_PORT, c_port=C_PORT)
    print("[+] Starting communication loop (Press Ctrl+C to exit)")
    print("Enter a message to send (anytime): ", end='', flush=True)
    
    buffer = ""
    
    try:
        while True:
            # Check for incoming messages
            comm.receive_message()
            
            # Check for user input (non-blocking)
            try:
                if select.select([sys.stdin], [], [], 0)[0]:
                    try:
                        input_data = sys.stdin.readline()
                        if input_data:
                            input_data = input_data.strip()
                            if input_data:
                                comm.send_message(input_data)
                                print("Enter a message to send: ", end='', flush=True)
                    except (IOError, TypeError):
                        pass
            except (IOError, TypeError):
                pass
            
            # Small delay to reduce CPU usage
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\n[+] Exiting...")
    
    finally:
        comm.cleanup()

if __name__ == "__main__":
    main()