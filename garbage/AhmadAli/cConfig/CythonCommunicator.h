#ifndef COMMUNICATOR_H
#define COMMUNICATOR_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <time.h>

#define BUFFER_SIZE 1024
#define FLAGS 0
#define MESSAGE_INTERVAL 0 // seconds between messages
#define PYTHON_PORT 50000
#define C_PORT 50001
#define LOCALHOST "127.0.0.1"
#define SLEEP_TIME 10000

typedef struct {
    int sockfd;                     // Socket file descriptor
    struct sockaddr_in python_addr;   // Address to send to
    struct sockaddr_in c_addr;   // Address to receive on
    char recv_buffer[BUFFER_SIZE];  // Buffer for receiving messages
    int c_port;                  // Port to listen on
    int python_port;                  // Port to send to
    char* python_ip;                  // IP to send to
    time_t last_send_time;          // Time of last message sent
} CythonCommunicator;

CythonCommunicator* init_communicator(int c_port, int python_port, const char* python_ip);
int send_message(CythonCommunicator* comm, const char* message);
int receive_message(CythonCommunicator* comm);
void cleanup_communicator(CythonCommunicator* comm);

#endif // COMMUNICATOR_H
