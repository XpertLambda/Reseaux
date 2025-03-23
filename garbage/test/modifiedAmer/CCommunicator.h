#ifndef CCOMMUNICATOR_H
#define CCOMMUNICATOR_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <errno.h>
#include <unistd.h>
#include <fcntl.h>

#define ACTION_LEN 2048
#define BROADCAST "255.255.255.255"  // Broadcast IP
#define C_PORT2 50003
#define EXTERNAL_PORT 50003
#define SLEEP_TIME 10000     // Sleep time in microseconds (10ms)

typedef struct {
    int sockfd;
    struct sockaddr_in c_addr;
    struct sockaddr_in external_addr;
    char recv_buffer[ACTION_LEN];
} CCommunicator;

CCommunicator* init_C_communicator(int c_port, int external_port, const char* external_ip);
int send_to_external(CCommunicator* comm, const char* message);
int receive_message(CCommunicator* comm);
void cleanup_communicator(CCommunicator* comm);

#endif