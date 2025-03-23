CC = gcc
CFLAGS = -Wall -Wextra -O2
TARGET = communicator

SRCS = main.c communicator.c
OBJS = $(SRCS:.c=.o)
DEPS = communicator.h

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^

%.o: %.c $(DEPS)
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all clean
