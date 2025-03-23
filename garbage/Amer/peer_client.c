#include "action_connection.h"


int main(){
    int sockfd=socket(AF_INET,SOCK_DGRAM,0);
    char action[ACTION_LEN];

    if (sockfd<0){
        perror("error socket");
        return EXIT_FAILURE;
    }
    
    int pid=fork();
    if (pid==0){
        recv_action(sockfd);
    }else{
        send_action(action,sockfd);
    }
    
    return 0;
    
}