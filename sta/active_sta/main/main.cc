#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_spi_flash.h"
#include "freertos/event_groups.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_http_client.h"
#include "esp_log.h"
#include "nvs_flash.h"

#include <lmic.h>

#include "lwip/err.h"
#include "lwip/sys.h"

#include "../../_components/nvs_component.h"
#include "../../_components/sd_component.h"
#include "../../_components/csi_component.h"
#include "../../_components/time_component.h"
#include "../../_components/input_component.h"
#include "../../_components/sockets_component.h"


/*
 * The examples use WiFi configuration that you can set via 'idf.py menuconfig'.
 *
 * If you'd rather not, just change the below entries to strings with
 * the config you want - ie #define ESP_WIFI_SSID "mywifissid"
 */
#define ESP_WIFI_SSID      CONFIG_ESP_WIFI_SSID
#define ESP_WIFI_PASS      CONFIG_ESP_WIFI_PASSWORD

#ifdef CONFIG_WIFI_CHANNEL
#define WIFI_CHANNEL CONFIG_WIFI_CHANNEL
#else
#define WIFI_CHANNEL 6
#endif

#ifdef CONFIG_SHOULD_COLLECT_CSI
#define SHOULD_COLLECT_CSI 1
#else
#define SHOULD_COLLECT_CSI 0
#endif

#ifdef CONFIG_SHOULD_COLLECT_ONLY_LLTF
#define SHOULD_COLLECT_ONLY_LLTF 1
#else
#define SHOULD_COLLECT_ONLY_LLTF 0
#endif

#ifdef CONFIG_SEND_CSI_TO_SERIAL
#define SEND_CSI_TO_SERIAL 1
#else
#define SEND_CSI_TO_SERIAL 0
#endif

#ifdef CONFIG_SEND_CSI_TO_SD
#define SEND_CSI_TO_SD 1
#else
#define SEND_CSI_TO_SD 0
#endif

/* FreeRTOS event group to signal when we are connected*/
static EventGroupHandle_t s_wifi_event_group;

/* The event group allows multiple bits for each event, but we only care about one event
 * - are we connected to the AP with an IP? */
const int WIFI_CONNECTED_BIT = BIT0;

static const char *TAG = "Active CSI collection (Station)";

esp_err_t _http_event_handle(esp_http_client_event_t *evt) {
    switch (evt->event_id) {
        case HTTP_EVENT_ON_DATA:
            ESP_LOGI(TAG, "HTTP_EVENT_ON_DATA, len=%d", evt->data_len);
            if (!esp_http_client_is_chunked_response(evt->client)) {
                if (!real_time_set) {
                    char *data = (char *) malloc(evt->data_len + 1);
                    strncpy(data, (char *) evt->data, evt->data_len);
                    data[evt->data_len + 1] = '\0';
                    time_set(data);
                    free(data);
                }
            }
            break;
        default:
            break;
    }
    return ESP_OK;
}

//// en_sys_seq: see https://github.com/espressif/esp-idf/blob/master/docs/api-guides/wifi.rst#wi-fi-80211-packet-send for details
esp_err_t esp_wifi_80211_tx(wifi_interface_t ifx, const void *buffer, int len, bool en_sys_seq);

static void event_handler(void* arg, esp_event_base_t event_base,
                          int32_t event_id, void* event_data) {
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        ESP_LOGI(TAG, "Retry connecting to the AP");
        esp_wifi_connect();
        xEventGroupClearBits(s_wifi_event_group, WIFI_CONNECTED_BIT);
    } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t* event = (ip_event_got_ip_t*) event_data;
        ESP_LOGI(TAG, "Got ip:" IPSTR, IP2STR(&event->ip_info.ip));
        xEventGroupSetBits(s_wifi_event_group, WIFI_CONNECTED_BIT);
    }
}

bool is_wifi_connected() {
    return (xEventGroupGetBits(s_wifi_event_group) & WIFI_CONNECTED_BIT);
}

