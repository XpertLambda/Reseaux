CC = gcc
CFLAGS = -Wall -Wextra -O2 $(shell pkg-config --cflags openssl)
LDLIBS = $(shell pkg-config --libs openssl)
TARGET = communicator

SRCS = communicator.c main.c
OBJS = $(SRCS:.c=.o)
DEPS = communicator.h

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDLIBS)

%.o: %.c $(DEPS)
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all clean
