# compile.do

# Set the project library name
set libname work

# Create the library
vlib $libname
vmap $libname $libname

# Set the source directory
set srcdir ./dpi

# Compile the DPI interface first
vlog -sv $srcdir/server_dpi_interface.sv

# Compile the package first
vlog -sv $srcdir/server_pkg.sv

# Compile the SystemVerilog files
vlog -sv $srcdir/server_dpi.sv
vlog -sv ./pattern_gen_analyzer_exampel.sv

# Link the C/C++ DPI library
vlog -ccflags "-I/usr/include" -cflags "-fPIC" -LDFLAGS "-shared" -sv_lib $srcdir/server

# Load the simulation
vsim -lib $libname top

# Run the simulation
run -all

# End of compile.do
