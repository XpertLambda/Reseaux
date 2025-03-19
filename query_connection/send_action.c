#include "action_connection.h"

struct sockaddr_in broadcast_addr;

void send_action(char * action,int SOCKFD) {
    SOCKFD = socket(AF_INET, SOCK_DGRAM, 0);
    if (SOCKFD < 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    // Activer le mode broadcast
    int broadcastEnable = 1;
    if (setsockopt(SOCKFD, SOL_SOCKET, SO_BROADCAST, &broadcastEnable, sizeof(broadcastEnable)) < 0) {
        perror("setsockopt (SO_BROADCAST)");
        close(SOCKFD);
        exit(EXIT_FAILURE);
    }

    memset(&broadcast_addr, 0, sizeof(broadcast_addr));
    broadcast_addr.sin_family = AF_INET;
    broadcast_addr.sin_port = htons(PORT);
    broadcast_addr.sin_addr.s_addr = inet_addr(BROADCAST_IP); // Utilisation de l'IP de broadcast

    while (1) {
        printf("Enter the action: ");
        fflush(stdout);

        if (!fgets(action, ACTION_LEN, stdin)) {
            printf("Error fgets.\n");
            break;
        }

        action[strcspn(action, "\n")] = '\0'; // Supprimer le saut de ligne

        if (sendto(SOCKFD, action, ACTION_LEN, 0, (struct sockaddr *)&broadcast_addr, sizeof(broadcast_addr)) < 0) {
            perror("send failed");
        }
    }

    close(SOCKFD);
}
