#include "communicator.h"

int main() {
    Communicator* python_communicator = init_communicator(C_PORT1, PYTHON_PORT, LOCALHOST_IP, TRUE, TRUE);
    Communicator* external_communicator = init_communicator(C_PORT2, EXTERNAL_PORT, BROADCAST_IP, TRUE, TRUE);
    
    if (!python_communicator || !external_communicator) {
        fprintf(stderr, "Failed to initialize communicators\n");
        return EXIT_FAILURE;
    }
    
    printf("[+] Starting communication loop (Press Ctrl+C to exit)\n");
    
    // Variables to track packet statistics
    int internal_total_recieve = 0;
    int external_total_recieve = 0;
    int internal_total_sent = 0;
    int external_total_sent = 0;
    
    int packetlost = 0;

    while (1) {
        // Receive queries from both communicators
        char* internal_query = receive_packet(python_communicator);
        char* external_query = receive_packet(external_communicator);
        
        // Count received packets
        if (internal_query != NULL) {
            //printf("[Rvd PACKET]: %s | [RvdIntPackets]: %d",internal_query, internal_total_recieve);
            internal_total_recieve++;
            if(atoi(internal_query) - packetlost != internal_total_recieve){
                packetlost++;
            }
            //printf(" | Packet Loss : %d \n", packetlost);              
        }
        if (external_query != NULL) {
            external_total_recieve++;
            //printf("[Rvd PACKET]: %s | [RvdExtPackets]: %d",external_query, external_total_recieve);
            if(atoi(external_query) - packetlost != external_total_recieve){
                packetlost++;             
            }
            //printf(" | Packet Loss : %d \n", packetlost); 
        }
        
        // Process the external query if it exists
        if (external_query != NULL) {
            send_packet(python_communicator, external_query);
            internal_total_sent++;
            //printf("[SNT PACKET]: %s | [SntIntPackets]: %d \n",external_query, internal_total_sent);
        }
        
        // Process the internal query if it exists
        if (internal_query != NULL) {
            send_packet(external_communicator, internal_query);
            external_total_sent++;
            //printf("[SNT PACKET]: %s | [SntExtPackets]: %d \n",internal_query, external_total_sent);
        }

        if(packetlost) printf("LOSS : %d\n", packetlost);
        usleep(SLEEP_TIME);
    }
    
    cleanup_communicator(python_communicator);
    cleanup_communicator(external_communicator);
    
    return EXIT_SUCCESS;
}