CC = gcc
CFLAGS = -Wall -Wextra -O2
TARGET = CCommunicator

SRCS = main.c CCommunicator.c
OBJS = $(SRCS:.c=.o)
DEPS = CCommunicator.h

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^

%.o: %.c $(DEPS)
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all clean
