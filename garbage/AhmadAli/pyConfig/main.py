from CythonCommunicator import *
from global_vars import *

import time

def main():
    comm = CythonCommunicator(python_port = PYTHON_PORT, c_port = C_PORT)
    print("[+] Starting communication loop (Press Ctrl+C to exit)")

    try:
        while True:
            comm.receive_message()
            comm.send_message("message from Python")
            time.sleep(SLEEP_TIME)
    
    except KeyboardInterrupt:
        print("\n[+] Exiting...")
    
    finally:
        comm.cleanup()

if __name__ == "__main__":
    main()
