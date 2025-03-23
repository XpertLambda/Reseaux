#include "CythonCommunicator.h"

int main() {
    CythonCommunicator* comm = init_communicator(C_PORT, PYTHON_PORT, LOCALHOST);
    if (!comm) {
        fprintf(stderr, "Failed to initialize communicator\n");
        return EXIT_FAILURE;
    }

    printf("[+] Starting communication loop (Press Ctrl+C to exit)\n");

    while (1) {
        receive_message(comm);
        send_message(comm, "message from C");
        usleep(SLEEP_TIME);
    }

    // Clean up (this part won't be reached due to infinite loop)
    cleanup_communicator(comm);
    return EXIT_SUCCESS;
}
