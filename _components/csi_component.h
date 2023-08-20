#ifndef ESP32_CSI_CSI_COMPONENT_H
#define ESP32_CSI_CSI_COMPONENT_H

#include "time_component.h"
#include "math.h"
#include <sstream>
#include <iostream>

#include <eigen3/Eigen/Eigen>
using Eigen::MatrixXf;
using Eigen::VectorXf;
using Eigen::ArrayXf;

char *project_type;

#define CSI_RAW 1
#define CSI_AMPLITUDE 0
#define CSI_PHASE 0

#define CSI_TYPE CSI_RAW

SemaphoreHandle_t mutex = xSemaphoreCreateMutex();

// --------
const int MAX_FRAMES = 500;
const int N_SUBPORTERS = 64;
const int N_NON_NULL_SUBPORTERS = 52;
const int WINDOW_SIZE = 15;
const float THRESHOLD_DETECTION = 0.07;
float reference_power = 0;
float current_power = 0;
MatrixXf frames(MAX_FRAMES, N_NON_NULL_SUBPORTERS);
ArrayXf powers(MAX_FRAMES);
ArrayXf csi_vector(N_NON_NULL_SUBPORTERS);
int collected_frames = 0;
bool detected = false;
bool should_send_lora_packet = false;

void process_csi(ArrayXf full_csi_vector, float rssi) {
  csi_vector << full_csi_vector(Eigen::seq(6, 31)), full_csi_vector(Eigen::seq(33, 58));

  float rssi_power = pow(10, rssi/10);
  float scale_factor = rssi_power / (csi_vector.sum() / N_NON_NULL_SUBPORTERS);
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

        printf("Current power: %f, Reference power: %f \n", current_power, reference_power);


      if (current_power <= (1 + THRESHOLD_DETECTION) * reference_power) {
        if(!detected) {
          printf("\n DETECTED \n");
          should_send_lora_packet = true;
          detected = true;
        } else {
          detected = false;
        }
        
      }
    }

    frames << frames(Eigen::seq(1, MAX_FRAMES-1), Eigen::all), csi_vector.transpose();
  } 
  
  collected_frames += 1;

  return;
}


// --------

void _wifi_csi_cb(void *ctx, wifi_csi_info_t *data) {
    xSemaphoreTake(mutex, portMAX_DELAY);
    std::stringstream ss;

    wifi_csi_info_t d = data[0];
    char mac[20] = {0};
    sprintf(mac, "%02X:%02X:%02X:%02X:%02X:%02X", d.mac[0], d.mac[1], d.mac[2], d.mac[3], d.mac[4], d.mac[5]);

    ss << "CSI_DATA,"
       << project_type << ","
       << mac << ","
       // https://github.com/espressif/esp-idf/blob/9d0ca60398481a44861542638cfdc1949bb6f312/components/esp_wifi/include/esp_wifi_types.h#L314
       << d.rx_ctrl.rssi << ","
       << d.rx_ctrl.rate << ","
       << d.rx_ctrl.sig_mode << ","
       << d.rx_ctrl.mcs << ","
       << d.rx_ctrl.cwb << ","
       << d.rx_ctrl.smoothing << ","
       << d.rx_ctrl.not_sounding << ","
       << d.rx_ctrl.aggregation << ","
       << d.rx_ctrl.stbc << ","
       << d.rx_ctrl.fec_coding << ","
       << d.rx_ctrl.sgi << ","
       << d.rx_ctrl.noise_floor << ","
       << d.rx_ctrl.ampdu_cnt << ","
       << d.rx_ctrl.channel << ","
       << d.rx_ctrl.secondary_channel << ","
       << d.rx_ctrl.timestamp << ","
       << d.rx_ctrl.ant << ","
       << d.rx_ctrl.sig_len << ","
       << d.rx_ctrl.rx_state << ","
       << real_time_set << ","
       << get_steady_clock_timestamp() << ","
       << data->len << ",[";



#if CONFIG_SHOULD_COLLECT_ONLY_LLTF
    int data_len = 128;
#else
    int data_len = data->len;
#endif

int8_t *my_ptr;
#if CSI_RAW
    my_ptr = data->buf;
    for (int i = 0; i < data_len; i++) {
        ss << (int) my_ptr[i] << " ";
    }
#endif

// -------------------------
    ArrayXf full_csi_vector(N_SUBPORTERS);;

    my_ptr = data->buf;
    for (int i = 0; i < data_len / 2; i++) {
        full_csi_vector(i) = (float) sqrt(pow(my_ptr[i * 2], 2) + pow(my_ptr[(i * 2) + 1], 2));
    }

    process_csi(full_csi_vector, d.rx_ctrl.rssi);


// -------------------------
#if CSI_AMPLITUDE
    my_ptr = data->buf;
    for (int i = 0; i < data_len / 2; i++) {
        ss << (int) sqrt(pow(my_ptr[i * 2], 2) + pow(my_ptr[(i * 2) + 1], 2)) << " ";
    }
#endif
#if CSI_PHASE
    my_ptr = data->buf;
    for (int i = 0; i < data_len / 2; i++) {
        ss << (int) atan2(my_ptr[i*2], my_ptr[(i*2)+1]) << " ";
    }
#endif
    ss << "]\n";
    //printf(ss.str().c_str());
    fflush(stdout);
    vTaskDelay(0);
    xSemaphoreGive(mutex);
}

void _print_csi_csv_header() {
    char *header_str = (char *) "type,role,mac,rssi,rate,sig_mode,mcs,bandwidth,smoothing,not_sounding,aggregation,stbc,fec_coding,sgi,noise_floor,ampdu_cnt,channel,secondary_channel,local_timestamp,ant,sig_len,rx_state,real_time_set,real_timestamp,len,CSI_DATA\n";
    outprintf(header_str);
}

void csi_init(char *type) {
    project_type = type;

#ifdef CONFIG_SHOULD_COLLECT_CSI
    ESP_ERROR_CHECK(esp_wifi_set_csi(1));

    // @See: https://github.com/espressif/esp-idf/blob/master/components/esp_wifi/include/esp_wifi_types.h#L401
    wifi_csi_config_t configuration_csi;
    configuration_csi.lltf_en = 1;
    configuration_csi.htltf_en = 1;
    configuration_csi.stbc_htltf2_en = 1;
    configuration_csi.ltf_merge_en = 1;
    configuration_csi.channel_filter_en = 0;
    configuration_csi.manu_scale = 0;

    ESP_ERROR_CHECK(esp_wifi_set_csi_config(&configuration_csi));
    ESP_ERROR_CHECK(esp_wifi_set_csi_rx_cb(&_wifi_csi_cb, NULL));

    _print_csi_csv_header();
#endif
}

#endif //ESP32_CSI_CSI_COMPONENT_H
