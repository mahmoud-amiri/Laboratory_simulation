import json
import sys
import os
from math import ceil

sys.path.append(os.path.join(os.path.dirname(__file__), '../submodules'))
from submodules.socket.python.server import Server

CHUNK_SIZE = 1024  # Size of each chunk in bytes
VIDEO_WIDTH = 100
VIDEO_HEIGHT = 100
class EnhancedServer(Server):
    def send_large_data(self, data):
        serialized_data = json.dumps(data)
        print(f"len(serialized_data) = {len(serialized_data)}")
        num_chunks = ceil(len(serialized_data) / CHUNK_SIZE)
        print(f"num_chunks = {num_chunks}")
        for i in range(num_chunks):
            chunk = serialized_data[i * CHUNK_SIZE:(i + 1) * CHUNK_SIZE]
            self.send_data({"chunk": chunk, "index": i, "total": num_chunks})
            print(f"chunk number {i} is sent")
            data = self.receive_data()
            print(f"server answered : {data}")


    def receive_large_data(self, max_attempts=100000):
        partial_data = ""
        attempts = 0

        while attempts < max_attempts:
            print(f"attempts = {attempts}")
            chunk = self.receive_data()
            if chunk:
                chunk_data = chunk.get("chunk", "")
                index = chunk.get("index", 0)
                total = chunk.get("total", 0)
                self.send_data({"data": f" chunk {index}/{total-1} received successfully"}) 
                print(f"index = {index} / total = {total-1}")
                partial_data += chunk_data

                if index + 1 == total:
                    print("Last chunk received")
                    # Last chunk received
                    try:
                        return json.loads(partial_data)
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse complete data: {e}")
                        return None
            attempts += 1

        raise TimeoutError("Failed to receive all chunks within the maximum number of attempts")


def communicate(server_gen, server_analyzer):
    try:
        print("Initializing communication between servers")

        config_gen = {
            "command": "CONFIG",
            "data": [
                # {
                #     "type": "SOLID_COLOR",
                #     "name": "solid_color1",
                #     "color": [255, 0, 0],
                #     "width": VIDEO_WIDTH,
                #     "height": VIDEO_HEIGHT,
                #     "duration": 10,
                #     "frame_rate": 30
                # },
                # {
                #     "type": "CHECKERBOARD",
                #     "name": "checkerboard1",
                #     "width": VIDEO_WIDTH,
                #     "height": VIDEO_HEIGHT,
                #     "square_size": 50,
                #     "duration": 10,
                #     "frame_rate": 30
                # },
                # {
                #     "type": "COLOR_BARS",
                #     "name": "colobar1",
                #     "width": VIDEO_WIDTH,
                #     "height": VIDEO_HEIGHT,
                #     "duration": 10,
                #     "frame_rate": 30
                # },
                {
                    "type": "MOVING_BOX",
                    "name": "movingbox1",
                    "width": VIDEO_WIDTH,
                    "height": VIDEO_HEIGHT,
                    "box_size": 10,
                    "speed" : 10,
                    "duration": 3,
                    "frame_rate": 60
                }
            ]
        }

        config_analyzer = {
            "command": "CONFIG",
            "data": [
                # {
                #     "name": "solid_color1",
                #     "width": VIDEO_WIDTH,
                #     "height": VIDEO_HEIGHT
                # },
                # {
                #     "name": "checkerboard1",
                #     "width": VIDEO_WIDTH,
                #     "height": VIDEO_HEIGHT
                # },
                # {
                #     "name": "colobar1",
                #     "width": VIDEO_WIDTH,
                #     "height": VIDEO_HEIGHT
                # },
                {
                    "name": "movingbox1",
                    "width": VIDEO_WIDTH,
                    "height": VIDEO_HEIGHT
                }
            ]
        }

        # Send configuration to the pattern generator
        server_gen.send_data(config_gen)
        print("Config sent to pattern generator")
        data_gen = server_gen.receive_data()
        if data_gen["config"] == "OK":
            print("Pattern generator configured successfully")

        # Send configuration to the video analyzer
        server_analyzer.send_data(config_analyzer)
        print("Config sent to video analyzer")
        data_analyzer = server_analyzer.receive_data()
        if data_analyzer["config"] == "OK":
            print("Video analyzer configured successfully")

        while True:
            for config in config_analyzer["data"]:
                name = config["name"]
                print(name)
                frame_req = {"command": "GET_FRAME", "name": name}
                server_gen.send_data(frame_req)
                data_gen = server_gen.receive_large_data()
                print("frame received")
                if data_gen and data_gen["frame"] is not None:
                    frame_data = {
                        "name": name,
                        "frame": data_gen["frame"]
                    }
                    server_analyzer.send_large_data(frame_data)
                    data_analyzer = server_analyzer.receive_data()
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
