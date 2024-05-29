import json
import matplotlib.pyplot as plt
import sys
import os
import cv2
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '../submodules'))
from submodules.socket.python.client import Client

class VideoAnalyzer:
    def __init__(self, client):
        self.client = client
        self.channels = {}
        self.config = {}

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

    def receive_frame(self):
        response = self.client.receive_data()
        if response:
            if "command" in response and response["command"] == "CONFIG":
                self.configure(response["data"])
                self.client.send_data({"config":"OK"})  # Send acknowledgment after processing the configuration
                print("I have sent the configuration ack")
            else:
                if response["name"] in self.channels:
                    name = response["name"] 
                    frame_data = response["frame"]
                    frame = np.frombuffer(frame_data, dtype=np.uint8).reshape((480, 640, 3))  # Assuming 640x480 RGB image
                    print(f"the channel {name} is updated")
                    self.update_frame(name, frame)
                    self.client.send_data({"response":"OK"})  # Send acknowledgment after processing the data
                else:
                    self.client.send_data({"response":f"False channel {name}"})

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