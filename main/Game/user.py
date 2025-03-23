
from Game.query_executor import *
from network.QueryProcessing.networkqueryparser import *
from network.packettransport.python.CythonCommunicator import *
# import comm here

from collections import deque
import subprocess

class User:

    def __init__(self):
        self.communicator = CythonCommunicator(python_port=PYTHON_PORT, c_port=C_PORT)
        self.query_rcv_queue = deque()
        self.query_snd_queue = deque()

        # run the c process here
        script_dir = os.path.dirname(os.path.abspath(__file__))
        communicator_path = os.path.join(script_dir, "..", "network", "packettransport", "C", "communicator")
        #process = subprocess.Popen([communicator_path])
        print(f"Started communicator from: {communicator_path}")


        self.team = 2
        self.connected = False

    def add_query(self, query, flag):

        if flag == "r":
            self.query_rcv_queue.append(query)
        elif flag == "s":
            self.query_snd_queue.append(query)


    def get_query(self, flag):

        if flag == "r":
            if len(self.query_rcv_queue) > 0:

                return self.query_rcv_queue.popleft()

        elif flag == "s":
            if len(self.query_snd_queue) > 0:

                return self.query_snd_queue.popleft()

        return None

    def handle_all_rcv_queries(self, game_map):

        current_query = None

        while ((current_query := self.get_query("r")) != None):
            QueryExecutor.handle_query(game_map, NetworkQueryParser.parse_query(current_query))

    def handle_all_snd_queries(self):

        current_query = None

        while ((current_query := self.get_query("s")) != None):
            self.communicator.send_packet(current_query)


    def update(self, dt, game_map):


        packet_rcvd, addr = self.communicator.receive_packet()
        if packet_rcvd != None:
            self.add_query(packet_rcvd, "r")

        if self.connected:
            self.handle_all_rcv_queries(game_map)

            uplayer = game_map.get_player_by_team(self.team)

            if uplayer != None:
                uplayer.think(dt, self.query_snd_queue)

        self.handle_all_snd_queries()
