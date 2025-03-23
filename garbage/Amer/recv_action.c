#include "action_connection.h"

struct sockaddr_in recv_addr;

void recv_action(int sockfd){

    int opt=1;
    if(setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt))<0){
        perror("error reuseaddr");
        return;
    }; // to allow using the same port

    memset(&recv_addr, 0, sizeof(recv_addr));
    recv_addr.sin_family=AF_INET;
    recv_addr.sin_port=htons(PORT);
    recv_addr.sin_addr.s_addr=INADDR_ANY;

    if(bind(sockfd, (struct sockaddr*)&recv_addr, sizeof(recv_addr)) < 0){
        perror("bind() failed for UDP");
        return;
    }

    char action[ACTION_LEN];
    struct sockaddr_in sender_addr;
    socklen_t sender_len=sizeof(sender_addr);

    while(1){
        memset(action,0, ACTION_LEN); //for cleaning the buffer

        int recv=recvfrom(sockfd, action, ACTION_LEN - 1, 0, (struct sockaddr *)&sender_addr, &sender_len);
        if (recv<0) {
            perror("recv error");
            return;
        }
        action[recv]='\0';
        printf("%s\n", action);

    }
    close(sockfd);          
}
