#include <iostream>
#include <Eigen/Dense>
#include <thread>
#include <chrono>

int main() {
    Eigen::MatrixXf mat(500, 52);
    
    while (true) {
        // Filling the matrix with random numbers
        mat.setRandom();
        
        // Printing start delimiter, the matrix, and end delimiter
        std::cout << "START_MATRIX\n" << mat << "\nEND_MATRIX\n";
        
        // Flushing the output to make sure it is written immediately
        std::cout << std::flush;
        
        // Waiting for 10 seconds
        std::this_thread::sleep_for(std::chrono::seconds(5));
    }
    
    return 0;
}
