#include "CCommunicator.h"

int main() {
    CCommunicator* comm = init_C_communicator(C_PORT2, EXTERNAL_PORT, BROADCAST);
    if (!comm) {
        fprintf(stderr, "Failed to initialize communicator\n");
        return EXIT_FAILURE;
    }

    char input_buffer[ACTION_LEN];
    int stdin_fd = fileno(stdin);
    
    //Non-blocking listener
    int flags = fcntl(stdin_fd, F_GETFL, 0);
    fcntl(stdin_fd, F_SETFL, flags | O_NONBLOCK);

    printf("[+] Starting communication loop (Press Ctrl+C to exit)\n");
    printf("[+] Type a message and press Enter to send\n");

    while (1) {
        receive_message(comm);
        memset(input_buffer, 0, ACTION_LEN);
        if (fgets(input_buffer, ACTION_LEN, stdin) != NULL) {
            input_buffer[strcspn(input_buffer, "\n")] = '\0';
            if (strlen(input_buffer) > 0) {
                send_to_external(comm, input_buffer);
            }
        }
        usleep(SLEEP_TIME);
    }

    cleanup_communicator(comm);
    return EXIT_SUCCESS;
}