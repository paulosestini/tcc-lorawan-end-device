#include <iostream>
#include <Eigen/Dense>
 
using Eigen::MatrixXd;
using Eigen::VectorXd;
using Eigen::ArrayXd;

const int MAX_FRAMES = 500;
const int N_SUBPORTERS = 64;
const float THRESHOLD_DETECTION = 0.03;
MatrixXd frames(MAX_FRAMES, N_SUBPORTERS);
ArrayXd powers(MAX_FRAMES);
int collected_frames = 0;


ArrayXd generate_fake_csi_vector() {
  return (ArrayXd::Random(64) + 1) / 2;
}

void process_Csi(ArrayXd csi_vector, double rssi) {
  
  double rssi_power = pow(10, rssi/10);
  double scale_factor = rssi_power / (csi_vector.sum() / N_SUBPORTERS);
  scale_factor = sqrt(scale_factor);

  csi_vector *= scale_factor;
  csi_vector = 10 * (csi_vector + 1e-10 ).log10();

  if(collected_frames < MAX_FRAMES) {
    // To be continued...
  }


  std::cout << csi_vector << std::endl;

  collected_frames += 1;

  return;
}
 
int main()
{
 while(1) {
  process_Csi(generate_fake_csi_vector(), 10.0);
 } 
}

