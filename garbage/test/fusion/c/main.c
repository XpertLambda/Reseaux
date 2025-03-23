#include "communicator.h"

int main() {
    Communicator* python_communicator = init_communicator(C_PORT1, PYTHON_PORT, LOCALHOST_IP, TRUE, TRUE);
    Communicator* external_communicator = init_communicator(C_PORT2, EXTERNAL_PORT, BROADCAST_IP, TRUE, TRUE);
    
    if (!python_communicator || !external_communicator) {
        fprintf(stderr, "Failed to initialize communicators\n");
        return EXIT_FAILURE;
    }
    
    printf("[+] Starting communication loop (Press Ctrl+C to exit)\n");
    
    while (1) {
        // Receive queries from both communicators
        char* internal_query = receive_query(python_communicator);
        char* external_query = receive_query(external_communicator);
        
        // Process the external query if it exists
        if (external_query != NULL) {
            send_query(python_communicator, external_query);
        }
        
        // Process the internal query if it exists
        if (internal_query != NULL) {
            send_query(external_communicator, internal_query); // Fixed: send the query string
        }
        
        usleep(SLEEP_TIME);
    }
    
    cleanup_communicator(python_communicator);
    cleanup_communicator(external_communicator);
    
    return EXIT_SUCCESS;
}