#include "communicator.h"

void init_key_and_iv(unsigned char *key, unsigned char *iv) {
    // Générer une clé aléatoire
    if (!RAND_bytes(key, KEY_SIZE)) {
        perror("Erreur lors de la génération de la clé");
    }
    // Générer un vecteur d'initialisation (IV) aléatoire
    if (!RAND_bytes(iv, IV_SIZE)) {
        perror("Erreur lors de la génération du vecteur d'initialisation");
    }
}

// Fonction de chiffrement
int encrypt_message(const unsigned char *plaintext, int plaintext_len, unsigned char *key, unsigned char *iv, unsigned char *ciphertext) {
    EVP_CIPHER_CTX *ctx;
    int len;
    int ciphertext_len;

    if (!(ctx = EVP_CIPHER_CTX_new())) {
        perror("EVP_CIPHER_CTX_new failed");
        return -1;
    }

    if (EVP_EncryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, key, iv) != 1) {
        perror("EVP_EncryptInit_ex failed");
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }

    if (EVP_EncryptUpdate(ctx, ciphertext, &len, plaintext, plaintext_len) != 1) {
        perror("EVP_EncryptUpdate failed");
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }
    ciphertext_len = len;

    if (EVP_EncryptFinal_ex(ctx, ciphertext + len, &len) != 1) {
        perror("EVP_EncryptFinal_ex failed");
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }
    ciphertext_len += len;

    EVP_CIPHER_CTX_free(ctx);
    return ciphertext_len;
}

int decrypt_message(const unsigned char *ciphertext, int ciphertext_len, unsigned char *key, unsigned char *iv, unsigned char *plaintext) {
    EVP_CIPHER_CTX *ctx;
    int len;
    int plaintext_len;

    if (!(ctx = EVP_CIPHER_CTX_new())) {
        perror("EVP_CIPHER_CTX_new failed");
        return -1;
    }

    if (EVP_DecryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, key, iv) != 1) {
        perror("EVP_DecryptInit_ex failed");
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }

    if (EVP_DecryptUpdate(ctx, plaintext, &len, ciphertext, ciphertext_len) != 1) {
        perror("EVP_DecryptUpdate failed");
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }
    plaintext_len = len;

    if (EVP_DecryptFinal_ex(ctx, plaintext + len, &len) != 1) {
        perror("EVP_DecryptFinal_ex failed");
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }
    plaintext_len += len;

    EVP_CIPHER_CTX_free(ctx);
    return plaintext_len;
}

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
    unsigned char encrypted_message[BUFFER_SIZE];
    unsigned char key[KEY_SIZE];  // Clé de chiffrement
    unsigned char iv[IV_SIZE];    // IV (vecteur d'initialisation)
    
    // Initialiser la clé et l'IV avec des valeurs adaptées (fixes ou générées)
    init_key_and_iv(key, iv);

    // Chiffrement du message
    int encrypted_len = encrypt_message((unsigned char*)query, strlen(query), key, iv, encrypted_message);
    if (encrypted_len <= 0) {
        perror("Error encrypting message");
        return -1;
    }
    
    char* destination_ip = inet_ntoa(comm->destination_addr.sin_addr);
    int destination_port = ntohs(comm->destination_addr.sin_port);
    
    int result = sendto(comm->sockfd, encrypted_message, encrypted_len, 0, 
                        (struct sockaddr*)&comm->destination_addr, sizeof(comm->destination_addr));
    if (result < 0) {
        if (errno != EAGAIN && errno != EWOULDBLOCK) {
            perror("Send failed");
        }
        return -1;
    }
    printf("[+] Sent encrypted message to %s:%d \n", destination_ip, destination_port);
    return result;
}


char* receive_query(Communicator* comm) {
    struct sockaddr_in sender_addr;
    socklen_t addr_len = sizeof(sender_addr);
    memset(comm->recv_buffer, 0, BUFFER_SIZE);  // Initialisation du buffer

    // Réception du message UDP
    int recv_len = recvfrom(comm->sockfd, comm->recv_buffer, BUFFER_SIZE - 1, 0, 
                            (struct sockaddr*)&sender_addr, &addr_len);

    if (recv_len > 0) {
        comm->recv_buffer[recv_len] = '\0';  // Ajouter une terminaison nulle

        unsigned char decrypted_text[BUFFER_SIZE] = {0};  // Buffer pour le texte décrypté
        unsigned char key[KEY_SIZE];  // Clé de déchiffrement
        unsigned char iv[IV_SIZE];    // IV

        // Initialiser la clé et l'IV avec des valeurs adaptées
        init_key_and_iv(key, iv);

        // Décryptage du message reçu
        int decrypted_len = decrypt_message((unsigned char*)comm->recv_buffer, recv_len, 
                                            key, iv, decrypted_text);

        if (decrypted_len <= 0) {
            printf("[-] Erreur lors du décryptage du message.\n");
            return NULL;
        }

        // Copier le texte décrypté dans le buffer de réception
        strncpy(comm->recv_buffer, (char*)decrypted_text, decrypted_len);
        comm->recv_buffer[decrypted_len] = '\0';  // Terminaison nulle

        // Vérification du préfixe ID dans le message
        char* colon = strchr(comm->recv_buffer, ':');
        if (colon && (size_t)(colon - comm->recv_buffer) < ID_SIZE) {
            char msg_id[ID_SIZE];
            size_t id_len = (size_t)(colon - comm->recv_buffer);
            strncpy(msg_id, comm->recv_buffer, id_len);
            msg_id[id_len] = '\0';  // Assurer la terminaison

            // Vérifier si c'est un message de cette instance
            if (strcmp(msg_id, comm->instance_id) == 0) {
                printf("[*] Ignoré : message de notre propre instance avec ID %s\n", msg_id);
                return NULL;  // Ignorer le message propre
            }

            // Déplacement du contenu du message sans l'ID
            char* message_content = colon + 1;
            memmove(comm->recv_buffer, message_content, strlen(message_content) + 1);
            printf("[+] Message reçu : %s de %s:%d (ID expéditeur : %s)\n",
                   comm->recv_buffer, inet_ntoa(sender_addr.sin_addr), ntohs(sender_addr.sin_port), msg_id);
            return comm->recv_buffer;
        } else {
            // Si le message n'a pas un format ID valide
            printf("[+] Message sans format ID valide : %s de %s:%d\n", comm->recv_buffer,
                   inet_ntoa(sender_addr.sin_addr), ntohs(sender_addr.sin_port));
            return comm->recv_buffer;  // Retourner le message brut
        }
    } else if (recv_len == -1 && errno != EAGAIN && errno != EWOULDBLOCK) {
        perror("Échec de la réception");
    }
    return NULL;  // Aucun message reçu ou erreur temporaire
}




void cleanup_communicator(Communicator* comm) {
    if (comm) {
        close(comm->sockfd);
        free(comm);
        printf("[+] Communicator cleaned up\n");
    }
}