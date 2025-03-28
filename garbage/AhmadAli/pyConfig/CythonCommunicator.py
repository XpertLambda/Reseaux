import socket
import select
import time
from global_vars import *

class CythonCommunicator:
    def __init__(self, python_port, c_port, c_ip = DEFAULT_IP):
        """Initialize the communicator with specified ports and IP"""
        self.python_port = python_port
        self.c_port = c_port
        self.c_ip = c_ip
        self.c_addr = (c_ip, c_port)
        self.buffer_size = BUFFER_SIZE
        self.message_interval = MESSAGE_INTERVAL

        # Create and configure socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', python_port))
        self.sock.setblocking(False)

        print(f"[+] Initialized communicator (python_port: {python_port}, c_port: {c_port}, c_ip: {c_ip})")

    def send_packet(self, packet):
        """Send a message to the configured address."""
        try:
            if isinstance(packet, str):
                packet = packet.encode('utf-8')
            self.sock.sendto(packet, self.c_addr)
            print(f"[+] Sent: {packet.decode() if isinstance(packet, bytes) else packet}")
            return True
        except Exception as e:
            print(f"[-] Send failed: {str(e)}")
            return False

    def receive_packet(self):
        """Receive a message (non-blocking)."""
        try:
            ready = select.select([self.sock], [], [], 0)
            if ready[0]:
                packet, addr = self.sock.recvfrom(self.buffer_size)
                print(f"[+] Received: {packet.decode()} from {addr}")
                return packet.decode(), addr
        except Exception as e:
            if not isinstance(e, BlockingIOError):
                print(f"[-] Receive failed: {str(e)}")
        return None, None

    def cleanup(self):
        if hasattr(self, 'sock'):
            self.sock.close()
            print("[+] Communicator cleaned up")

    def __del__(self):
        self.cleanup()
