import socket
import json
CHUNK_SIZE = 4096
class Client:
    def __init__(self, port):
        self.host = socket.gethostname()
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Client initialized to connect to port {self.port}")

    def start(self):
        try:
            self.client_socket.connect((self.host, self.port))
            print(f"Connected to server on port {self.port}")
            if self.handshake():
                print("Handshake successful, connection is OK")
                return True
            else:
                print("Handshake failed")
                return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def handshake(self):
        try:
            self.client_socket.send("HELLO SERVER".encode('utf-8'))
            data = self.client_socket.recv(CHUNK_SIZE).decode('utf-8')
            print(f"returned data = {data}")
            if data == "HELLO CLIENT":
                self.client_socket.send("OK".encode('utf-8'))    
                return True
        except Exception as e:
            print(f"An error occurred during handshake: {e}")
            return False

    def send_data(self, data):
        try:
            serialized_data = json.dumps(data) + '\n'
            self.client_socket.send(serialized_data.encode('utf-8'))
        except Exception as e:
            print(f"An error occurred while sending data: {e}")
            self.stop()

    def receive_data(self):
        try:
            data = self.client_socket.recv(CHUNK_SIZE).decode('utf-8')
            return json.loads(data)
        except Exception as e:
            print(f"An error occurred while receiving data: {e}")
            self.stop()
            return None

    def stop(self):
        self.client_socket.close()
        print("Client has stopped")
