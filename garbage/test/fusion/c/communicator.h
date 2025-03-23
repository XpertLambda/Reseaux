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
#define BUFFER_SIZE 2048
#define FLAGS 0
#define SLEEP_TIME 10000

#define PYTHON_PORT 50000
#define C_PORT1 50001
#define C_PORT2 50002
#define EXTERNAL_PORT 50002

#define LOCALHOST_IP "127.0.0.1"
#define BROADCAST_IP "255.255.255.255"

typedef struct {
    int sockfd;                   // Socket file descriptor
    struct sockaddr_in destination_addr;  // Address to send to
    struct sockaddr_in listener_addr;     // Address to receive on
    char recv_buffer[BUFFER_SIZE];        // Buffer for receiving messages
    char instance_id[ID_SIZE];  // Unique identifier for this instance
} Communicator;

Communicator* init_communicator(int listener_port, int destination_port, const char* destination_addr, int REUSEADDR_FLAG, int BROADCAST_FLAG);
int send_query(Communicator* comm, const char* query);
char* receive_query(Communicator* comm);
void cleanup_communicator(Communicator* comm);

#endif // COMMUNICATOR_H