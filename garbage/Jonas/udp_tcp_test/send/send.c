// send.c : Envoi d'un fichier .pickle via UDP en Broadcast sur le port 50003
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define BUF_SIZE 1024
#define PORT 50003

void send_pickle(char *ip_dest, char *filename) {
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    // 🔥 Activer le mode broadcast
    int broadcast_enable = 1;
    if (setsockopt(sockfd, SOL_SOCKET, SO_BROADCAST, &broadcast_enable, sizeof(broadcast_enable)) < 0) {
        perror("setsockopt (SO_BROADCAST)");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    struct sockaddr_in dest_addr;
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(PORT);

    // 🔥 Vérifier si l'adresse est en broadcast
    if (strcmp(ip_dest, "255.255.255.255") == 0) {
        dest_addr.sin_addr.s_addr = INADDR_BROADCAST;  // Utiliser l'adresse broadcast
    } else {
        inet_pton(AF_INET, ip_dest, &dest_addr.sin_addr);
    }

    FILE *file = fopen(filename, "rb");
    if (!file) {
        perror("fopen");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    char buffer[BUF_SIZE];
    int bytes_read;

    sendto(sockfd, filename, strlen(filename) + 1, 0, (struct sockaddr*)&dest_addr, sizeof(dest_addr));
    usleep(1000);

    while ((bytes_read = fread(buffer, 1, BUF_SIZE, file)) > 0) {
        sendto(sockfd, buffer, bytes_read, 0, (struct sockaddr*)&dest_addr, sizeof(dest_addr));
        usleep(1000);
    }

    const char *end_marker = "__END__";
    sendto(sockfd, end_marker, strlen(end_marker) + 1, 0, (struct sockaddr*)&dest_addr, sizeof(dest_addr));

    printf("'%s' envoyé à %s:%d\n", filename, ip_dest, PORT);

    fclose(file);
    close(sockfd);
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        printf("Usage: %s <IP_dest ou 255.255.255.255> <fichier_pickle>\n", argv[0]);
        return 1;
    }
    send_pickle(argv[1], argv[2]);
    return 0;
}
