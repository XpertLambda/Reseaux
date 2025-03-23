#ifndef ACTION_CONNECTION_H
#define ACTION_CONNECTION_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <errno.h>
#include <unistd.h>

#define ACTION_LEN 2048
#define IP "255.255.255.255"
#define PORT 50003

void send_action(char * action,int sockfd);
void recv_action(int sockfd);
#endif

