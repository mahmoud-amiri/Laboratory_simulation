// server.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define CHUNK_SIZE 1024

int server_socket, client_socket;
struct sockaddr_in server_addr, client_addr;

void start_server(int port) {
    server_socket = socket(AF_INET, SOCK_STREAM, 0);
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);

    bind(server_socket, (struct sockaddr*)&server_addr, sizeof(server_addr));
    listen(server_socket, 1);
    int addrlen = sizeof(client_addr);
    client_socket = accept(server_socket, (struct sockaddr*)&client_addr, (socklen_t*)&addrlen);
}

void stop_server() {
    close(client_socket);
    close(server_socket);
}

void send_data(const char* data) {
    send(client_socket, data, strlen(data), 0);
}

void receive_data(char* buffer) {
    recv(client_socket, buffer, CHUNK_SIZE, 0);
}
