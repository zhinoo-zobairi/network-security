#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define PORT 3490
#define BACKLOG 10
#define BUF_SIZE 1024

void handle_request(const char* buffer, int socket, size_t received_len) {
    uint8_t claimed_len = buffer[0];
    size_t actual_len = received_len - 1; // exclude the length byte itself

    // Validate: never send back more than we actually received
    uint8_t safe_len = claimed_len <= actual_len ? claimed_len : actual_len;

    char* reply = malloc(2 + safe_len); // 'Z' + length + data
    if (!reply) return;

    reply[0] = 'Z';
    reply[1] = safe_len;
    memcpy(reply + 2, buffer + 1, safe_len); // skip length byte

    send(socket, reply, 2 + safe_len, 0);
    free(reply);
}

int main() {
    int sock_fd = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in addr = {0};

    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(PORT);

    bind(sock_fd, (struct sockaddr*)&addr, sizeof(addr));
    listen(sock_fd, BACKLOG);

    printf("Server running on port %d...\n", PORT);

    while (1) {
        int client_fd = accept(sock_fd, NULL, NULL);
        char buffer[BUF_SIZE];
        char byte;
        size_t i = 0;

        while (i < BUF_SIZE && byte != 'X') {
            recv(client_fd, &byte, 1, 0);
            buffer[i++] = byte;
        }

        if (byte == 'X' && i > 1) {
            handle_request(buffer, client_fd, i - 1); // exclude 'X'
        }

        close(client_fd);
    }

    return 0;
}