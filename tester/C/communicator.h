#ifndef COMMUNICATOR_H
#define COMMUNICATOR_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <netinet/in.h>
#include <time.h>
#include <sys/socket.h>

#define DISCOVERY_INTERVAL 10  // Seconds between discovery broadcasts
#define DISCOVERY_TIMEOUT 30   // Timeout for player discovery
#define DISCOVERY_MESSAGE "DISCOVER_REQUEST"
#define DISCOVERY_REPLY "DISCOVER_REPLY"

#define TRUE 1
#define FALSE 0
#define BUFFER_SIZE 5000
#define ID_SIZE 10
#define SEPARATOR '~'
#define MAX_PLAYERS 100  // Added max players definition

#define REUSEADDR_FLAG 1
#define BROADCAST_FLAG 1
#define RCVBUF_SIZE 10485760
#define SNDBUF_SIZE 10485760
#define SOCKET_PRIORITY 6

#define SLEEP_TIME 1000

#define PYTHON_PORT 50000
#define C_PORT1 50001
#define C_PORT2 50002
#define EXTERNAL_PORT 50002

#define LOCALHOST_IP "127.0.0.1"
#define BROADCAST_IP "255.255.255.255"

typedef struct {
    int sockfd;
    struct sockaddr_in destination_addr;
    struct sockaddr_in listener_addr;
    char recv_buffer[BUFFER_SIZE];
    char instance_id[ID_SIZE];
} Communicator;

typedef struct {
    struct sockaddr_in sender;
    char* sender_id;
    char* query;
    int id;
} PacketInfo;

typedef struct {
    char ip[INET_ADDRSTRLEN];     // IP address
    char instance_id[ID_SIZE];    // Unique instance identifier
    time_t last_seen;             // Last time this player was active
    int PacketsCount;
} PlayerInfo;

typedef struct {
    PlayerInfo players[MAX_PLAYERS];  // Fixed-size array of players
    int count;                        // Current number of players
} PlayersTable;

void generate_instance_id(Communicator* comm);
Communicator* init_communicator(int listener_port, int destination_port, const char* destination_addr);
char* construct_buffer(Communicator* comm, const char* query);
int send_buffer(Communicator* comm, const char* buffer);
int process_buffer(Communicator* comm, PacketInfo* packet);
int receive_buffer(Communicator* comm, struct sockaddr_in sender);
void cleanup_communicator(Communicator* comm);

// Updated player table functions
PlayersTable* init_player_table();
int find_player(PlayersTable* table, const char* ip);
int add_player(PlayersTable* table, const char* ip, const char* instance_id);
void remove_player(PlayersTable* table, const char* ip);
void cleanup_stale_players(PlayersTable* table, time_t max_age);
void print_players(PlayersTable* table);
void send_discovery_broadcast(Communicator* external_communicator);
int handle_discovery(PacketInfo* packet, PlayersTable* players_table);

#endif // COMMUNICATOR_H