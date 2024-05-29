// Communication.sv
class Communication;
    Server server_gen;
    Server server_analyzer;
    string config_gen, config_analyzer;

    function new(Server server_gen, Server server_analyzer);
        this.server_gen = server_gen;
        this.server_analyzer = server_analyzer;
    endfunction

    task configure_gen();
        $readmemb("config_gen.mem", config_gen);
        server_gen.send(config_gen);
        server_gen.receive(config_gen);
        if (server_gen.get_received_data() == "{\"config\":\"OK\"}") begin
            $display("Pattern generator configured successfully");
        end
    endtask

    task configure_analyzer();
        $readmemb("config_analyzer.mem", config_analyzer);
        server_analyzer.send(config_analyzer);
        server_analyzer.receive(config_analyzer);
        if (server_analyzer.get_received_data() == "{\"config\":\"OK\"}") begin
            $display("Video analyzer configured successfully");
        end
    endtask

    task main_loop();
        string frame_req;
        while (1) begin
            frame_req = "{\"command\":\"GET_FRAME\",\"name\":\"movingbox1\"}";
            server_gen.send(frame_req);
            server_gen.receive(frame_req);
            $display("Frame received: %s", server_gen.get_received_data());

            // Assuming `received_data` contains the frame data
            string frame_data = "{\"name\":\"movingbox1\",\"frame\":\"" + server_gen.get_received_data() + "\"}";
            server_analyzer.send(frame_data);
            server_analyzer.receive(frame_req);
            if (server_analyzer.get_received_data() == "{\"response\":\"FRAME_OK\"}") begin
                $display("Frame for movingbox1 processed by analyzer");
            end
        end
    endtask
endclass
