# Step 1: Install prerequisites
sudo apt update
sudo apt install git cmake gcc

# Step 2: Clone the cJSON repository
git clone https://github.com/DaveGamble/cJSON.git

# Step 3: Create and navigate to the build directory
cd cJSON
mkdir build
cd build

# Step 4: Configure the build with CMake
cmake ..

# Step 5: Build the library
make

# Step 6: Install the library (optional)
sudo make install
