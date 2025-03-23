#include "CythonCommunicator.h"

CythonCommunicator* init_cython_communicator(int c_port, int python_port, const char* python_ip) {
    CythonCommunicator* comm = (CythonCommunicator*)malloc(sizeof(CythonCommunicator));
    if (!comm) {
        perror("Memory allocation failed");
        return NULL;
    }

    // Create socket
    if ((comm->sockfd = socket(AF_INET, SOCK_DGRAM, FLAGS)) < 0) {
        perror("Socket creation failed");
        free(comm->python_ip);
        free(comm);
        return NULL;
    }

    // Set socket to non-blocking mode
    int flags = fcntl(comm->sockfd, F_GETFL, 0);
    if (fcntl(comm->sockfd, F_SETFL, flags | O_NONBLOCK) < 0) {
        perror("Failed to set socket to non-blocking mode");
        close(comm->sockfd);
        free(comm->python_ip);
        free(comm);
        return NULL;
    }

    // Configure receiving address
    memset(&comm->c_addr, 0, sizeof(comm->c_addr));
    comm->c_addr.sin_family = AF_INET;
    comm->c_addr.sin_addr.s_addr = INADDR_ANY;
    comm->c_addr.sin_port = htons(c_port);

    // Configure sending address
    memset(&comm->python_addr, 0, sizeof(comm->python_addr));
    comm->python_addr.sin_family = AF_INET;
    comm->python_addr.sin_addr.s_addr = inet_addr(python_ip);
    comm->python_addr.sin_port = htons(python_port);

    // Bind socket for receiving
    if (bind(comm->sockfd, (struct sockaddr*)&comm->c_addr, sizeof(comm->c_addr)) < 0) {
        perror("Binding socket failed");
        close(comm->sockfd);
        free(comm->python_ip);
        free(comm);
        return NULL;
    }

    printf("[+] Initialized communicator (c_port: %d, python_port: %d, python_ip: %s)\n", c_port, python_port, python_ip);
    return comm;
}

int send_message(CythonCommunicator* comm, const char* message) {
    int result = sendto(comm->sockfd, message, strlen(message), 0, (struct sockaddr*)&comm->python_addr, sizeof(comm->python_addr));
    if (result < 0) {
        if (errno != EAGAIN && errno != EWOULDBLOCK) {
            perror("Send failed");
        }
        return -1;
    }
    printf("[+] Sent: %s\n", message);
    return result;
}

int receive_message(CythonCommunicator* comm) {
    struct sockaddr_in sender_addr;
    socklen_t addr_len = sizeof(sender_addr);

    int recv_len = recvfrom(comm->sockfd, comm->recv_buffer, BUFFER_SIZE - 1, 0, (struct sockaddr*)&sender_addr, &addr_len);

    if (recv_len > 0) {
        comm->recv_buffer[recv_len] = '\0';
        printf("[+] Received: %s from %s:%d\n", comm->recv_buffer, inet_ntoa(sender_addr.sin_addr), ntohs(sender_addr.sin_port));
        return recv_len;
    } else if (errno != EAGAIN && errno != EWOULDBLOCK) {
        perror("Receive failed");
    }

    return -1;
}

void cleanup_communicator(CythonCommunicator* comm) {
    if (comm) {
        close(comm->sockfd);
        free(comm->python_ip);
        free(comm);
        printf("[+] Communicator cleaned up\n");
    }
}
