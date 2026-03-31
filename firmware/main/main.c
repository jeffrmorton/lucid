/* Lucid Firmware — ESP32-S3 + ADS1299 EEG acquisition */
#include "ads1299.h"
#include "streaming.h"
#include "esp_log.h"

static const char *TAG = "lucid";

void app_main(void) {
    ESP_LOGI(TAG, "Lucid BCI firmware v0.1.2");
    // TODO: Initialize ADS1299, start BLE/WiFi streaming
}
