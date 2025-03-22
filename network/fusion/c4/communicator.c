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
    
    // Initialize sequence counters
    comm->send_seq = 0;
    comm->last_recv_seq = 0;
    comm->packets_lost = 0;

    // Create socket
    if ((comm->sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("Socket creation failed");
        free(comm);
        return NULL;
    }
    
    // Non-blocking mode
    int flags = fcntl(comm->sockfd, F_GETFL, 0);
    if (fcntl(comm->sockfd, F_SETFL, flags | O_NONBLOCK) < 0) {
        perror("Failed to set socket to non-blocking mode");
        close(comm->sockfd);
        free(comm);
        return NULL;
    }
    
    // Socket options for reliability
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

    // Set receive buffer size
    int receive_buff = RCVBUF_SIZE;
    if (setsockopt(comm->sockfd, SOL_SOCKET, SO_RCVBUF, &receive_buff, sizeof(receive_buff)) < 0) {
        perror("setsockopt SO_RCVBUF failed");
        close(comm->sockfd);
        free(comm);
        return NULL;
    }
    
    // Set send buffer size
    int send_buff = SNDBUF_SIZE;
    if (setsockopt(comm->sockfd, SOL_SOCKET, SO_SNDBUF, &send_buff, sizeof(send_buff)) < 0) {
        perror("setsockopt SO_SNDBUF failed");
        close(comm->sockfd);
        free(comm);
        return NULL;
    }
    
    // Set priority for this socket's traffic
    int priority = 6;  // High priority
    if (setsockopt(comm->sockfd, SOL_SOCKET, SO_PRIORITY, &priority, sizeof(priority)) < 0) {
        perror("setsockopt SO_PRIORITY failed");
        // Not critical, continue anyway
    }

    // Receiving address
    memset(&comm->listener_addr, 0, sizeof(comm->listener_addr));
    comm->listener_addr.sin_family = AF_INET;
    comm->listener_addr.sin_port = htons(listener_port);
    comm->listener_addr.sin_addr.s_addr = INADDR_ANY;
    
    // Destination address
    memset(&comm->destination_addr, 0, sizeof(comm->destination_addr));
    comm->destination_addr.sin_family = AF_INET;
    comm->destination_addr.sin_port = htons(destination_port);
    
    // Handle both IP address and broadcast formats
    if (strcmp(destination_addr, BROADCAST_IP) == 0) {
        comm->destination_addr.sin_addr.s_addr = INADDR_BROADCAST;
    } else {
        comm->destination_addr.sin_addr.s_addr = inet_addr(destination_addr);
    }
    
    // Bind socket for receiving
    if (bind(comm->sockfd, (struct sockaddr*)&comm->listener_addr, sizeof(comm->listener_addr)) < 0) {
        perror("Binding socket failed");
        close(comm->sockfd);
        free(comm);
        return NULL;
    }

    // Initialize rate limiting
    comm->last_send_time = current_time_micros();
    comm->send_rate_limit = DEFAULT_SEND_RATE;

    printf("[+] Initialized communicator (ID: %s, listener %s:%d, destination %s:%d)\n", 
           comm->instance_id, 
           inet_ntoa(comm->listener_addr.sin_addr), 
           ntohs(comm->listener_addr.sin_port), 
           inet_ntoa(comm->destination_addr.sin_addr), 
           ntohs(comm->destination_addr.sin_port));

    return comm;
}

void construct_packet(Communicator* comm, const char* query, char* packet, size_t packet_size) {
    if (ntohs(comm->destination_addr.sin_port) != PYTHON_PORT) {
        // Format: ID:SEQUENCE:PAYLOAD
        snprintf(packet, packet_size, "%s:%d:%s", comm->instance_id, comm->send_seq, query);
        comm->send_seq++;
    } else {
        // For Python communication, just send the payload
        strncpy(packet, query, packet_size - 1);
        packet[packet_size - 1] = '\0';
    }
}

// Get current time in microseconds for rate limiting
uint64_t current_time_micros() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (uint64_t)tv.tv_sec * 1000000 + tv.tv_usec;
}

