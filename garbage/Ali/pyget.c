#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <unistd.h>

#define PORT 50001
#define BUFFER_SIZE 1024
#define FLAGS 0
#define INFO_BUFFER_SIZE 100

const char* get_addr_info(struct sockaddr_in *addr) {
    static char info[INFO_BUFFER_SIZE]; // Static buffer to store result
    snprintf(info, INFO_BUFFER_SIZE, "IP: %s, Port: %d",
             inet_ntoa(addr->sin_addr), ntohs(addr->sin_port));
    return info;
}



int main(){
    int sockfd, recv_len;

    struct sockaddr_in C_addr, python_addr;

    char buffer[BUFFER_SIZE];
    socklen_t addr_len = sizeof(python_addr);

    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, FLAGS)) < 0){
        perror("[-] socket creation failed!");
        exit(EXIT_FAILURE);
    }

    memset(&C_addr, 0, sizeof(C_addr));
    C_addr.sin_family = AF_INET;
    C_addr.sin_addr.s_addr = INADDR_ANY;
    C_addr.sin_port = htons(PORT);

    if (bind(sockfd, (struct sockaddr*)&C_addr, sizeof(C_addr)) < 0){
        perror("[-] binding socket failed!");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    printf("[+] listening on port %d\n", PORT);

    if ((recv_len = recvfrom(sockfd, buffer, BUFFER_SIZE, 0, (struct sockaddr*)&python_addr, &addr_len)) > 0){
        buffer[recv_len] = '\0';
        printf("+> received: %s\n", buffer);
        printf("=> sender: %s\n", get_addr_info(&python_addr));
    }

    close(sockfd);

    return 0;
}
