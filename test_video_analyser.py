import json
import threading
import time
import random
import numpy as np

from matplotlib import pyplot as plt
from oscilloscope.oscilloscope_client import Oscilloscope
from Video_analyzer.video_analyzer_client import VideoAnalyzer


class SimulatedClient:
    def __init__(self, port):
        self.port = port
        self.data_queue = []
        self.running = True

    def start(self):
        print(f"Simulated client started on port {self.port}")
        return True

    def stop(self):
        self.running = False
        print("Simulated client stopped")

    def send_data(self, data):
        print(f"Sending data: {data}")

    def receive_data(self):
        if self.data_queue:
            return self.data_queue.pop(0)
        return None

    def generate_oscilloscope_data(self):
        while self.running:
            sample = {"name": "channel1", "sample": random.random()}
            self.data_queue.append(sample)
            time.sleep(0.01)

    def generate_video_data(self):
        while self.running:
            frame = (np.random.rand(480, 640, 3) * 255).astype(np.uint8)
            frame_data = frame.tobytes()
            sample = {"name": "channel1", "frame": frame_data}
            self.data_queue.append(sample)
            time.sleep(0.1)

def test_oscilloscope():
    client = SimulatedClient(port=12345)
    oscilloscope = Oscilloscope(client)

    config_data = [{"name": "channel1"}]
    oscilloscope.configure(config_data)

    threading.Thread(target=client.generate_oscilloscope_data).start()

    try:
        if client.start():
            oscilloscope.start()
    except KeyboardInterrupt:
        client.stop()
        print("Client stopped by user")

def test_video_analyzer():
    client = SimulatedClient(port=12345)
    video_analyzer = VideoAnalyzer(client)

    config_data = [{"name": "channel1"}]
    video_analyzer.configure(config_data)

    threading.Thread(target=client.generate_video_data).start()

    try:
        if client.start():
            video_analyzer.start()
    except KeyboardInterrupt:
        client.stop()
        print("Client stopped by user")

if __name__ == "__main__":
    # Run the tests
    choice = input("Enter '1' to test Oscilloscope or '2' to test VideoAnalyzer: ")
    if choice == '1':
        test_oscilloscope()
    elif choice == '2':
        test_video_analyzer()
    else:
        print("Invalid choice")
