
from network.QueryProcessing.networkqueryparser import *
from network.QueryProcessing.networkqueryformatter import *

from collections import deque

class User:

    def __init__(self):
        self.communicator = None
        self.query_queue = deque()

        self.team = 1
        self.connected = False
