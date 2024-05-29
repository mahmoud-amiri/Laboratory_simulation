// top.sv
module top;

    // Instantiate the servers
    Server server_gen = new(5000); // example port numbers
    Server server_analyzer = new(6000);

    // Instantiate the communication handler
    Communication comm = new(server_gen, server_analyzer);

    initial begin
        // Start servers
        server_gen.start();
        server_analyzer.start();

        // Configure servers
        comm.configure_gen();
        comm.configure_analyzer();

        // Start main communication loop
        comm.main_loop();

        // Stop servers (this part will be executed when the loop ends, which is not in the original Python code)
        server_gen.stop();
        server_analyzer.stop();
    end

endmodule
