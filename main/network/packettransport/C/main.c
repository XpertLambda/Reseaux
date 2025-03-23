#include "communicator.h"
#include <unistd.h> // For sleep function
#include <time.h>   // For time tracking

int main() {
    Communicator* python_communicator = init_communicator(C_PORT1, PYTHON_PORT, LOCALHOST_IP);
    Communicator* external_communicator = init_communicator(C_PORT2, EXTERNAL_PORT, BROADCAST_IP);

    if (!python_communicator || !external_communicator) {
        fprintf(stderr, "Failed to initialize communicators\n");
        return EXIT_FAILURE;
    }

    printf("[+] Starting communication loop (Press Ctrl+C to exit)\n");

    // Variables to track packet statistics
    int internal_total_receive = 0;
    int external_total_receive = 0;
    int internal_total_sent = 0;
    int external_total_sent = 0;
    int internal_packet_lost = 0;
    int external_packet_lost = 0;

    double internal_total_size = 0.0;
    double external_total_size = 0.0;

    time_t last_time = time(NULL);

    while (1) {
        // Receive queries from both communicators
        char* internal_query = receive_packet(python_communicator);
        char* external_query = receive_packet(external_communicator);

        // Count received packets and track size in KB
        if (internal_query != NULL) {
            internal_total_receive++;
            double size_kb = (double)strlen(internal_query) / 1024;  // Changed from MB to KB
            internal_total_size += size_kb;

            if (atoi(internal_query) - internal_packet_lost != internal_total_receive) {
                internal_packet_lost++;
            }
        }
        if (external_query != NULL) {
            external_total_receive++;
            double size_kb = (double)strlen(external_query) / 1024;  // Changed from MB to KB
            external_total_size += size_kb;

            if (atoi(external_query) - external_packet_lost != external_total_receive) {
                external_packet_lost++;
            }
        }

        // Process the external query if it exists
        if (external_query != NULL) {
            send_packet(python_communicator, external_query);
            internal_total_sent++;
        }

        // Process the internal query if it exists
        if (internal_query != NULL) {
            send_packet(external_communicator, internal_query);
            external_total_sent++;
        }

        // Check if 1 second has passed
        time_t current_time = time(NULL);
        if (difftime(current_time, last_time) >= 1.0) {
            double internal_loss_percentage = (internal_total_receive + internal_packet_lost) == 0 ? 0.0 : 
                (double)internal_packet_lost / (internal_total_receive + internal_packet_lost) * 100.0;

            double external_loss_percentage = (external_total_receive + external_packet_lost) == 0 ? 0.0 : 
                (double)external_packet_lost / (external_total_receive + external_packet_lost) * 100.0;

            double internal_avg_size = internal_total_receive == 0 ? 0.0 : internal_total_size / internal_total_receive;
            double external_avg_size = external_total_receive == 0 ? 0.0 : external_total_size / external_total_receive;

            printf("[Packet Loss] External -> Sent: %d, Received: %d, Lost: %d (%.2f%%), Avg Size: %.2f KB\n", external_total_sent, external_total_receive, external_packet_lost, external_loss_percentage, external_avg_size);

            last_time = current_time;
        }

        usleep(SLEEP_TIME);
    }

    cleanup_communicator(python_communicator);
    cleanup_communicator(external_communicator);

    return EXIT_SUCCESS;
}
