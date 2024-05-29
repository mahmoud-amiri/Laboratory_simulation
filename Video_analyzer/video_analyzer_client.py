import json
import matplotlib.pyplot as plt
import sys
import os
import cv2
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '../submodules'))
from submodules.socket.python.client import Client

CHUNK_SIZE = 1024  # Size of each chunk in bytes

class VideoAnalyzer:
    def __init__(self, client):
        self.client = client
        self.channels = {}
        self.config = {}
        self.partial_data = {}
        self.total_chunks = {}
        self.received_chunks = {}

    def configure(self, config_data):
        for config in config_data:
            name = config["name"]
            print(f"name = {name}")
            self.config[name] = config
            self.channels[name] = {
                "fig": plt.figure(),
                "ax": None,
                "im": None
            }
            self.channels[name]["ax"] = self.channels[name]["fig"].add_subplot(1, 1, 1)
            self.channels[name]["im"] = self.channels[name]["ax"].imshow(np.zeros((480, 640, 3), dtype=np.uint8))  # Initialize with a blank frame
        print("VideoAnalyzer configuration complete")

    def update_frame(self, name, frame):
        ax = self.channels[name]["ax"]
        im = self.channels[name]["im"]
        im.set_data(frame)
        ax.figure.canvas.draw()
        ax.figure.canvas.flush_events()

    def receive_large_data(self):
        data_complete = False
        while not data_complete:
            chunk = self.client.receive_data()
            if chunk:
                chunk_data = chunk["chunk"]
                index = chunk["index"]
                total = chunk["total"]

                if index == 0:
                    self.partial_data[chunk["name"]] = chunk_data
                    self.received_chunks[chunk["name"]] = 1
                    self.total_chunks[chunk["name"]] = total
                else:
                    self.partial_data[chunk["name"]] += chunk_data
                    self.received_chunks[chunk["name"]] += 1

                if self.received_chunks[chunk["name"]] == self.total_chunks[chunk["name"]]:
                    data_complete = True
                    complete_data = self.partial_data.pop(chunk["name"])
                    self.received_chunks.pop(chunk["name"])
                    self.total_chunks.pop(chunk["name"])
                    return complete_data, chunk["name"]
        return None, None

    def receive_frame(self):
        data, name = self.receive_large_data()
        if data:
            response = json.loads(data)
            if "command" in response and response["command"] == "CONFIG":
                self.configure(response["data"])
                self.client.send_data({"config": "OK"})  # Send acknowledgment after processing the configuration
                print("I have sent the configuration ack")
            else:
                if response["name"] in self.channels:
                    name = response["name"]
                    frame_data = response["frame"]
                    frame = np.array(frame_data, dtype=np.uint8).reshape((480, 640, 3))  # Assuming 640x480 RGB image
                    print(f"the channel {name} is updated")
                    self.update_frame(name, frame)
                    self.client.send_data({"response": "OK"})  # Send acknowledgment after processing the data
                else:
                    self.client.send_data({"response": f"False channel {name}"})

    def start(self):
        plt.ion()  # Initialize interactive mode once
        try:
            for i in range(20):  # while True:
                print("Waiting for data...")
                self.receive_frame()
                plt.pause(0.0001)
        except KeyboardInterrupt:
            self.client.stop()
            print("Client stopped by user")
        finally:
            plt.ioff()  # Turn off interactive mode before exiting
            plt.show()

if __name__ == "__main__":
    with open('./Video_analyzer/video_analyzer_port_config.json', 'r') as f:
        config = json.load(f)
    port = config["port"]
    client = Client(port)

    video_analyzer = VideoAnalyzer(client)
    try:
        if client.start():
            video_analyzer.start()
    except KeyboardInterrupt:
        client.stop()
        print("Client stopped by user")
