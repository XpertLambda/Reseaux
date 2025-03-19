#include "action_connection.h"

struct sockaddr_in recv_addr;

void recv_action(int SOCKFD){
    SOCKFD=socket(AF_INET,SOCK_DGRAM,0);
    memset(&recv_addr, 0, sizeof(recv_addr));

    recv_addr.sin_family=AF_INET;
    recv_addr.sin_port=htons(PORT);
    recv_addr.sin_addr.s_addr=INADDR_ANY;

    int opt=1;
    setsockopt(SOCKFD, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)); // to allow using the same port

    char action[ACTION_LEN];
    if(bind(SOCKFD, (struct sockaddr*)&recv_addr, sizeof(recv_addr)) < 0){
        perror("bind() failed for UDP");
        return;
    }

    while(1){
        memset(action,0, ACTION_LEN); //for cleaning the buffer
        int recv=recvfrom(SOCKFD, action, ACTION_LEN - 1, 0, (struct sockaddr *)&recv_addr, (socklen_t *)&recv_addr);
        if (recv<0) {
            perror("recv error");
            return;
        }
        action[recv]='\0';
        printf("recieved: %s\n", action);

    }

    close(SOCKFD);          
}
