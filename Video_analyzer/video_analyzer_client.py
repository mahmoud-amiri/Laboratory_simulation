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
                "im": None,
                "width": config["width"],
                "height": config["height"]
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


    def receive_large_data(self, max_attempts=100000):
        partial_data = ""
        attempts = 0

        while attempts < max_attempts:
            print(f"attempts = {attempts}")
            chunk = self.client.receive_data()
            print(chunk)
            if chunk:
                chunk_data = chunk.get("chunk", "")
                index = chunk.get("index", 0)
                total = chunk.get("total", 0)
                self.client.send_data({"data": f" chunk {index}/{total-1} received successfully"}) 
                print(f"index = {index} / total = {total-1}")
                partial_data += chunk_data

                if index + 1 == total:
                    print("Last chunk received")
                    # Last chunk received
                    try:
                        data = json.loads(partial_data)
                        name = data.get("name", 0)
                        return data, name
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse complete data: {e}")
                        return None
            attempts += 1

        raise TimeoutError("Failed to receive all chunks within the maximum number of attempts")


    def receive_frame(self):
        data, name = self.receive_large_data()
        print (f"frame name  = {name}")
        if data:
            print("if data:")
            #response = json.loads(data)
            response = data
            if response["name"] in self.channels:
                print("""if response["name"] in self.channels:""")
                name = response["name"]
                frame_data = response["frame"]
                print("""frame_data = response["frame"]""")
                frame = np.array(frame_data, dtype=np.uint8).reshape((self.channels[name]["width"], self.channels[name]["height"], 3))  # Assuming 640x480 RGB image
                print(f"the channel {name} is updated")
                self.update_frame(name, frame)
                self.client.send_data({"response": "OK"})  # Send acknowledgment after processing the data
            else:
                self.client.send_data({"response": f"False channel {name}"})

    def start(self):
        data = self.client.receive_data()
        if data:
            if "command" in data and data["command"] == "CONFIG":
                self.configure(data["data"])
                self.client.send_data({"config": "OK"})  # Send acknowledgment after processing the configuration
                print("I have sent the configuration ack")
        plt.ion()  # Initialize interactive mode once
        try:
            while True:
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
