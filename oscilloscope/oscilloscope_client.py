import socket
import json
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../submodules'))
from submodules.socket.python.client import Client

class Oscilloscope:
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
                "data": [],
                "fig": plt.figure(),
                "ax": None,
                "line": None,
                "zoom_x": 1,
                "zoom_y": 1
            }
            self.channels[name]["ax"] = self.channels[name]["fig"].add_subplot(1, 1, 1)
            self.channels[name]["line"], = self.channels[name]["ax"].plot([], [], lw=2)
        print("Oscilloscope configuration complete")

    def update_plot(self, name):
        data = self.channels[name]["data"]
        ax = self.channels[name]["ax"]
        line = self.channels[name]["line"]
        if data:
            # ax.clear()
            # line.set_data(range(len(data)), data)
            # ax.set_xlim(0, len(data) / self.channels[name]["zoom_x"])
            # ax.set_ylim(min(data) / self.channels[name]["zoom_y"], max(data) / self.channels[name]["zoom_y"])
            # ax.figure.canvas.draw()
            line.set_xdata(range(len(data)))
            line.set_ydata(data)
            ax.relim()
            ax.autoscale_view()
            ax.figure.canvas.draw()
            ax.figure.canvas.flush_events()

    def zoom(self, name, zoom_x=None, zoom_y=None):
        if zoom_x:
            self.channels[name]["zoom_x"] = zoom_x
        if zoom_y:
            self.channels[name]["zoom_y"] = zoom_y

    def receive_sample(self):
        
        #for i in range(20): #while True:
        response = self.client.receive_data()
        if response:
            if "command" in response and response["command"] == "CONFIG":
                self.configure(response["data"])
                self.client.send_data({"config":"OK"})  # Send acknowledgment after processing the configuration
                print("I have sent the configuration ack")
            else:
                if response["name"] in self.channels:
                    name = response["name"] 
                    self.channels[name]["data"].append(response["sample"])
                    print(f"""the channel {name} is updated""")
                    if len(self.channels[name]["data"]) > 1000:  # Keep buffer to a reasonable size
                        self.channels[name]["data"].pop(0)
                    self.update_plot(name)
                    self.client.send_data({"response":"OK"})  # Send acknowledgment after processing the data
                else:
                    self.client.send_data({"response":f"False channel {name}"})   

    def start(self):
        plt.ion()  # Initialize interactive mode once
        try:
            while True:
                print("Waiting for data...")
                self.receive_sample()
                plt.pause(0.0001)
        except KeyboardInterrupt:
            self.client.stop()
            print("Client stopped by user")
        finally:
            plt.ioff()  # Turn off interactive mode before exiting
            plt.show()  



if __name__ == "__main__":
    with open('./oscilloscope/oscilloscope_port_config.json', 'r') as f:
        config = json.load(f)
    port = config["port"]
    client = Client(port)
    oscilloscope = Oscilloscope(client)

    try:
        if client.start():
            oscilloscope.start()
    except KeyboardInterrupt:
        client.stop()
        print("Client stopped by user")
