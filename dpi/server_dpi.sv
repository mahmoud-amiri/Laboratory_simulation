// server_dpi.sv
import "DPI-C" function void start_server(input int port);
import "DPI-C" function void stop_server();
import "DPI-C" function void send_data(input string data);
import "DPI-C" function void receive_data(output string data);
