// top.sv
import server_pkg::*;
module top;

    // Instantiate the servers
    Server server_gen;
    Server server_analyzer;
    Communication comm;

   

    initial begin
        // Initialize servers
        server_gen = new(5000); // example port numbers
        server_analyzer = new(6000);
        comm = new(server_gen, server_analyzer);
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
