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

int create_server_socket() {
    int server_sock = socket(PF_INET, SOCK_STREAM, 0);
    if (server_sock == -1)
        error_handling("socket() error");
    return server_sock;
}

void bind_socket(int server_sock, int port) {
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(port);

    if (bind(server_sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) == -1)
        error_handling("bind() error");

    printf("Socket bound to port %d\n", port);
}

void listen_socket(int server_sock) {
    if (listen(server_sock, 5) == -1)
        error_handling("listen() error");

    printf("Listening on socket\n");
}

int accept_connection(int server_sock) {
    struct sockaddr_in client_addr;
    socklen_t client_addr_size = sizeof(client_addr);
    int client_sock = accept(server_sock, (struct sockaddr *)&client_addr, &client_addr_size);
    if (client_sock == -1)
        error_handling("accept() error");

    printf("Client connected\n");
    return client_sock;
}

void handle_handshake(int client_sock) {
    char buffer[BUFFER_SIZE];
    int str_len = recv(client_sock, buffer, BUFFER_SIZE - 1, 0);
    if (str_len == -1)
        error_handling("recv() error");
    buffer[str_len] = 0;
    printf("Received handshake: %s\n", buffer);

    if (strcmp(buffer, "HELLO SERVER") == 0) {
        send(client_sock, "HELLO CLIENT", strlen("HELLO CLIENT"), 0);
    } else {
        error_handling("Handshake failed");
    }
}

void handle_client(int client_sock) {
    char buffer[BUFFER_SIZE];
    int str_len;

    while (1) {
        str_len = recv(client_sock, buffer, BUFFER_SIZE - 1, 0);
        if (str_len == -1) {
            perror("recv() error");
            break;
        }
        if (str_len == 0) { // Connection closed by client
            printf("Client disconnected\n");
            break;
        }
        buffer[str_len] = 0;

        printf("Received data: %s\n", buffer);

        cJSON *received_json = cJSON_Parse(buffer);
        if (received_json == NULL) {
            fprintf(stderr, "Error parsing JSON\n");
            continue;
        }

        printf("Parsed JSON from client: %s\n", cJSON_Print(received_json));

        cJSON *response_json = cJSON_CreateObject();
        cJSON_AddStringToObject(response_json, "message", "Data received");
        cJSON_AddItemToObject(response_json, "received_data", received_json);

        char *response_str = cJSON_Print(response_json);
        send(client_sock, response_str, strlen(response_str), 0);

        printf("Sent response: %s\n", response_str);

        cJSON_Delete(response_json);
        free(response_str);
    }
}

int main(int argc, char *argv[]) {
    int port = (argc > 1) ? atoi(argv[1]) : DEFAULT_PORT;

    initialize_winsock();

    int server_sock = create_server_socket();
    bind_socket(server_sock, port);
    listen_socket(server_sock);

    int client_sock = accept_connection(server_sock);
    handle_handshake(client_sock);
    handle_client(client_sock);

    CLOSE_SOCKET(client_sock);
    CLOSE_SOCKET(server_sock);

    cleanup_winsock();

    return 0;
}