int send_packet(Communicator* comm, const char* query) {
    // Apply rate limiting
    uint64_t now = current_time_micros();
    uint64_t elapsed = now - comm->last_send_time;
    
    if (elapsed < comm->send_rate_limit) {
        uint64_t sleep_time = comm->send_rate_limit - elapsed;
        usleep(sleep_time);
    }
    comm->last_send_time = current_time_micros();

    char packet[BUFFER_SIZE];
    construct_packet(comm, query, packet, BUFFER_SIZE);

    int result = sendto(comm->sockfd, packet, strlen(packet), 0, 
                       (struct sockaddr*)&comm->destination_addr, 
                       sizeof(comm->destination_addr));
                       
    if (result < 0) {
        if (errno != EAGAIN && errno != EWOULDBLOCK) {
            perror("Send failed");
        }
        return -1;
    }
    
    return result;
}

// Modified to handle sequence numbers
char* process_packet(char* packet, char* packet_id, int* seq_num) {
    char* first_separator = strchr(packet, SEPARATOR);
    
    if (!first_separator) {
        *packet_id = '\0';
        *seq_num = -1;
        return packet;
    }
    
    size_t id_length = first_separator - packet;
    memcpy(packet_id, packet, id_length);
    packet_id[id_length] = '\0';
    
    char* second_separator = strchr(first_separator + 1, SEPARATOR);
    if (!second_separator) {
        *seq_num = -1;
        return first_separator + 1;
    }
    
    // Extract sequence number
    char seq_str[16] = {0};
    size_t seq_length = second_separator - (first_separator + 1);
    memcpy(seq_str, first_separator + 1, seq_length);
    seq_str[seq_length] = '\0';
    *seq_num = atoi(seq_str);
    
    return second_separator + 1;
}

void log_message(const char* query, const struct sockaddr_in* sender_addr, const char* packet_id, int seq_num) {
    if (*packet_id) {
        printf("[+] Received: %s from %s:%d (Sender ID: %s, Seq: %d)\n", 
               query, inet_ntoa(sender_addr->sin_addr), 
               ntohs(sender_addr->sin_port), packet_id, seq_num);
    } else {
        printf("[+] Received query without proper format: %s from %s:%d\n", 
               query, inet_ntoa(sender_addr->sin_addr), 
               ntohs(sender_addr->sin_port));
    }
}

char* receive_packet(Communicator* comm) {
    struct sockaddr_in sender_addr;
    socklen_t addr_len = sizeof(sender_addr);

    int recv_len = recvfrom(comm->sockfd, comm->recv_buffer, BUFFER_SIZE - 1, 0, 
                          (struct sockaddr*)&sender_addr, &addr_len);
    
    if (recv_len <= 0) {
        if (recv_len == -1 && errno != EAGAIN && errno != EWOULDBLOCK) {
            perror("Receive failed");
        }
        return NULL;
    }
    
    comm->recv_buffer[recv_len] = '\0';
    
    char packet_id[ID_SIZE];
    int seq_num;
    char* query = process_packet(comm->recv_buffer, packet_id, &seq_num);
    
    // Skip our own packets
    if (strcmp(packet_id, comm->instance_id) == 0) {
        return NULL;
    }

    // Track packet loss
    if (seq_num >= 0) {
        if (comm->last_recv_seq > 0 && seq_num > comm->last_recv_seq + 1) {
            comm->packets_lost += (seq_num - comm->last_recv_seq - 1);
            printf("[!] Detected packet loss! Missing %d packets between %d and %d\n",
                  seq_num - comm->last_recv_seq - 1, comm->last_recv_seq, seq_num);
        }
        comm->last_recv_seq = seq_num;
    }
    
    // Move the payload to the beginning of the buffer
    if (query != comm->recv_buffer) {
        size_t content_len = strlen(query);
        memmove(comm->recv_buffer, query, content_len + 1);
    }

    return comm->recv_buffer;
}

void cleanup_communicator(Communicator* comm) {
    if (comm) {
        close(comm->sockfd);
        free(comm);
        printf("[+] Communicator cleaned up\n");
    }
}

// Adaptively adjust send rate based on packet loss
void adjust_send_rate(Communicator* comm) {
    // If we've detected packet loss, slow down
    if (comm->packets_lost > 0) {
        comm->send_rate_limit += RATE_INCREASE_STEP;
        if (comm->send_rate_limit > MAX_SEND_RATE) {
            comm->send_rate_limit = MAX_SEND_RATE;
        }
        printf("[+] Increased send rate limit to %lu microseconds due to packet loss\n", 
               comm->send_rate_limit);
    } else {
        // If no packet loss, we can speed up slightly
        if (comm->send_rate_limit > MIN_SEND_RATE) {
            comm->send_rate_limit -= RATE_DECREASE_STEP;
        }
    }
    
    // Reset packet loss counter for next period
    comm->packets_lost = 0;
}