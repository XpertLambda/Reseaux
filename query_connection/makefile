CC = gcc
CFLAGS = -Wall -Wextra 
OBJ = peer_client.o send_action.o recv_action.o
TARGET = peer_client

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJ)

peer_client.o: peer_client.c action_connection.h
	$(CC) $(CFLAGS) -c peer_client.c

send_action.o: send_action.c action_connection.h
	$(CC) $(CFLAGS) -c send_action.c

recv_action.o: recv_action.c action_connection.h
	$(CC) $(CFLAGS) -c recv_action.c

clean:
	rm -f $(OBJ) $(TARGET)
