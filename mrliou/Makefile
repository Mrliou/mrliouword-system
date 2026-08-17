# Mr.liou AI Local Server — Makefile
#
# Build:    make
# Run:      ./mrliou-server          (default port 7890)
#           ./mrliou-server 8080     (custom port)
# Clean:    make clean
# Install:  make install PREFIX=/usr/local

CC      ?= gcc
CFLAGS  := -Wall -Wextra -O2 -std=c99 -I. -D_POSIX_C_SOURCE=200809L
LDFLAGS :=

SRCS := main.c \
        server.c \
        router.c \
        memory.c \
        reasoning.c \
        learning.c \
        growth.c \
        generation.c

OBJS    := $(SRCS:.c=.o)
TARGET  := mrliou-server
PREFIX  ?= /usr/local

.PHONY: all clean install uninstall run

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^
	@echo ""
	@echo "Build complete: ./$(TARGET)"
	@echo "Run with:       ./$(TARGET) [port]"
	@echo ""

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)
	@echo "Cleaned."

install: $(TARGET)
	install -d $(PREFIX)/bin
	install -m 755 $(TARGET) $(PREFIX)/bin/$(TARGET)
	@echo "Installed to $(PREFIX)/bin/$(TARGET)"

uninstall:
	rm -f $(PREFIX)/bin/$(TARGET)

run: $(TARGET)
	./$(TARGET)

# Dependencies (generated manually; use gcc -MM to regenerate)
main.o:       main.c config.h mrliou_defs.h server.h router.h
server.o:     server.c server.h config.h mrliou_defs.h
router.o:     router.c router.h memory.h reasoning.h learning.h growth.h generation.h config.h mrliou_defs.h
memory.o:     memory.c memory.h config.h mrliou_defs.h
reasoning.o:  reasoning.c reasoning.h memory.h config.h mrliou_defs.h
learning.o:   learning.c learning.h memory.h config.h mrliou_defs.h
growth.o:     growth.c growth.h config.h mrliou_defs.h
generation.o: generation.c generation.h memory.h config.h mrliou_defs.h
