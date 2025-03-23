#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <unistd.h>

#define SERVER_IP "127.0.0.1"  
#define SERVER_PORT 50000

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <message>\n", argv[0]);
        return 1;
    }

    int sockfd;
    struct sockaddr_in server_addr;
    
    // UDP socket
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("Socket creation failed");
        return 1;
    }

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    server_addr.sin_addr.s_addr = inet_addr(SERVER_IP);

    // Send message
    if (sendto(sockfd, argv[1], strlen(argv[1]), 0, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        perror("Send failed");
        return 1;
    }

    printf("Message sent: %s\n", argv[1]);

    // Close socket
    close(sockfd);
    return 0;
}
