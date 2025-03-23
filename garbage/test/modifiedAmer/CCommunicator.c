#include "CCommunicator.h"

CCommunicator* init_C_communicator(int c_port, int external_port, const char* external_ip) {
    CCommunicator* comm = (CCommunicator*)malloc(sizeof(CCommunicator));
    if (!comm) {
        perror("Memory allocation failed");
        return NULL;
    }

    // Create socket
    if ((comm->sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Socket creation failed");
        free(comm);
        return NULL;
    }

    // Set socket to non-blocking mode
    int flags = fcntl(comm->sockfd, F_GETFL, 0);
    if (fcntl(comm->sockfd, F_SETFL, flags | O_NONBLOCK) < 0) {
        perror("Failed to set socket to non-blocking mode");
        close(comm->sockfd);
        free(comm);
        return NULL;
    }
    
    int opt = 1; //Address reuse
    if (setsockopt(comm->sockfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("setsockopt SO_REUSEADDR failed");
        close(comm->sockfd);
        free(comm);
        return NULL;
    }

    int broadcast = 1; // Enable broadcasting
    if (setsockopt(comm->sockfd, SOL_SOCKET, SO_BROADCAST, &broadcast, sizeof(broadcast)) < 0) {
        perror("setsockopt SO_BROADCAST failed");
        close(comm->sockfd);
        free(comm);
        return NULL;
    }

    //Receiving address
    memset(&comm->c_addr, 0, sizeof(comm->c_addr));
    comm->c_addr.sin_family = AF_INET;
    comm->c_addr.sin_port = htons(c_port);
    comm->c_addr.sin_addr.s_addr = INADDR_ANY;

    //Broadcasting address
    memset(&comm->external_addr, 0, sizeof(comm->external_addr));
    comm->external_addr.sin_family = AF_INET;
    comm->external_addr.sin_port = htons(external_port);
    comm->external_addr.sin_addr.s_addr = inet_addr(external_ip);

    // Bind socket for receiving
    if (bind(comm->sockfd, (struct sockaddr*)&comm->c_addr, sizeof(comm->c_addr)) < 0) {
        perror("Binding socket failed");
        close(comm->sockfd);
        free(comm);
        return NULL;
    }

    printf("[+] Initialized communicator (port: %d, broadcast IP: %s)\n", c_port, external_ip);
    return comm;
}

int send_to_external(CCommunicator* comm, const char* message) {
    int result = sendto(comm->sockfd, message, strlen(message), 0, (struct sockaddr*)&comm->external_addr, sizeof(comm->external_addr));
    
    if (result < 0) {
        if (errno != EAGAIN && errno != EWOULDBLOCK) {
            perror("Send failed");
        }
        return -1;
    }
    
    printf("[+] Sent: %s\n", message);
    return result;
}

int receive_message(CCommunicator* comm) {
    struct sockaddr_in sender_addr;
    socklen_t addr_len = sizeof(sender_addr);

    memset(comm->recv_buffer, 0, ACTION_LEN);
    
    int recv_len = recvfrom(comm->sockfd, comm->recv_buffer, ACTION_LEN - 1, 0, (struct sockaddr*)&sender_addr, &addr_len);

    if (recv_len > 0) {
        comm->recv_buffer[recv_len] = '\0';
        printf("[+] Received: %s from %s:%d\n", comm->recv_buffer, inet_ntoa(sender_addr.sin_addr), ntohs(sender_addr.sin_port));
        return recv_len;
    
    } else if (errno != EAGAIN && errno != EWOULDBLOCK) {
        perror("Receive failed");
    }

    return -1;
}

void cleanup_communicator(CCommunicator* comm) {
    if (comm) {
        close(comm->sockfd);
        free(comm);
        printf("[+] Communicator cleaned up\n");
    }
}