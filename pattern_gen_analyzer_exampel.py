import json
import sys
import os
from math import ceil

sys.path.append(os.path.join(os.path.dirname(__file__), '../submodules'))
from submodules.socket.python.server import Server

CHUNK_SIZE = 1024  # Size of each chunk in bytes

class EnhancedServer(Server):
    def send_large_data(self, data):
        serialized_data = json.dumps(data)
        num_chunks = ceil(len(serialized_data) / CHUNK_SIZE)
        for i in range(num_chunks):
            chunk = serialized_data[i * CHUNK_SIZE:(i + 1) * CHUNK_SIZE]
            self.send_data({"chunk": chunk, "index": i, "total": num_chunks})

    def receive_large_data(self):
        partial_data = {}
        total_chunks = {}
        received_chunks = {}
        
        while True:
            chunk = self.receive_data()
            if chunk:
                chunk_data = chunk["chunk"]
                index = chunk["index"]
                total = chunk["total"]

                if index == 0:
                    partial_data[chunk["name"]] = chunk_data
                    received_chunks[chunk["name"]] = 1
                    total_chunks[chunk["name"]] = total
                else:
                    partial_data[chunk["name"]] += chunk_data
                    received_chunks[chunk["name"]] += 1

                if received_chunks[chunk["name"]] == total_chunks[chunk["name"]]:
                    complete_data = partial_data.pop(chunk["name"])
                    received_chunks.pop(chunk["name"])
                    total_chunks.pop(chunk["name"])
                    return json.loads(complete_data)

def communicate(server_gen, server_analyzer):
    try:
        print("Initializing communication between servers")

        config_gen = {
            "command": "CONFIG",
            "data": [
                {
                    "type": "SOLID_COLOR",
                    "name": "solid_color1",
                    "color": [255, 0, 0],
                    "width": 640,
                    "height": 480,
                    "duration": 10,
                    "frame_rate": 30
                },
                {
                    "type": "CHECKERBOARD",
                    "name": "checkerboard1",
                    "width": 640,
                    "height": 480,
                    "square_size": 50,
                    "duration": 10,
                    "frame_rate": 30
                }
            ]
        }

        config_analyzer = {
            "command": "CONFIG",
            "data": [
                {"name": "solid_color1"},
                {"name": "checkerboard1"}
            ]
        }

        # Send configuration to the pattern generator
        server_gen.send_large_data(config_gen)
        print("Config sent to pattern generator")
        data_gen = server_gen.receive_large_data()
        if data_gen["config"] == "OK":
            print("Pattern generator configured successfully")

        # Send configuration to the video analyzer
        server_analyzer.send_large_data(config_analyzer)
        print("Config sent to video analyzer")
        data_analyzer = server_analyzer.receive_large_data()
        if data_analyzer["config"] == "OK":
            print("Video analyzer configured successfully")

        for _ in range(20):  # or while True:
            for name in ["solid_color1", "checkerboard1"]:
                frame_req = {"command": "GET_FRAME", "name": name}
                server_gen.send_large_data(frame_req)
                data_gen = server_gen.receive_large_data()
                if data_gen and data_gen["frame"] is not None:
                    frame_data = {
                        "name": name,
                        "frame": data_gen["frame"]
                    }
                    server_analyzer.send_large_data(frame_data)
                    data_analyzer = server_analyzer.receive_large_data()
                    if data_analyzer["response"] == "FRAME_OK":
                        print(f"Frame for {name} processed by analyzer")
    except json.JSONDecodeError as json_err:
        print(f"JSON decode error: {json_err}")
    except Exception as e:
        print(f"An error occurred during communication: {e}")
    finally:
        server_gen.stop()
        server_analyzer.stop()

if __name__ == "__main__":
    with open('port_config.json', 'r') as f:
        config = json.load(f)
    port_gen = config["port_pattern_gen"]
    port_analyzer = config["port_analyzer"]

    server_gen = EnhancedServer(port_gen)
    server_analyzer = EnhancedServer(port_analyzer)

    try:
        server_analyzer.start()
        print("Video analyzer server started")
        server_gen.start()
        print("Pattern generator server started")
        communicate(server_gen, server_analyzer)
    except KeyboardInterrupt:
        server_gen.stop()
        server_analyzer.stop()
        print("Servers stopped by user")
