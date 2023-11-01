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
        std::cout << "324rty431START_MATRIX\n";

        for(int i = 0; i < mat.rows(); i++) {
            std::cout << "324rty431" << mat.row(i) << std::endl;
        }
    
        
        std::cout << "324rty431END_MATRIX\n";
        
        // Flushing the output to make sure it is written immediately
        std::cout << std::flush;
        
        // Waiting for 10 seconds
        std::this_thread::sleep_for(std::chrono::seconds(5));
    }
    
    return 0;
}
