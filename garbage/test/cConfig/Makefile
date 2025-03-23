CC = gcc
CFLAGS = -Wall -Wextra -O2
TARGET = CythonCommunicator

SRCS = main.c CythonCommunicator.c
OBJS = $(SRCS:.c=.o)
DEPS = CythonCommunicator.h

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^

%.o: %.c $(DEPS)
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all clean
