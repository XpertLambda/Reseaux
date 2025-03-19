#include "action_connection.h"

int main() {
    int sockfd;
    char action[ACTION_LEN];

    // Initialisation correcte du socket avant le fork
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    int pid = fork();
    if (pid == 0) {
        recv_action(sockfd);
    } else {
        send_action(action, sockfd);
    }

    close(sockfd);
    return 0;
}
