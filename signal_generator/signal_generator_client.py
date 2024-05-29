import numpy as np
import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../submodules'))
from submodules.socket.python.client import Client

class SignalGeneratorClient:
    def __init__(self, client):
        self.client = client
        self.signals = {}
        self.indices = {}

    def generate_sine_wave(self, name, frequency, amplitude, phase, duration, sampling_rate):
        t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
        self.signals[name] = amplitude * np.sin(2 * np.pi * frequency * t + phase)
        self.indices[name] = 0

    def generate_cosine_wave(self, name, frequency, amplitude, phase, duration, sampling_rate):
        t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
        self.signals[name] = amplitude * np.cos(2 * np.pi * frequency * t + phase)
        self.indices[name] = 0

    def generate_square_wave(self, name, frequency, amplitude, phase, duration, sampling_rate):
        t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
        self.signals[name] = amplitude * np.sign(np.sin(2 * np.pi * frequency * t + phase))
        self.indices[name] = 0

    def generate_triangular_wave(self, name, frequency, amplitude, phase, duration, sampling_rate):
        t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
        self.signals[name] = amplitude * (2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1)
        self.indices[name] = 0

    def generate_sawtooth_wave(self, name, frequency, amplitude, phase, duration, sampling_rate):
        t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
        self.signals[name] = amplitude * (2 * (t * frequency - np.floor(t * frequency + 0.5)))
        self.indices[name] = 0

    def configure(self, config_data):
        for config in config_data:
            print(f"Processing config: {config}")
            signal_type = config["type"]
            name = config["name"]
            frequency = config["frequency"]
            amplitude = config["amplitude"]
            phase = config.get("phase", 0)  # Default phase is 0 if not provided
            duration = config["duration"]
            sampling_rate = config["sampling_rate"]
            if signal_type == "SINE":
                self.generate_sine_wave(name, frequency, amplitude, phase, duration, sampling_rate)
            elif signal_type == "COSINE":
                self.generate_cosine_wave(name, frequency, amplitude, phase, duration, sampling_rate)
            elif signal_type == "SQUARE":
                self.generate_square_wave(name, frequency, amplitude, phase, duration, sampling_rate)
            elif signal_type == "TRIANGLE":
                self.generate_triangular_wave(name, frequency, amplitude, phase, duration, sampling_rate)
            elif signal_type == "SAWTOOTH":
                self.generate_sawtooth_wave(name, frequency, amplitude, phase, duration, sampling_rate)
        print("Configuration complete")

    def get_sample(self, name):
        if self.signals.get(name) is not None and self.indices[name] < len(self.signals[name]):
            sample = self.signals[name][self.indices[name]]
            self.indices[name] += 1
            return sample
        return None

    def communicate(self):
        try:
            for i in range(2000): #while True:
                request = self.client.receive_data()
                if request:
                    print(f"Received request: {request}")
                    if isinstance(request, dict) and "command" in request:
                        if request["command"] == "CONFIG":
                            self.configure(request["data"])
                            print("config received")
                        elif request["command"] == "GET_SAMPLE":
                            name = request["name"]
                            sample = self.get_sample(name)
                            response = {"sample": sample}
                            self.client.send_data(response)
                        elif request["command"] == "STOP":
                            break
        except Exception as e:
            print(f"An error occurred during communication: {e}")

if __name__ == "__main__":
    with open('./signal_generator/signal_generator_port_config.json', 'r') as f:
        config = json.load(f)
    port = config["port"]
    client = Client(port)
    signal_generator_client = SignalGeneratorClient(client)

    try:
        client.start()
        signal_generator_client.communicate()
    except KeyboardInterrupt:
        client.stop()
        print("Client stopped by user")
