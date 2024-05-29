#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "Ws2_32.lib")
#define CLOSE_SOCKET closesocket
#define SOCKET_ERROR_CODE WSAGetLastError()
#else
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#define CLOSE_SOCKET close
#define SOCKET_ERROR_CODE errno
#endif

#include "cJSON.h"

#define DEFAULT_PORT 5000
#define BUFFER_SIZE 1024

void error_handling(const char *message) {
    perror(message);
    exit(1);
}

void initialize_winsock() {
#ifdef _WIN32
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        error_handling("WSAStartup() error");
    }
#endif
}

void cleanup_winsock() {
#ifdef _WIN32
    WSACleanup();
#endif
}

int create_socket() {
    int sock = socket(PF_INET, SOCK_STREAM, 0);
    if (sock == -1)
        error_handling("socket() error");
    return sock;
}

void connect_to_server(int sock, const char *server_ip, int port) {
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr(server_ip);
    server_addr.sin_port = htons(port);

    if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) == -1)
        error_handling("connect() error");

    printf("Connected to server %s on port %d\n", server_ip, port);
}

void handle_handshake(int sock) {
    char buffer[BUFFER_SIZE];
    send(sock, "HELLO SERVER", strlen("HELLO SERVER"), 0);
    int str_len = recv(sock, buffer, BUFFER_SIZE - 1, 0);
    if (str_len == -1)
        error_handling("recv() error");
    buffer[str_len] = 0;
    printf("Received handshake response: %s\n", buffer);

    if (strcmp(buffer, "HELLO CLIENT") != 0) {
        error_handling("Handshake failed");
    }
}

void communicate_with_server(int sock) {
    char buffer[BUFFER_SIZE];
    int str_len;

    while (1) {
        printf("Enter JSON data to send to server (or type 'exit' to quit): ");
        fgets(buffer, BUFFER_SIZE, stdin);
        buffer[strcspn(buffer, "\n")] = 0; // Remove trailing newline

        if (strcmp(buffer, "exit") == 0)
            break;

        cJSON *json = cJSON_Parse(buffer);
        if (json == NULL) {
            fprintf(stderr, "Invalid JSON format. Please try again.\n");
            continue;
        }

        char *json_str = cJSON_Print(json);
        send(sock, json_str, strlen(json_str), 0);
        free(json_str);
        cJSON_Delete(json);

        str_len = recv(sock, buffer, BUFFER_SIZE - 1, 0);
        if (str_len == -1)
            error_handling("recv() error");
        buffer[str_len] = 0;

        cJSON *response_json = cJSON_Parse(buffer);
        if (response_json == NULL) {
            fprintf(stderr, "Error parsing JSON response\n");
            continue;
        }

        printf("Received from server: %s\n", cJSON_Print(response_json));
        cJSON_Delete(response_json);
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <server_ip> [port]\n", argv[0]);
        exit(1);
    }

    const char *server_ip = argv[1];
    int port = (argc > 2) ? atoi(argv[2]) : DEFAULT_PORT;

    initialize_winsock();

    int sock = create_socket();
    connect_to_server(sock, server_ip, port);
    handle_handshake(sock);
    communicate_with_server(sock);

    CLOSE_SOCKET(sock);

    cleanup_winsock();

    return 0;
}
