CC = gcc
CFLAGS = -Wall -Wextra -Werror
SRC = peer_client.c send_action.c recv_action.c
TARGET = peer_client

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC)

clean:
	rm -f $(TARGET)

re: clean all
