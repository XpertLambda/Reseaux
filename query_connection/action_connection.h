#define ACTION_CONNECTION_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <errno.h>
#include <unistd.h>
#include <pthread.h>

#define ACTION_LEN 2048
#define IP "127.0.0.1"
#define PORT 50003

void send_action(char * action,int SOCKFD);
void recv_action(int SOCKFD);

