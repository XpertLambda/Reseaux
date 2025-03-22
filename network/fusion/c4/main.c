#include "communicator.h"
#include <time.h>
#include <signal.h>

// Global flag for clean shutdown
volatile sig_atomic_t keep_running = 1;

// Signal handler for clean shutdown
void handle_signal(int sig) {
    keep_running = 0;
    printf("\n[!] Received signal %d, shutting down gracefully...\n", sig);
}

int main() {
    // Set up signal handlers for clean shutdown
    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);
    
    // Initialize communicators
    Communicator* python_communicator = init_communicator(C_PORT1, PYTHON_PORT, LOCALHOST_IP, TRUE, TRUE);
    Communicator* external_communicator = init_communicator(C_PORT2, EXTERNAL_PORT, "192.168.1.120", TRUE, TRUE);
    
    if (!python_communicator || !external_communicator) {
        fprintf(stderr, "Failed to initialize communicators\n");
        return EXIT_FAILURE;
    }
    
    printf("[+] Starting communication loop (Press Ctrl+C to exit)\n");
    
    // Variables to track packet statistics
    int sent_packets = 0;
    int received_packets = 0;
    time_t last_stats_time = time(NULL);
    time_t rate_adjust_time = time(NULL);
    
    // Main communication loop
    while (keep_running) {
        // Get current time
        time_t current_time = time(NULL);
        
        // Receive queries from both communicators
        char* internal_query = receive_packet(python_communicator);
        char* external_query = receive_packet(external_communicator);
        
        // Process internal queries
        if (internal_query != NULL) {
            received_packets++;
            printf("[RECEIVED INTERNAL]: %s\n", internal_query);
            
            // Send to external destination
            if (send_packet(external_communicator, internal_query) > 0) {
                sent_packets++;
            }
        }
        
        // Process external queries
        if (external_query != NULL) {
            received_packets++;
            printf("[RECEIVED EXTERNAL]: %s\n", external_query);
            
            // Send to python
            if (send_packet(python_communicator, external_query) > 0) {
                sent_packets++;
            }
        }
        
        // Print statistics every second
        if (current_time - last_stats_time >= 1) {
            printf("[STATS] Sent: %d packets/sec | Received: %d packets/sec | "
                   "Int Loss: %d | Ext Loss: %d | Rate: %lu µs/packet\n", 
                   sent_packets, received_packets,
                   python_communicator->packets_lost,
                   external_communicator->packets_lost,
                   external_communicator->send_rate_limit);
            
            // Reset counters and update the time
            sent_packets = 0;
            received_packets = 0;
            last_stats_time = current_time;
        }
        
        // Adjust send rates every 5 seconds based on packet loss
        if (current_time - rate_adjust_time >= 5) {
            adjust_send_rate(python_communicator);
            adjust_send_rate(external_communicator);
            rate_adjust_time = current_time;
        }
        
        // Sleep to prevent CPU hogging
        usleep(SLEEP_TIME);
    }
    
    // Clean shutdown
    printf("[+] Shutting down communicators...\n");
    cleanup_communicator(python_communicator);
    cleanup_communicator(external_communicator);
    
    return EXIT_SUCCESS;
}