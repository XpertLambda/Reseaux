#include "communicator.h"

void generate_instance_id(Communicator* comm) {
    srand(time(NULL) ^ getpid());
    snprintf(comm->instance_id, ID_SIZE, "%08X", rand() % 0xFFFFFFFF);
}

Communicator* init_communicator(int listener_port, int destination_port, const char* destination_addr, int REUSEADDR_FLAG, int BROADCAST_FLAG) {
    Communicator* comm = (Communicator*)malloc(sizeof(Communicator));
    if (!comm) {
        perror("Memory allocation failed");
        return NULL;
    }
    
    // Generate random unique ID
    generate_instance_id(comm);

    // Create socket
    if ((comm->sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Socket creation failed");
        free(comm);
        return NULL;
    }
    //Non-blocking mode
    int flags = fcntl(comm->sockfd, F_GETFL, 0);
    if (fcntl(comm->sockfd, F_SETFL, flags | O_NONBLOCK) < 0) {
        perror("Failed to set socket to non-blocking mode");
        close(comm->sockfd);
        free(comm);
        return NULL;
    }
    
    if (setsockopt(comm->sockfd, SOL_SOCKET, SO_REUSEADDR, &REUSEADDR_FLAG, sizeof(REUSEADDR_FLAG)) < 0) {
        perror("setsockopt SO_REUSEADDR failed");
        close(comm->sockfd);
        free(comm);
        return NULL;
    }
    if (setsockopt(comm->sockfd, SOL_SOCKET, SO_BROADCAST, &BROADCAST_FLAG, sizeof(BROADCAST_FLAG)) < 0) {
        perror("setsockopt SO_BROADCAST failed");
        close(comm->sockfd);
        free(comm);
        return NULL;
    }

    int recieve_buff = RCVBUF_SIZE;
    if (setsockopt(comm->sockfd, SOL_SOCKET, SO_RCVBUF, &recieve_buff, sizeof(recieve_buff)) < 0) {
        perror("setsockopt SO_RCVBUF failed");
        close(comm->sockfd);
        free(comm);
        return NULL;
    }

    int send_buff = SNDBUF_SIZE;
    if (setsockopt(comm->sockfd, SOL_SOCKET, SO_SNDBUF, &send_buff, sizeof(send_buff)) < 0) {
        perror("setsockopt SO_SNDBUF failed");
        close(comm->sockfd);
        free(comm);
        return NULL;
    }

    //Receiving address
    memset(&comm->listener_addr, 0, sizeof(comm->listener_addr));
    comm->listener_addr.sin_family = AF_INET;
    comm->listener_addr.sin_port = htons(listener_port);
    comm->listener_addr.sin_addr.s_addr = INADDR_ANY;
    
    //Destination address
    memset(&comm->destination_addr, 0, sizeof(comm->destination_addr));
    comm->destination_addr.sin_family = AF_INET;
    comm->destination_addr.sin_port = htons(destination_port);
    comm->destination_addr.sin_addr.s_addr = inet_addr(destination_addr);
    // Bind socket for receiving
    if (bind(comm->sockfd, (struct sockaddr*)&comm->listener_addr, sizeof(comm->listener_addr)) < 0) {
        perror("Binding socket failed");
        close(comm->sockfd);
        free(comm);
        return NULL;
    }

    printf("[+] Initialized communicator (ID: %s, listener %s:%d, destination %s:%d)\n",  comm->instance_id, inet_ntoa(comm->listener_addr.sin_addr),  ntohs(comm->listener_addr.sin_port), inet_ntoa(comm->destination_addr.sin_addr), ntohs(comm->destination_addr.sin_port));

    return comm;
}

void construct_packet(Communicator* comm, const char* query, char* packet, size_t packet_size) {
    if (ntohs(comm->destination_addr.sin_port) != PYTHON_PORT){
        snprintf(packet, packet_size, "%s:%s", comm->instance_id, query);
    } else {
        strncpy(packet, query, packet_size - 1);
        packet[packet_size - 1] = '\0';
    }
}

int send_packet(Communicator* comm, const char* query) {
    char* destination_ip = inet_ntoa(comm->destination_addr.sin_addr);
    int destination_port = ntohs(comm->destination_addr.sin_port);

    char packet[BUFFER_SIZE];
    construct_packet(comm, query, packet, BUFFER_SIZE);

    int result = sendto(comm->sockfd, packet, strlen(packet), 0, (struct sockaddr*)&comm->destination_addr, sizeof(comm->destination_addr));
    if (result < 0) {
        if (errno != EAGAIN && errno != EWOULDBLOCK) {
            perror("Send failed");
        }
        return -1;
    }
    //printf("[+] Sent: %s to %s:%d \n", packet, destination_ip, destination_port);
    return result;
}

char* process_packet(char* packet, char* packet_id, size_t id_size) {
    char* separator = strchr(packet, SEPARATOR);
    
    if (!separator) {
        *packet_id = '\0';
        return packet;
    }
    
    size_t id_length = separator - packet;
    size_t copy_size = (id_length < id_size - 1) ? id_length : id_size - 1;
    
    memcpy(packet_id, packet, copy_size);
    packet_id[copy_size] = '\0';
    
    return separator + 1;
}

void log_message(const char* query, const struct sockaddr_in* sender_addr, const char* packet_id) {
    if (*packet_id) {
        printf("[+] Received: %s from %s:%d (Sender ID: %s)\n", query, inet_ntoa(sender_addr->sin_addr), ntohs(sender_addr->sin_port), packet_id);
    } else {
        printf("[+] Received query without proper ID format: %s from %s:%d\n", query, inet_ntoa(sender_addr->sin_addr), ntohs(sender_addr->sin_port));
    }
}

char* receive_packet(Communicator* comm) {
    struct sockaddr_in sender_addr;
    socklen_t addr_len = sizeof(sender_addr);

    int recv_len = recvfrom(comm->sockfd, comm->recv_buffer, BUFFER_SIZE - 1, 0, (struct sockaddr*)&sender_addr, &addr_len);
    
    if (recv_len <= 0) {
        if (recv_len == -1 && errno != EAGAIN && errno != EWOULDBLOCK) {
            perror("Receive failed");
        }
        return NULL;
    }
    
    comm->recv_buffer[recv_len] = '\0';
    
    char packet_id[ID_SIZE];
    char* query = process_packet(comm->recv_buffer, packet_id, ID_SIZE);
    if (strcmp(packet_id, comm->instance_id) == 0) return NULL;

    if (query != comm->recv_buffer) {
        size_t content_len = strlen(query);
        memmove(comm->recv_buffer, query, content_len + 1);
    }

    //log_message(comm->recv_buffer, &sender_addr, packet_id);
    return comm->recv_buffer;
}

void cleanup_communicator(Communicator* comm) {
    if (comm) {
        close(comm->sockfd);
        free(comm);
        printf("[+] Communicator cleaned up\n");
    }
}