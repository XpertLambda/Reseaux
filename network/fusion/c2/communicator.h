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

#define TRUE 1
#define FALSE 0
#define ID_SIZE 10
#define SEPARATOR ':'
#define BUFFER_SIZE 2048
#define RCVBUF_SIZE 1048576
#define FLAGS 0
#define SLEEP_TIME 10000

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

void generate_instance_id(Communicator* comm);
Communicator* init_communicator(int listener_port, int destination_port, const char* destination_addr, int REUSEADDR_FLAG, int BROADCAST_FLAG);
void construct_packet(Communicator* comm, const char* query, char* packet, size_t packet_size);
int send_packet(Communicator* comm, const char* message);
char* process_packet(char* packet, char* packet_id, size_t id_size);
void log_message(const char* message, const struct sockaddr_in* sender_addr, const char* packet_id);
char* receive_packet(Communicator* comm);
void cleanup_communicator(Communicator* comm);

#endif // COMMUNICATOR_H