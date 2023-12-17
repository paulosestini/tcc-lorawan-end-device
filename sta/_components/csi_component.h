#ifndef ESP32_CSI_CSI_COMPONENT_H
#define ESP32_CSI_CSI_COMPONENT_H

#include "freertos/task.h"
#include "esp_system.h"
#include "esp_log.h"
#include "esp_timer.h"

#include "time_component.h"
#include "math.h"
#include <sstream>
#include <iostream>
#include <freertos/semphr.h>

#include <eigen3/Eigen/Eigen>
using Eigen::Array;
using Eigen::MatrixXf;
using Eigen::VectorXf;
using Eigen::ArrayXf;
using Eigen::ArrayXXf;


char *project_type;

#define CSI_RAW 1
#define CSI_AMPLITUDE 0
#define CSI_PHASE 0

#define CSI_TYPE CSI_RAW

#define TIMEOUT_SECONDS 7

SemaphoreHandle_t mutex = xSemaphoreCreateMutex();
SemaphoreHandle_t lmicSemaphore = NULL;
static esp_timer_handle_t timeout_timer = NULL;

typedef unsigned int uint;
// --------
const int MAX_FRAMES = 500;
const int N_SUBPORTERS = 64;
const int N_NON_NULL_SUBPORTERS = 52;
const int WINDOW_SIZE = 150;
const int N_FEATURES = 16;
// const float THRESHOLD_DETECTION = 0.0415;
const float THRESHOLD_DETECTION = 0.04;
float reference_power = 0;
float current_power = 0;
MatrixXf frames(MAX_FRAMES, N_NON_NULL_SUBPORTERS);
//ArrayXXf frames(MAX_FRAMES, N_NON_NULL_SUBPORTERS);
ArrayXf powers(MAX_FRAMES);
ArrayXf csi_vector(N_NON_NULL_SUBPORTERS);
ArrayXf subporters_frame_mean(N_NON_NULL_SUBPORTERS);
ArrayXf subporters_frame_std_dev(N_NON_NULL_SUBPORTERS);
ArrayXf full_lora_payload(2*N_NON_NULL_SUBPORTERS);
ArrayXf final_lora_payload(N_FEATURES);

//Array<uint8_t, 1, 4*N_NON_NULL_SUBPORTERS> lora_payload;
Array<uint8_t, 1, 2*N_FEATURES> lora_payload;

Eigen::VectorXi features_to_send(N_FEATURES);


int collected_frames = 0;
bool detected = false;
bool obj_in_sight = false;
bool should_send = true;
bool potential_danger = false;


uint as_uint(const float x) {
    return *(uint*)&x;
}

float as_float(const uint x) {
    return *(float*)&x;
}

float half_to_float(const uint16_t x) { // IEEE-754 16-bit floating-point format (without infinity): 1-5-10, exp-15, +-131008.0, +-6.1035156E-5, +-5.9604645E-8, 3.311 digits
    const uint e = (x&0x7C00)>>10; // exponent
    const uint m = (x&0x03FF)<<13; // mantissa
    const uint v = as_uint((float)m)>>23; // evil log2 bit hack to count leading zeros in denormalized format
    return as_float((x&0x8000)<<16 | (e!=0)*((e+112)<<23|m) | ((e==0)&(m!=0))*((v-37)<<23|((m<<(150-v))&0x007FE000))); // sign : normalized : denormalized
}

uint16_t float_to_half(const float x) { // IEEE-754 16-bit floating-point format (without infinity): 1-5-10, exp-15, +-131008.0, +-6.1035156E-5, +-5.9604645E-8, 3.311 digits
    const uint b = as_uint(x)+0x00001000; // round-to-nearest-even: add last bit after truncated mantissa
    const uint e = (b&0x7F800000)>>23; // exponent
    const uint m = b&0x007FFFFF; // mantissa; in line below: 0x007FF000 = 0x00800000-0x00001000 = decimal indicator flag - initial rounding
    return (b&0x80000000)>>16 | (e>112)*((((e-112)<<10)&0x7C00)|m>>13) | ((e<113)&(e>101))*((((0x007FF000+m)>>(125-e))+1)>>1) | (e>143)*0x7FFF; // sign : normalized : denormalized : saturate
}

void print_bits(const uint16_t x) {
    for(int i=15; i>=0; i--) {
        std::cout << ((x>>i)&1);
        if(i==15||i==10) std::cout << " ";
        if(i==10) std::cout << "      ";
    }
    std::cout << '\n';
}

void print_bits(const float x) {
    uint b = *(uint*)&x;
    for(int i=31; i>=0; i--) {
        std::cout << ((b>>i)&1);
        if(i==31||i==23) std::cout << " ";
        if(i==23) std::cout << "   ";
    }
    std::cout << '\n';
}

