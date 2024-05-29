import json


from submodules.socket.python.server import Server

def communicate(server_signal_gen, server_oscilloscope):
    try:

        print("def communicate(server_signal_gen, server_oscilloscope):")
        config_signal_gen = {
            "command": "CONFIG",
            "data": [{
                "type": "SINE",
                "name": "sine1",
                "frequency": 100,
                "amplitude": 1,
                "phase": 0,
                "duration": 100,
                "sampling_rate": 10000
            },
            {
                "type": "COSINE",
                "name": "cosine1",
                "frequency": 200,
                "amplitude": 0.5,
                "phase": 0,
                "duration": 100,
                "sampling_rate": 10000
            },
            {
                "type": "SQUARE",
                "name": "square1",
                "frequency": 300,
                "amplitude": 1.5,
                "phase": 0,
                "duration": 100,
                "sampling_rate": 10000
            },
            {
                "type": "TRIANGLE",
                "name": "triangle1",
                "frequency": 50,
                "amplitude": 0.7,
                "phase": 0,
                "duration": 100,
                "sampling_rate": 10000
            },
            {
                "type": "SAWTOOTH",
                "name": "sawtooth1",
                "frequency": 150,
                "amplitude": 0.3,
                "phase": 0,
                "duration": 100,
                "sampling_rate": 10000
            }
            ]
        }
        config_oscilloscope = {
        "command": "CONFIG",
        "data": [
            {
            "name": "sine1",
            "data": 0
            },{
            "name": "cosine1",
            "data": 0
            },
            {
            "name": "square1",
            "data": 0
            },
            {
            "name": "triangle1",
            "data": 0
            },
            {
            "name": "sawtooth1",
            "data": 0
            }
        ]
        }
        server_signal_gen.send_data(config_signal_gen)
        print("config_signal_gen sent")
        print(config_oscilloscope)
        server_oscilloscope.send_data(config_oscilloscope)
        print("config_oscilloscope sent")
        data = server_oscilloscope.receive_data()
        if data["config"]=="OK":
            print(f"oscilloscope configured successfully")
        for i in range(2000): #while True:
            for name in ["sine1","cosine1","square1","triangle1", "sawtooth1"]:
                sample_req = {"command": "GET_SAMPLE", "name": name}
                server_signal_gen.send_data(sample_req)
                data = server_signal_gen.receive_data()
                if data:
                    data_cfg = {
                    "name": name,
                    "sample": data["sample"]
                    }
                    server_oscilloscope.send_data(data_cfg)
                    data = server_oscilloscope.receive_data()
                    if data["response"]=="OK":
                        print(f"oscilloscope received the data")
                    # print(f"Received JSON from client: {data}")
    except Exception as e:
        print(f"An error occurred during communication: {e}")
    finally:
        server_signal_gen.stop()

if __name__ == "__main__":
    with open('port_config.json', 'r') as f:
        config = json.load(f)
    port_signal_gen = config["port_signal_gen"]
    port_oscilloscope = config["port_oscilloscope"]

    server_signal_gen = Server(port_signal_gen)
    server_oscilloscope = Server(port_oscilloscope)

    try:
        print("try:server_oscilloscope.start()")
        server_oscilloscope.start()
        print("server_oscilloscope.start()")
        server_signal_gen.start()
        communicate(server_signal_gen, server_oscilloscope)
    except KeyboardInterrupt:
        server_signal_gen.stop()
        print("Client stopped by user")
