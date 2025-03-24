#include "action_connection.h"


int main(){
    int sockfd;
    char action[ACTION_LEN];
    int pid=fork();
    if (pid==0){
        recv_action(sockfd);
    }else{
        send_action(action,sockfd);
    }
    return 0;
    
}