#include "action_connection.h"

struct sockaddr_in broadcast_addr;

void send_action(char * action,int sockfd){
    int broadcast=1;
    if(setsockopt(sockfd, SOL_SOCKET, SO_BROADCAST, &broadcast, sizeof(broadcast))<0){
        perror("error broadcasting");
        return;
    }; // to allow broadcasting

    memset(&broadcast_addr, 0, sizeof(broadcast_addr));
    broadcast_addr.sin_family=AF_INET;
    broadcast_addr.sin_port=htons(PORT);
    broadcast_addr.sin_addr.s_addr=inet_addr(IP);   

    printf("listening on the ip:%s and on the port:%d...\n",IP,PORT);
    printf("start commmunication...\n");

    while(1){
        if (!fgets(action, ACTION_LEN, stdin)) {
                printf("Error fget.\n");
                return;
            }

        action[strcspn(action, "\n")] = '\0'; //put /0 when we go to another line

        if (sendto(sockfd, action, ACTION_LEN, 0, (struct sockaddr *)&broadcast_addr, sizeof(broadcast_addr))<0){
            perror("sent failed");
            return;
        }
    }
    close(sockfd);
}