uint8_t get_high(uint16_t val){
    return uint8_t(val >> 8);
}

uint8_t get_low(uint16_t val){
    return uint8_t(val & 0xFF);
}

void print_bits8(uint8_t value) {
    for (int i = 7; i >= 0; --i) {
        std::cout << ((value >> i) & 1);
    }
    std::cout << std::endl;
}

static void timeout_callback(void* arg) {
    potential_danger = true;
    xSemaphoreGive(lmicSemaphore);
    ESP_LOGI("TIMER", "Object blocking for the last %d seconds. Sending Alert.", TIMEOUT_SECONDS);
    // Handle the timeout event here...
    esp_timer_stop(timeout_timer);
    esp_timer_start_once(timeout_timer, TIMEOUT_SECONDS * 1000000); //
}

void init_timeout_timer() {
    // Initialize the timer
    esp_timer_create_args_t timer_config = {
        .callback = &timeout_callback,
        .name = "Timeout Timer"
    };
    esp_timer_create(&timer_config, &timeout_timer);
    esp_timer_start_once(timeout_timer, TIMEOUT_SECONDS * 1000000); // Convert seconds to microseconds
}

void process_csi(ArrayXf full_csi_vector, float rssi) {
  features_to_send << 70,  71,  69,  72,  31,  35,  16, 102,  37,  39, 101,  36, 103,
        33,  20, 100;



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
      init_timeout_timer();
    } else {
      current_power = frames(Eigen::seq(MAX_FRAMES/2 - WINDOW_SIZE, MAX_FRAMES/2-1), Eigen::all).sum();
      current_power /= WINDOW_SIZE;

        printf("Current power: %f, Reference power: %f \n", current_power, reference_power);
      
      if (current_power > (1 + THRESHOLD_DETECTION) * reference_power && should_send == false){
        obj_in_sight = false;
        should_send = true;
        printf("\n OBJECT NOT IN SIGHT ANYMORE\n");
        xSemaphoreGive(lmicSemaphore);
      }
      
      if (current_power <= (1 + THRESHOLD_DETECTION) * reference_power){
        printf("\n DETECTED \n");
        obj_in_sight = true;
      } else {
        potential_danger = false;
        esp_timer_stop(timeout_timer);
        esp_timer_start_once(timeout_timer, TIMEOUT_SECONDS * 1000000);
      }
      
      if (should_send && obj_in_sight) {
          should_send = false;
          printf("\n SENDING CSI PACKAGE\n");
          subporters_frame_mean << (frames / (frames.mean())).transpose().rowwise().mean().array();
          subporters_frame_std_dev = (((frames / (frames.mean())).transpose().array().colwise() - subporters_frame_mean).square().rowwise().sum()/MAX_FRAMES).sqrt().array(); // standard deviation
          
          //Array<uint16_t, 1, N_NON_NULL_SUBPORTERS> subporters_frame_mean_half = subporters_frame_mean.unaryExpr(&float_to_half).transpose();
          //Array<uint8_t, 1, N_NON_NULL_SUBPORTERS> subporters_frame_mean_high = subporters_frame_mean_half.unaryExpr(&get_high);
          //Array<uint8_t, 1, N_NON_NULL_SUBPORTERS> subporters_frame_mean_low = subporters_frame_mean_half.unaryExpr(&get_low);
          
          //Array<uint16_t, 1, N_NON_NULL_SUBPORTERS> subporters_frame_std_dev_half = subporters_frame_std_dev.unaryExpr(&float_to_half).transpose();
          //Array<uint8_t, 1, N_NON_NULL_SUBPORTERS> subporters_frame_std_dev_high = subporters_frame_std_dev_half.unaryExpr(&get_high);
          //Array<uint8_t, 1, N_NON_NULL_SUBPORTERS> subporters_frame_std_dev_low = subporters_frame_std_dev_half.unaryExpr(&get_low);
          
          
          full_lora_payload << subporters_frame_mean, subporters_frame_std_dev;

          final_lora_payload << full_lora_payload(features_to_send);
          Array<uint16_t, 1, N_FEATURES> final_lora_payload_half = final_lora_payload.unaryExpr(&float_to_half).transpose();
          Array<uint8_t, 1, N_FEATURES> final_lora_payload_high = final_lora_payload_half.unaryExpr(&get_high);
          Array<uint8_t, 1, N_FEATURES> final_lora_payload_low = final_lora_payload_half.unaryExpr(&get_low);





          lora_payload << final_lora_payload_high, 
                          final_lora_payload_low;
        //                  subporters_frame_std_dev_high(Eigen::seq(0, 2)),
        //                  subporters_frame_std_dev_low(Eigen::seq(0, 2));


          xSemaphoreGive(lmicSemaphore);
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