void station_init() {
    s_wifi_event_group = xEventGroupCreate();

    ESP_ERROR_CHECK(esp_netif_init());

    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    esp_event_handler_instance_t instance_any_id;
    esp_event_handler_instance_t instance_got_ip;
    ESP_ERROR_CHECK(esp_event_handler_instance_register(WIFI_EVENT,
                                                        ESP_EVENT_ANY_ID,
                                                        &event_handler,
                                                        NULL,
                                                        &instance_any_id));
    ESP_ERROR_CHECK(esp_event_handler_instance_register(IP_EVENT,
                                                        IP_EVENT_STA_GOT_IP,
                                                        &event_handler,
                                                        NULL,
                                                        &instance_got_ip));

    wifi_sta_config_t wifi_sta_config = {};
    wifi_sta_config.channel = WIFI_CHANNEL;
    wifi_config_t wifi_config = {
            .sta = wifi_sta_config,
    };

    strlcpy((char *) wifi_config.sta.ssid, ESP_WIFI_SSID, sizeof(ESP_WIFI_SSID));
    strlcpy((char *) wifi_config.sta.password, ESP_WIFI_PASS, sizeof(ESP_WIFI_PASS));

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());

    esp_wifi_set_ps(WIFI_PS_NONE);

    ESP_LOGI(TAG, "connect to ap SSID:%s password:%s", ESP_WIFI_SSID, ESP_WIFI_PASS);
}

TaskHandle_t xHandle = NULL;

void vTask_socket_transmitter_sta_loop(void *pvParameters) {
    for (;;) {
        socket_transmitter_sta_loop(&is_wifi_connected);
    }
}

void config_print() {
    printf("\n\n\n\n\n\n\n\n");
    printf("-----------------------\n");
    printf("ESP32 CSI Tool Settings\n");
    printf("-----------------------\n");
    printf("PROJECT_NAME: %s\n", "ACTIVE_STA");
    printf("CONFIG_ESPTOOLPY_MONITOR_BAUD: %d\n", CONFIG_ESPTOOLPY_MONITOR_BAUD);
    printf("CONFIG_ESP_CONSOLE_UART_BAUDRATE: %d\n", CONFIG_ESP_CONSOLE_UART_BAUDRATE);
    printf("IDF_VER: %s\n", IDF_VER);
    printf("-----------------------\n");
    printf("WIFI_CHANNEL: %d\n", WIFI_CHANNEL);
    printf("ESP_WIFI_SSID: %s\n", ESP_WIFI_SSID);
    printf("ESP_WIFI_PASSWORD: %s\n", ESP_WIFI_PASS);
    printf("PACKET_RATE: %i\n", CONFIG_PACKET_RATE);
    printf("SHOULD_COLLECT_CSI: %d\n", SHOULD_COLLECT_CSI);
    printf("SHOULD_COLLECT_ONLY_LLTF: %d\n", SHOULD_COLLECT_ONLY_LLTF);
    printf("SEND_CSI_TO_SERIAL: %d\n", SEND_CSI_TO_SERIAL);
    printf("SEND_CSI_TO_SD: %d\n", SEND_CSI_TO_SD);
    printf("-----------------------\n");
    printf("\n\n\n\n\n\n\n\n");
}


static uint8_t obj_not_in_sight[] = "OBJECT NOT IN SIGHT";
static uint8_t danger[] = "POTENTIAL DANGER";


//static char power_data[11];
//static osjob_t sendjob;
const unsigned TX_INTERVAL = 1;
//extern "C" void do_send(osjob_t* j){
extern "C" void do_send(){
    vTaskDelay(1000 / portTICK_PERIOD_MS);

    // Check if there is not a current TX/RX job running
    if (LMIC.opmode & OP_TXRXPEND) {
        printf(("OP_TXRXPEND, not sending"));
    } else {
            if(xSemaphoreTake(lmicSemaphore, portMAX_DELAY) == pdTRUE){
                if (!obj_in_sight && !potential_danger){
                    LMIC_setTxData2(1, (uint8_t*) obj_not_in_sight, sizeof(obj_not_in_sight)-1, 0);
                }
                else if(obj_in_sight && !potential_danger){
                    LMIC_setTxData2(1, lora_payload.data(), sizeof(lora_payload), 0);
                }
                else{
                    LMIC_setTxData2(1, (uint8_t*) danger, sizeof(danger)-1, 0);
                }
        }
    }
    // Next TX is scheduled after TX_COMPLETE event.
}


