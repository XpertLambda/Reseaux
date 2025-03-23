#include "communicator.h"

Communicator* init_communicator(int listener_port, int destination_port, const char* destination_addr, int REUSEADDR_FLAG, int BROADCAST_FLAG) {
    Communicator* comm = (Communicator*)malloc(sizeof(Communicator));
    if (!comm) {
        perror("Memory allocation failed");
        return NULL;
    }
    
    // Generate random unique ID
    srand(time(NULL) ^ getpid());
    snprintf(comm->instance_id, ID_SIZE, "%08X", rand() % 0xFFFFFFFF);
    
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

int send_query(Communicator* comm, const char* query) {
    char buffer[BUFFER_SIZE];
    char* destination_ip = inet_ntoa(comm->destination_addr.sin_addr);
    int destination_port = ntohs(comm->destination_addr.sin_port);
    
    if (destination_port != PYTHON_PORT){
    	snprintf(buffer, BUFFER_SIZE, "%s:%s", comm->instance_id, query);
    } else {
        snprintf(buffer, BUFFER_SIZE, "%s", query);
    }

    int result = sendto(comm->sockfd, buffer, strlen(buffer), 0, (struct sockaddr*)&comm->destination_addr, sizeof(comm->destination_addr));
    if (result < 0) {
        if (errno != EAGAIN && errno != EWOULDBLOCK) {
            perror("Send failed");
        }
        return -1;
    }
    printf("[+] Sent: %s to %s:%d \n", buffer, destination_ip, destination_port);
    return result;
}

char* receive_query(Communicator* comm) {
    struct sockaddr_in sender_addr;
    socklen_t addr_len = sizeof(sender_addr);
    memset(comm->recv_buffer, 0, BUFFER_SIZE);
    
    int recv_len = recvfrom(comm->sockfd, comm->recv_buffer, BUFFER_SIZE - 1, 0, (struct sockaddr*)&sender_addr, &addr_len);
    
    if (recv_len > 0) {
        comm->recv_buffer[recv_len] = '\0';  // Null-terminate the received data
        
        // Check if message has an ID prefix
        char* colon = strchr(comm->recv_buffer, ':');
        if (colon && (colon - comm->recv_buffer) < ID_SIZE) {
            // Extract the ID part
            char msg_id[ID_SIZE];
            int id_len = colon - comm->recv_buffer;
            strncpy(msg_id, comm->recv_buffer, id_len);
            msg_id[id_len] = '\0';
            
            // Check if it's our own message
            if (strcmp(msg_id, comm->instance_id) == 0) {
                // It's our own message, ignore it
                printf("[*] Ignored own message with ID %s\n", msg_id);
                return NULL;
            }
            
            // Not our message, move the message content to the beginning of the buffer
            // to return just the message without the ID
            char* message_content = colon + 1;
            memmove(comm->recv_buffer, message_content, strlen(message_content) + 1);
            printf("[+] Received: %s from %s:%d (Sender ID: %s)\n", comm->recv_buffer, inet_ntoa(sender_addr.sin_addr), ntohs(sender_addr.sin_port), msg_id);
            return comm->recv_buffer;
        } else {
            // No valid ID format found, just return as is but log a warning
            printf("[+] Received message without proper ID format: %s from %s:%d\n", comm->recv_buffer, inet_ntoa(sender_addr.sin_addr), ntohs(sender_addr.sin_port));
            return comm->recv_buffer;
        }

    } else if (recv_len == -1 && errno != EAGAIN && errno != EWOULDBLOCK) {
        perror("Receive failed");
    }
    return NULL;
}

void cleanup_communicator(Communicator* comm) {
    if (comm) {
        close(comm->sockfd);
        free(comm);
        printf("[+] Communicator cleaned up\n");
    }
}