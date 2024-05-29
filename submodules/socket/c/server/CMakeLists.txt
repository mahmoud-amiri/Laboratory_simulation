cmake_minimum_required(VERSION 3.10)
project(serverSocket)

set(CMAKE_C_STANDARD 99)

# Find cJSON package
find_path(CJSON_INCLUDE_DIR cjson/cJSON.h)
find_library(CJSON_LIBRARY cjson)

if (CJSON_INCLUDE_DIR AND CJSON_LIBRARY)
    set(CJSON_FOUND TRUE)
else ()
    set(CJSON_FOUND FALSE)
endif ()

if (CJSON_FOUND)
    include_directories(${CJSON_INCLUDE_DIR})
    message(STATUS "Found cJSON in ${CJSON_INCLUDE_DIR}")
else ()
    message(FATAL_ERROR "Could not find cJSON")
endif ()

# Add executable
add_executable(server_socket server_socket.c)

# Link libraries based on the operating system
if (WIN32)
    target_link_libraries(server_socket PRIVATE ${CJSON_LIBRARY} ws2_32)
else ()
    target_link_libraries(server_socket PRIVATE ${CJSON_LIBRARY})
endif ()
