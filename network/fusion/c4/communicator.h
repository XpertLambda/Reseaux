#ifndef COMMUNICATOR_H
#define COMMUNICATOR_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <netinet/in.h>
#include <time.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <stdint.h>

#define TRUE 1
#define FALSE 0
#define ID_SIZE 10
#define SEPARATOR ':'
#define BUFFER_SIZE 1472  // Optimized for Ethernet MTU (1500) - IP header (20) - UDP header (8)
#define RCVBUF_SIZE 10485760  // ~10MB
#define SNDBUF_SIZE 10485760  // ~10MB
#define FLAGS 0
#define SLEEP_TIME 1000      // Microseconds between main loop iterations

// Rate limiting constants
#define DEFAULT_SEND_RATE 1000   // Microseconds between packets (1ms)
#define MIN_SEND_RATE 500        // Minimum time between packets (0.5ms)
#define MAX_SEND_RATE 10000      // Maximum time between packets (10ms)
#define RATE_INCREASE_STEP 500   // How much to increase delay when packet loss detected
#define RATE_DECREASE_STEP 50    // How much to decrease delay when no packet loss

// Port definitions
#define PYTHON_PORT 50000
#define C_PORT1 50001
#define C_PORT2 50002
#define EXTERNAL_PORT 50002

#define LOCALHOST_IP "127.0.0.1"
#define BROADCAST_IP "255.255.255.255"

typedef struct {
    int sockfd;                         
    struct sockaddr_in destination_addr;
    struct sockaddr_in listener_addr;   
    char recv_buffer[BUFFER_SIZE];
    char instance_id[ID_SIZE];
    
    // Sequence tracking
    int send_seq;          // Next sequence number to send
    int last_recv_seq;     // Last sequence number received
    int packets_lost;      // Count of detected lost packets
    
    // Rate limiting
    uint64_t last_send_time;   // Last time we sent a packet
    uint64_t send_rate_limit;  // Microseconds between packets
} Communicator;

// Function prototypes
void generate_instance_id(Communicator* comm);
Communicator* init_communicator(int listener_port, int destination_port, const char* destination_addr, int REUSEADDR_FLAG, int BROADCAST_FLAG);
void construct_packet(Communicator* comm, const char* query, char* packet, size_t packet_size);
uint64_t current_time_micros();
int send_packet(Communicator* comm, const char* message);
char* process_packet(char* packet, char* packet_id, int* seq_num);
void log_message(const char* message, const struct sockaddr_in* sender_addr, const char* packet_id, int seq_num);
char* receive_packet(Communicator* comm);
void adjust_send_rate(Communicator* comm);
void cleanup_communicator(Communicator* comm);

#endif // COMMUNICATOR_H