extern "C" void onEvent (ev_t ev) {
    printf("%d", os_getTime());
    printf(": \n");
    switch(ev) {
        case ev_t::EV_SCAN_TIMEOUT:
            printf(("EV_SCAN_TIMEOUT\n"));
            break;
        case ev_t::EV_BEACON_FOUND:
            printf(("EV_BEACON_FOUND\n"));
            break;
        case ev_t::EV_BEACON_MISSED:
            printf(("EV_BEACON_MISSED\n"));
            break;
        case ev_t::EV_BEACON_TRACKED:
            printf(("EV_BEACON_TRACKED\n"));
            break;
        case ev_t::EV_JOINING:
            printf(("EV_JOINING\n"));
            break;
        case ev_t::EV_JOINED:
            printf(("EV_JOINED\n"));
            break;
        case ev_t::EV_JOIN_FAILED:
            printf(("EV_JOIN_FAILED\n"));
            break;
        case ev_t::EV_REJOIN_FAILED:
            printf(("EV_REJOIN_FAILED\n"));
            break;
        case ev_t::EV_TXCOMPLETE:
            printf(("EV_TXCOMPLETE (includes waiting for RX windows)\n\n"));
            if (LMIC.txrxFlags & TXRX_ACK)
              printf(("Received ack\n"));
            if (LMIC.dataLen) {
              printf(("Received "));
              printf("%d", LMIC.dataLen);
              printf((" bytes of payload\n"));
            }
            // Schedule next transmission
            //os_setTimedCallback(&sendjob, os_getTime()+sec2osticks(TX_INTERVAL), do_send);
            //do_send(&sendjob);
            do_send();
            break;
        case ev_t::EV_LOST_TSYNC:
            printf(("EV_LOST_TSYNC\n"));
            break;
        case ev_t::EV_RESET:
            printf(("EV_RESET\n"));
            break;
        case ev_t::EV_RXCOMPLETE:
            // data received in ping slot
            printf(("EV_RXCOMPLETE\n"));
            break;
        case ev_t::EV_LINK_DEAD:
            printf(("EV_LINK_DEAD\n"));
            break;
        case ev_t::EV_LINK_ALIVE:
            printf(("EV_LINK_ALIVE\n"));
            break;
        default:
            printf(("Unknown event: "));
            printf("%d\n", (unsigned) ev);
            break;
    }
}


extern "C" const lmic_pinmap lmic_pins = {
    .nss = 18,
    .rxtx = LMIC_UNUSED_PIN,
    .rst = 23,
    .dio = { 26, 33, 32 },
    .spi = { /* MISO = */ 19, /* MOSI = */ 27, /* SCK = */ 5 },
};

static const u1_t NWKSKEY[16] = { 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11  };
static const u1_t APPSKEY[16] = { 0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x22 };
static const u4_t DEVADDR = 0x33333333 ; // <-- Change this address for every node!

void os_getArtEui (u1_t* buf) { }
void os_getDevEui (u1_t* buf) { }
void os_getDevKey (u1_t* buf) { }

extern "C" void lora_task(void *p) {

    os_init();
    LMIC_reset();
    LMIC_setSession(0x13, DEVADDR, (xref2u1_t)&NWKSKEY, (xref2u1_t)&APPSKEY);
    //LMIC.freq = 903100000;
    //LMIC.dn2Freq = 903100000;
    LMIC.freq = 916000000;
    LMIC.dn2Freq = 916000000;
    LMIC.datarate = DR_SF7;
    LMIC.txpow = 20;
    LMIC.rps = updr2rps(LMIC.datarate);

    //LMIC_setDrTxpow(DR_SF7, 20);
    //LMIC_selectSubBand(4);
    LMIC_setLinkCheckMode(0);
    LMIC.dn2Dr = DR_SF7;
    //do_send(&sendjob);
    do_send();

    while(1) {
        os_runloop_once();
    }

}

extern "C" void app_main() {
    // init_timeout_timer();
    lmicSemaphore = xSemaphoreCreateBinary();
    config_print();
    nvs_init();
    sd_init();
    station_init();
    csi_init((char *) "STA");
#if !(SHOULD_COLLECT_CSI)
    printf("CSI will not be collected. Check `idf.py menuconfig  # > ESP32 CSI Tool Config` to enable CSI");
#endif


    xTaskCreatePinnedToCore(&vTask_socket_transmitter_sta_loop, "socket_transmitter_sta_loop",
                            10000, (void *) &is_wifi_connected, 100, &xHandle, 1);
    xTaskCreatePinnedToCore(&lora_task, "lora_task", 8192, NULL, 5, NULL, 0);
}