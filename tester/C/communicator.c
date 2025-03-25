#include "communicator.h"

void generate_instance_id(Communicator* comm) {
    srand(time(NULL) ^ getpid());
    snprintf(comm->instance_id, ID_SIZE, "%08X", rand() % 0xFFFFFFFF);
}

Communicator* init_communicator(int listener_port, int destination_port, const char* destination_addr) {
    Communicator* comm = (Communicator*)malloc(sizeof(Communicator));
    if (!comm) {
        perror("Memory allocation failed");
        return NULL;
    }
    
    // Generate random unique ID
    generate_instance_id(comm);

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
    
    int reuseaddr = REUSEADDR_FLAG;
    if (setsockopt(comm->sockfd, SOL_SOCKET, SO_REUSEADDR, &reuseaddr, sizeof(reuseaddr)) < 0) {
        perror("setsockopt SO_REUSEADDR failed");
        close(comm->sockfd);
        free(comm);
        return NULL;
    }

    int broadcast = BROADCAST_FLAG;
    if (setsockopt(comm->sockfd, SOL_SOCKET, SO_BROADCAST, &broadcast, sizeof(broadcast)) < 0) {
        perror("setsockopt SO_BROADCAST failed");
        close(comm->sockfd);
        free(comm);
        return NULL;
    }

    // Set TTL value
    int ttl_value=TTL_VALUE;
    if (setsockopt(comm->sockfd, IPPROTO_IP, IP_TTL, &ttl_value, sizeof(ttl_value)) < 0) {
        perror("Failed to set IP_TTL");
        exit(EXIT_FAILURE);
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

    int priority = SOCKET_PRIORITY;
    if(setsockopt(comm->sockfd, SOL_SOCKET, SO_PRIORITY, &priority, sizeof(priority)) < 0){
        perror("setsockopt SO_PRIORITY failed");
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

    printf("[+] Initialized communicator (ID: %s | Listening on %d | Destination %d)\n",  comm->instance_id, ntohs(comm->listener_addr.sin_port), ntohs(comm->destination_addr.sin_port));
    printf("[+] Socket Options :\n");
    printf("\t[~] Non-blocking mode enabled\n");
    printf("\t[~] SO_REUSEADDR: %d\n", reuseaddr);
    printf("\t[~] SO_BROADCAST: %d\n", broadcast);
    printf("\t[~] SO_RCVBUF: %d bytes\n", recieve_buff);
    printf("\t[~] SO_SNDBUF: %d bytes\n", send_buff);
    printf("\t[~] SO_PRIORITY: %d\n", priority);

    return comm;
}

void construct_packet(Communicator* comm, const char* query, char* packet, size_t packet_size) {
    if (ntohs(comm->destination_addr.sin_port) != PYTHON_PORT){
        snprintf(packet, packet_size, "%s%c%s", comm->instance_id, SEPARATOR, query);
    } else {
        strncpy(packet, query, packet_size - 1);
        packet[packet_size - 1] = '\0';
    }
}

Keys* init_keys(){
    Keys *keys=(Keys*)malloc(sizeof(Keys));
    keys->aes_key=(unsigned char *)malloc(KEY_SIZE * sizeof(unsigned char));
        if (!keys->aes_key) {
        perror("key allocation failed");
        return NULL;
    }

    keys->aes_iv=(unsigned char *)malloc(IV_SIZE * sizeof(unsigned char));
        if (!keys->aes_iv) {
        perror("iv allocation failed");
        return NULL;
    }
    //iv for more security: when we have 2 same messages it avoids the ressemblance of their encryptions

    if(!RAND_bytes(keys->aes_key, sizeof(keys->aes_key))){
        perror("failed to generate key");
        return NULL;
    }; //for generating a random key
    if(!RAND_bytes(keys->aes_iv, sizeof(keys->aes_iv))){
        perror("failed to generate iv");
        return NULL;
    }; //for generating a random iv

    return keys;
}

int aes_encrypt (const char* packet, unsigned char *aes_key, unsigned char *aes_iv, const unsigned char *cipherpacket){
        EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
        int len, cipherpacket_len;
    
        EVP_EncryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, aes_key, aes_iv);
        EVP_EncryptUpdate(ctx, cipherpacket, &len, packet, BUFFER_SIZE);
        cipherpacket_len = len;
        EVP_EncryptFinal_ex(ctx, cipherpacket + len, &len);
        cipherpacket_len += len;

        EVP_CIPHER_CTX_free(ctx);
        return cipherpacket_len;
}

int aes_decrypt(const unsigned char *cipherpacket, unsigned char *aes_key, unsigned char *aes_iv, int cipherpacket_len, const char *packet) {
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    int len, packet_len;
    
    EVP_DecryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, aes_key, aes_iv);
    EVP_DecryptUpdate(ctx, packet, &len, cipherpacket, cipherpacket_len);
    packet_len = len;
    EVP_DecryptFinal_ex(ctx, packet + len, &len);
    packet_len += len;

    EVP_CIPHER_CTX_free(ctx);
    return packet_len;
}

int send_packet(Communicator* comm, Keys *keys, const char* query) {
    char* destination_ip = inet_ntoa(comm->destination_addr.sin_addr);
    int destination_port = ntohs(comm->destination_addr.sin_port);

    unsigned char cipherpacket[BUFFER_SIZE];

    char packet[BUFFER_SIZE];
    construct_packet(comm, query, packet, BUFFER_SIZE);

    int cipherpacket_len = aes_encrypt(packet, keys->aes_key, keys->aes_key, cipherpacket);

    int result = sendto(comm->sockfd, cipherpacket, cipherpacket_len, 0, (struct sockaddr*)&comm->destination_addr, sizeof(comm->destination_addr));
    if (result < 0) {
        if (errno != EAGAIN && errno != EWOULDBLOCK) {
            perror("Send failed");
        }
        return -1;
    }
    printf("[+] Sent: %s to %s:%d \n", cipherpacket, destination_ip, destination_port);
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

char* receive_packet(Communicator* comm, Keys* keys) {
    struct sockaddr_in sender_addr;
    socklen_t addr_len = sizeof(sender_addr);

    int recv_len = recvfrom(comm->sockfd, comm->recv_buffer, BUFFER_SIZE - 1, 0, (struct sockaddr*)&sender_addr, &addr_len);
    
    if (recv_len <= 0) {
        if (recv_len == -1 && errno != EAGAIN && errno != EWOULDBLOCK) {
            perror("Receive failed");
        }
        return NULL;
    }
    char packet[BUFFER_SIZE];
    
    int cipherpacket_len=aes_decrypt(comm->recv_buffer, keys->aes_key, keys->aes_iv, recv_len, packet);
    comm->recv_buffer[recv_len] = '\0';

    printf("[+] recieved: %s\n", packet);

    
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