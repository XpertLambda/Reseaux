CC = gcc
CFLAGS = -Wall -Wextra -std=c99
OBJ_RECV = recv_action.o
OBJ_SEND = send_action.o
HEADER = action_connection.h

# Compilation de recv_action
recv_action: $(OBJ_RECV)
	$(CC) -o recv_action $(OBJ_RECV)

# Compilation de send_action
send_action: $(OBJ_SEND)
	$(CC) -o send_action $(OBJ_SEND)

# Compilation des fichiers .c en .o
%.o: %.c $(HEADER)
	$(CC) $(CFLAGS) -c $< -o $@

# Nettoyage des fichiers objets et exécutables
clean:
	rm -f *.o recv_action send_action
