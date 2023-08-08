#include <iostream>
#include <Eigen/Dense>
 
using Eigen::MatrixXd;
using Eigen::VectorXd;
using Eigen::ArrayXd;

const int MAX_FRAMES = 500;
const int N_SUBPORTERS = 52;
const int WINDOW_SIZE = 50;
const float THRESHOLD_DETECTION = 0.03;
double reference_power = 0;
double current_power = 0;
MatrixXd frames(MAX_FRAMES, N_SUBPORTERS);
ArrayXd powers(MAX_FRAMES);
ArrayXd csi_vector(N_SUBPORTERS);
int collected_frames = 0;
bool detected = 0;
bool should_send_lora_packet = 0;


ArrayXd generate_fake_csi_vector() {
  return (ArrayXd::Random(64) + 1) / 2;
}

void process_Csi(ArrayXd full_csi_vector, double rssi) {
  csi_vector << full_csi_vector(Eigen::seq(6, 31)), full_csi_vector(Eigen::seq(33, 58));

  double rssi_power = pow(10, rssi/10);
  double scale_factor = rssi_power / (csi_vector.sum() / N_SUBPORTERS);
  scale_factor = sqrt(scale_factor);

  csi_vector *= scale_factor;
  csi_vector = 10 * (csi_vector + 1e-10 ).log10();

  if(collected_frames < MAX_FRAMES) {
    frames.row(collected_frames) = csi_vector;
  } else {
    if(collected_frames == MAX_FRAMES) {
      reference_power = frames.sum() / MAX_FRAMES;

      printf("\n\n ----REFERENCE ESTABLISHED---- \n\n");
    } else {
      current_power = frames(Eigen::seq(MAX_FRAMES - WINDOW_SIZE, MAX_FRAMES-1), Eigen::all).sum();
      current_power /= WINDOW_SIZE;

      if (current_power <= (1 + THRESHOLD_DETECTION) * reference_power) {
        if(!detected) {
          printf("\n DETECTED \n");
          should_send_lora_packet = true;
          detected = true;
        } else {
          detected = false;
        }
        
        printf("Current power: %f, Reference power: %f \n", current_power, reference_power);
      }
    }

    frames << frames(Eigen::seq(1, MAX_FRAMES-1), Eigen::all), csi_vector.transpose();
  } 
  
  collected_frames += 1;

  return;
}
 
int main()
{
 while(1) {
  process_Csi(generate_fake_csi_vector(), 10.0);
 } 
}

