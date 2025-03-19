#include "action_connection.h"

struct sockaddr_in broadcast_addr;

void send_action(char * action,int SOCKFD){

    SOCKFD=socket(AF_INET,SOCK_DGRAM,0);
    memset(&broadcast_addr, 0, sizeof(broadcast_addr));
    broadcast_addr.sin_family=AF_INET;
    broadcast_addr.sin_port=htons(PORT);
    broadcast_addr.sin_addr.s_addr=inet_addr(IP);
    while(1){
        printf("Enter the action:");
        fflush(stdout);

        if (!fgets(action, ACTION_LEN, stdin)) {
                printf("Error fget.\n");
                break;
            }

        action[strcspn(action, "\n")] = '\0'; //put /0 when we go to another line

        if (sendto(SOCKFD, action, ACTION_LEN, 0, (struct sockaddr *)&broadcast_addr, sizeof(broadcast_addr))<0){
            perror("sent failed");
        }
    }
    close(SOCKFD);
}

