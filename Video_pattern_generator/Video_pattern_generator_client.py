import numpy as np
import json
import sys
import os
import cv2
from math import ceil

sys.path.append(os.path.join(os.path.dirname(__file__), '../submodules'))
from submodules.socket.python.client import Client

CHUNK_SIZE = 1024  # Size of each chunk in bytes

class VideoPatternGeneratorClient:
    def __init__(self, client):
        self.client = client
        self.patterns = {}
        self.indices = {}

    def generate_solid_color(self, name, color, width, height, duration, frame_rate):
        frames = int(duration * frame_rate)
        self.patterns[name] = np.full((frames, height, width, 3), color, dtype=np.uint8)
        self.indices[name] = 0

    def generate_checkerboard(self, name, width, height, square_size, duration, frame_rate):
        frames = int(duration * frame_rate)
        pattern = np.zeros((height, width, 3), dtype=np.uint8)
        for y in range(0, height, square_size):
            for x in range(0, width, square_size):
                if (x // square_size) % 2 == (y // square_size) % 2:
                    pattern[y:y+square_size, x:x+square_size] = 255
        self.patterns[name] = np.tile(pattern, (frames, 1, 1, 1))
        self.indices[name] = 0

    def generate_color_bars(self, name, width, height, duration, frame_rate):
        frames = int(duration * frame_rate)
        color_bars = [
            (255, 255, 255), (255, 255, 0), (0, 255, 255),
            (0, 255, 0), (255, 0, 255), (255, 0, 0), (0, 0, 255)
        ]
        bar_width = width // len(color_bars)
        pattern = np.zeros((height, width, 3), dtype=np.uint8)
        for i, color in enumerate(color_bars):
            pattern[:, i*bar_width:(i+1)*bar_width] = color
        self.patterns[name] = np.tile(pattern, (frames, 1, 1, 1))
        self.indices[name] = 0

    def generate_moving_box(self, name, width, height, box_size, speed, duration, frame_rate):
        frames = int(duration * frame_rate)
        pattern = np.zeros((frames, height, width, 3), dtype=np.uint8)
        for i in range(frames):
            x = (i * speed) % (width - box_size)
            y = (i * speed) % (height - box_size)
            pattern[i, y:y+box_size, x:x+box_size] = (0, 255, 0)  # Green box
        self.patterns[name] = pattern
        self.indices[name] = 0

    def configure(self, config_data):
        for config in config_data:
            print(f"Processing config: {config}")
            pattern_type = config["type"]
            name = config["name"]
            width = config["width"]
            height = config["height"]
            duration = config["duration"]
            frame_rate = config["frame_rate"]
            if pattern_type == "SOLID_COLOR":
                color = tuple(config["color"])
                self.generate_solid_color(name, color, width, height, duration, frame_rate)
            elif pattern_type == "CHECKERBOARD":
                square_size = config["square_size"]
                self.generate_checkerboard(name, width, height, square_size, duration, frame_rate)
            elif pattern_type == "COLOR_BARS":
                self.generate_color_bars(name, width, height, duration, frame_rate)
            elif pattern_type == "MOVING_BOX":
                box_size = config["box_size"]
                speed = config["speed"]
                self.generate_moving_box(name, width, height, box_size, speed, duration, frame_rate)
        print("Configuration complete")
        self.client.send_data({"config": "OK"})  # Send acknowledgment after processing the configuration
        print("I have sent the configuration ack")

    def get_frame(self, name):
        if self.patterns.get(name) is not None and self.indices[name] < len(self.patterns[name]):
            frame = self.patterns[name][self.indices[name]]
            self.indices[name] += 1
            return frame
        return None

    def send_large_data(self, data):
        serialized_data = json.dumps(data)
        num_chunks = ceil(len(serialized_data) / CHUNK_SIZE)
        for i in range(num_chunks):
            chunk = serialized_data[i * CHUNK_SIZE:(i + 1) * CHUNK_SIZE]
            self.client.send_data({"chunk": chunk, "index": i, "total": num_chunks})

    def communicate(self):
        try:
            for i in range(20):  # while True:
                request = self.client.receive_data()
                if request:
                    print(f"Received request: {request}")
                    if isinstance(request, dict) and "command" in request:
                        if request["command"] == "CONFIG":
                            self.configure(request["data"])
                            print("Config received")
                        elif request["command"] == "GET_FRAME":
                            name = request["name"]
                            frame = self.get_frame(name)
                            response = {"frame": frame.tolist() if frame is not None else None}
                            self.send_large_data(response)
                        elif request["command"] == "STOP":
                            break
        except Exception as e:
            print(f"An error occurred during communication: {e}")

if __name__ == "__main__":
    with open('./Video_pattern_generator/Video_pattern_generator_port_config.json', 'r') as f:
        config = json.load(f)
    port = config["port"]
    client = Client(port)
    print("client = Client(port)")
    video_pattern_generator_client = VideoPatternGeneratorClient(client)
    print("video_pattern_generator_client = VideoPatternGeneratorClient(client)")

    try:
        client.start()
        print("client.start()")
        video_pattern_generator_client.communicate()
        print("video_pattern_generator_client.communicate()")
    except KeyboardInterrupt:
        client.stop()
        print("Client stopped by user")
