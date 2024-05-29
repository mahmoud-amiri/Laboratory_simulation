# Socket Communication Project

This repository contains a client-server application for socket communication using C/python and the cJSON library for JSON parsing. The project is designed to demonstrate basic socket programming, including establishing connections, performing handshakes, and sending/receiving JSON data.

## Table of Contents
- [Socket Communication Project](#socket-communication-project)
  - [Table of Contents](#table-of-contents)
  - [Project Overview](#project-overview)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Installation](#installation)
    - [Linux](#linux)
    - [Windows](#windows)
  - [Usage](#usage)
    - [Building the Project](#building-the-project)
      - [Linux](#linux-1)
      - [Windows](#windows-1)
    - [Running the Application](#running-the-application)
  - [Contributing](#contributing)
  - [License](#license)

## Project Overview

The project consists of two main components:

- **Client**: Connects to the server, sends JSON data, and receives responses.
- **Server**: Accepts connections from clients, processes JSON data, and sends responses.

## Features

- Establishes TCP connections between client and server.
- Handshaking mechanism to verify connections.
- JSON data parsing and handling using the cJSON library.
- Cross-platform support for both Windows and Linux.

## Requirements

- GCC or any C compiler
- CMake
- cJSON library

## Installation

### Linux

1. **Install Dependencies**:

    ```sh
    sudo apt update
    sudo apt install -y gcc cmake libcjson-dev
    ```

    or

    ```sh
        cd c
        chmod +x install_json.sh
        ./install_json.sh
    ```

2. **Clone the Repository**:

    ```sh
    git clone https://github.com/mahmoud-amiri/socket.git
    cd socket
    ```

### Windows

1. **Install Dependencies**:
    - Download and install [MinGW](http://www.mingw.org/)
    - Download and install [CMake](https://cmake.org/download/)

2. **Clone the Repository**:

    ```sh
    git clone https://github.com/mahmoud-amiri/socket.git
    cd socket
    ```

## Usage

### Building the Project

To build the project, you can use the provided `build.sh` script for Linux or manually use CMake for both Linux and Windows.

#### Linux

1. **Make the build script executable**:

    ```sh
    chmod +x build.sh
    ```

2. **Run the build script**:

    ```sh
    ./build.sh
    ```

#### Windows

Use CMake from the command prompt:

1. **Navigate to the client directory**:

    ```sh
    cd c/client
    ```

2. **Create a build directory and run CMake**:

    ```sh
    mkdir build
    cd build
    cmake ..
    cmake --build .
    ```

3. **Repeat for the server directory**:

    ```sh
    cd ../../server
    mkdir build
    cd build
    cmake ..
    cmake --build .
    ```

### Running the Application

1. **Start the Server**:
    Navigate to the server build directory and run the server executable:

    ```sh
    ./server/build/server_socket [port]
    ```

2. **Start the Client**:
    Navigate to the client build directory and run the client executable with the server's IP and port:

    ```sh
    ./client/build/client_socket <server_ip> [port]
    ```

    Replace `<server_ip>` with the IP address of the server (e.g., `127.0.0.1` for localhost) and `[port]` with the server port (default is 5000).

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
