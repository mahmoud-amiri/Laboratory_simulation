// Server.sv
class Server;
    int port;
    string received_data;

    function new(int port);
        this.port = port;
    endfunction

    task start();
        start_server(port);
        $display("Server started on port %0d", port);
    endtask

    task stop();
        stop_server();
        $display("Server stopped on port %0d", port);
    endtask

    task send(string data);
        send_data(data);
    endtask

    task receive(output string data);
        receive_data(data);
        this.received_data = data;
    endtask

    function string get_received_data();
        return received_data;
    endfunction
endclass
