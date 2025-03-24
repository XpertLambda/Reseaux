#include "action_connection.h"

struct sockaddr_in recv_addr;

void recv_action(int SOCKFD) {
    SOCKFD = socket(AF_INET, SOCK_DGRAM, 0);
    if (SOCKFD < 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    // Autoriser la réutilisation de l'adresse
    int opt = 1;
    if (setsockopt(SOCKFD, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("setsockopt (SO_REUSEADDR)");
        close(SOCKFD);
        exit(EXIT_FAILURE);
    }

    memset(&recv_addr, 0, sizeof(recv_addr));
    recv_addr.sin_family = AF_INET;
    recv_addr.sin_port = htons(PORT);
    recv_addr.sin_addr.s_addr = INADDR_ANY;

    if (bind(SOCKFD, (struct sockaddr*)&recv_addr, sizeof(recv_addr)) < 0) {
        perror("bind() failed for UDP");
        close(SOCKFD);
        exit(EXIT_FAILURE);
    }

    char action[ACTION_LEN];
    struct sockaddr_in sender_addr;
    socklen_t sender_len = sizeof(sender_addr);

    while (1) {
        memset(action, 0, ACTION_LEN); // Nettoyage du buffer
        int recv = recvfrom(SOCKFD, action, ACTION_LEN - 1, 0, (struct sockaddr *)&sender_addr, &sender_len);
        if (recv < 0) {
            perror("recv error");
            break;
        }
        action[recv] = '\0';
        printf("Received: %s\n", action);
    }
    close(SOCKFD);
}
